"""Define the interface of the repositories."""

import abc
import logging
import warnings
from contextlib import suppress
from typing import Dict, List, Optional, Sequence, Type, TypeVar, Union

from repository_orm.exceptions import TooManyEntitiesError

from ...exceptions import AutoIncrementError, EntityNotFoundError
from ...model import Entity as EntityModel
from ...model import EntityID
from .cache import Cache

Entity = TypeVar("Entity", bound=EntityModel)
EntityOrEntities = TypeVar("EntityOrEntities", Sequence[EntityModel], EntityModel)

Models = List[Type[Entity]]
OptionalModels = Optional[Models[Entity]]
OptionalModelOrModels = Optional[Union[Type[Entity], Models[Entity]]]

log = logging.getLogger(__name__)


class Repository(abc.ABC):
    """Gather common methods and define the interface of the repositories.

    Attributes:
        database_url: URL specifying the connection to the database.
    """

    @abc.abstractmethod
    def __init__(
        self,
        database_url: str = "",
        search_exception: Optional[bool] = None,
    ) -> None:
        """Initialize the repository attributes.

        Args:
            database_url: URL specifying the connection to the database.
            search_exception: Raise an exception when search doesn't return any value.
                It's a migration flag used to test the behaviour from 2022-06-10
                onwards.
        """
        if search_exception is not None:
            warnings.warn(
                "In 2022-12-10 initializing the repository with the argument "
                "search_exception is going to be deprecated as it was a flag to test "
                "a new behaviour that is now implemented, please remove argument.",
                UserWarning,
            )
        self.database_url = database_url
        self.search_exception = search_exception
        self.cache = Cache()

    def add(self, entities: EntityOrEntities, merge: bool = False) -> EntityOrEntities:
        """Append an entity or list of entities to the repository.

        If the id is not set, it will automatically increment the last available one.

        If `merge` is True, added entities will be merged with the existent ones in
        the cache.

        Args:
            entity: Entity to add to the repository.

        Returns:
            entity
        """
        if isinstance(entities, EntityModel):
            entity = entities

            if isinstance(entity.id_, int) and entity.id_ < 0:
                entity.id_ = self.next_id(entity)

            if merge:
                with suppress(EntityNotFoundError):
                    stored_entity = self.get(entity.id_, type(entity))
                    entity = stored_entity.merge(entity)

            if self.cache.entity_has_not_changed(entity):
                log.debug(
                    f"Skipping the addition of entity {entity} as it hasn't changed"
                )
                return entity
            entity = self._add(entity)
            self.cache.add(entity)
            return entity

        if isinstance(entities, list):
            updated_entities: List[EntityModel] = []
            for entity in entities:
                updated_entities.append(self.add(entity, merge))
            return updated_entities

        raise ValueError("Please add an entity or a list of entities")

    @abc.abstractmethod
    def _add(self, entity: Entity) -> Entity:
        """Append an entity to the repository.

        This method is specific to each database adapter.

        Args:
            entity: Entity to add to the repository.

        Returns:
            entity
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, entity: Entity) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.
        """
        raise NotImplementedError

    def get(
        self,
        id_: EntityID,
        model: Optional[Type[Entity]] = None,
        attribute: str = "id_",
        models: Optional[Type[Entity]] = None,
    ) -> Entity:
        """Obtain an entity from the repository by it's ID.

        Also save the entity in the cache

        Args:
            models: Entity class or classes to obtain.
            id_: ID of the entity to obtain.

        Returns:
            entity: Entity object that matches the id_

        Raises:
            EntityNotFoundError: If the entity is not found.
            TooManyEntitiesError: If more than one entity was found.
        """
        model = warn_on_models(models, "get", model)

        entities = self._get(value=id_, model=model, attribute=attribute)

        if len(entities) > 1:
            raise TooManyEntitiesError(
                f"More than one entity was found with the {attribute} {id_}"
            )
        if len(entities) == 0:
            raise EntityNotFoundError(
                f"There are no entities of type {model.__name__} in the repository "
                f"with {attribute} {id_}."
            )

        entity = entities[0]
        entity.clear_defined_values()
        self.cache.add(entity)
        return entity

    @abc.abstractmethod
    def _get(
        self,
        value: EntityID,
        model: Type[Entity],
        attribute: str = "id_",
    ) -> List[Entity]:
        """Obtain all entities from the repository that match an id_.

        If the attribute argument is passed, check that attribute instead.

        Args:
            value: Value of the entity attribute to obtain.
            model: Entity class to obtain.
            attribute: Entity attribute to check.

        Returns:
            entities: All entities that match the criteria.
        """
        raise NotImplementedError

    def all(
        self,
        model: Optional[Type[Entity]] = None,
        models: Optional[Type[Entity]] = None,
    ) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Also store the entities in the cache.

        Args:
            model: Entity class or classes to obtain.
        """
        model = warn_on_models(models, "all", model)

        entities = sorted(self._all(model))

        for entity in entities:
            entity.clear_defined_values()
            self.cache.add(entity)

        return entities

    @abc.abstractmethod
    def _all(self, model: Type[Entity]) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Particular implementation of the database adapter.

        Args:
            models: Entity class to obtain.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        """Persist the changes into the repository."""
        raise NotImplementedError

    def search(
        self,
        fields: Dict[str, EntityID],
        model: Optional[Type[Entity]] = None,
        models: Optional[Type[Entity]] = None,
    ) -> List[Entity]:
        """Get the entities whose attributes match one or several conditions.

        Also add the found entities to the cache.

        Args:
            model: Entity class to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.
        """
        model = warn_on_models(models, "search", model)
        found_entities = sorted(self._search(fields, model))

        for entity in found_entities:
            entity.clear_defined_values()
            self.cache.add(entity)

        return found_entities

    @abc.abstractmethod
    def _search(
        self,
        fields: Dict[str, EntityID],
        model: Type[Entity],
    ) -> List[Entity]:
        """Get the entities whose attributes match one or several conditions.

        Particular implementation of the database adapter.

        Args:
            model: Entity class to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def apply_migrations(self, migrations_directory: str) -> None:
        """Run the migrations of the repository schema.

        Args:
            migrations_directory: path to the directory containing the migration
                scripts.
        """
        raise NotImplementedError

    def last(
        self,
        model: Optional[Type[Entity]] = None,
        models: Optional[Type[Entity]] = None,
    ) -> Entity:
        """Get the biggest entity from the repository.

        Args:
            model: Entity class to obtain.

        Returns:
            entity: Biggest Entity object of type models.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        model = warn_on_models(models, "last", model)
        try:
            return max(self.all(model))
        except ValueError as error:
            raise EntityNotFoundError(
                f"There are no entities of type {model.__name__} in the repository."
            ) from error

    def first(
        self,
        model: Optional[Type[Entity]] = None,
        models: Optional[Type[Entity]] = None,
    ) -> Entity:
        """Get the smallest entity from the repository.

        Args:
            model: Type of entity object to obtain.

        Returns:
            entity: Smallest Entity object of type models.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        model = warn_on_models(models, "first", model)
        try:
            return min(self.all(model))
        except ValueError as error:
            raise EntityNotFoundError(
                f"There are no entities of type {model.__name__} in the repository."
            ) from error

    def next_id(self, entity: Entity) -> int:
        """Return one id unit more than the last entity id in the repository index.

        Args:
            entity: Entity whose model we want to get the next entity id.
        """
        try:
            last_id = self.last(type(entity)).id_
        except EntityNotFoundError:
            return 0
        if isinstance(last_id, int):
            return last_id + 1
        raise AutoIncrementError(
            "Auto increment is not yet supported for Entities with string id_s. "
            "Please set the id_ yourself before adding the entities to the "
            "repository."
        )

    @abc.abstractmethod
    def close(self) -> None:
        """Close the connection to the database."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_closed(self) -> bool:
        """Inform if the connection is closed."""
        raise NotImplementedError

    @abc.abstractmethod
    def empty(self) -> None:
        """Remove all entities from the repository."""
        raise NotImplementedError


# no cover: it's a transition function to deprecate stuff
def warn_on_models(
    models: Optional[Type[Entity]], method: str, model: Optional[Type[Entity]]
) -> Type[Entity]:
    """Warn users that using the models argument is going to be deprecated."""
    if models is not None:  # pragma: no cover
        warnings.warn(
            f"In 2022-12-10 using repo.{method} with the argument `models` is going to "
            "be deprecated, please use the argument `model`.",
            UserWarning,
        )
        return models
    if model is None:
        raise ValueError(  # pragma: no cover
            f"the `model` argument of the method repo.{method} can't be None"
        )

    return model
