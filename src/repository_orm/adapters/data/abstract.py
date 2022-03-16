"""Define the interface of the repositories."""

import abc
import logging
import warnings
from contextlib import suppress
from typing import Dict, List, Optional, Type, TypeVar, Union

from ...exceptions import AutoIncrementError, EntityNotFoundError
from ...model import Entity as EntityModel
from ...model import EntityID
from .cache import Cache

Entity = TypeVar("Entity", bound=EntityModel)
EntityOrEntities = TypeVar("EntityOrEntities", List[EntityModel], EntityModel)
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
        models: OptionalModels[Entity] = None,
        database_url: str = "",
        search_exception: bool = True,
    ) -> None:
        """Initialize the repository attributes.

        Args:
            database_url: URL specifying the connection to the database.
            models: List of stored entity models.
            search_exception: Raise an exception when search doesn't return any value.
                It's a migration flag used to test the behaviour from 2022-06-10
                onwards.
        """
        self.database_url = database_url
        self.search_exception = search_exception
        if models is None:
            models = []
        else:
            warnings.warn(
                "In 2022-06-10 initializing the repository with any model is going "
                "to be deprecated, please remove the models argument.",
                UserWarning,
            )
        self.models = models
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
        self, id_: EntityID, models: OptionalModelOrModels[Entity] = None
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
        warn_on_models(models, "get")

        entity = self._get(id_, models).clear_defined_values()
        self.cache.add(entity)
        return entity

    @abc.abstractmethod
    def _get(
        self, id_: EntityID, models: OptionalModelOrModels[Entity] = None
    ) -> Entity:
        """Obtain an entity from the repository by it's ID.

        Particular implementation of the adapter.

        Args:
            models: Entity class or classes to obtain.
            id_: ID of the entity to obtain.

        Returns:
            entity: Entity object that matches the id_

        Raises:
            EntityNotFoundError: If the entity is not found.
            TooManyEntitiesError: If more than one entity was found.
        """
        raise NotImplementedError

    def all(self, models: OptionalModelOrModels[Entity] = None) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Also store the entities in the cache.

        Args:
            models: Entity class or classes to obtain.
        """
        warn_on_models(models, "all")

        entities = sorted(self._all(models))

        # ignore: the type cannot be List[Entity] but it can, I don't know how to fix
        # this
        self.cache.add(entities)  # type: ignore

        return entities

    @abc.abstractmethod
    def _all(self, models: OptionalModelOrModels[Entity] = None) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Particular implementation of the database adapter.

        Args:
            models: Entity class or classes to obtain.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        """Persist the changes into the repository."""
        raise NotImplementedError

    def search(
        self,
        fields: Dict[str, EntityID],
        models: OptionalModelOrModels[Entity] = None,
    ) -> List[Entity]:
        """Get the entities whose attributes match one or several conditions.

        Also add the found entities to the cache.

        Args:
            models: Entity class or classes to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        warn_on_models(models, "search")
        try:
            found_entities = sorted(self._search(fields, models))
        except EntityNotFoundError as error:
            if self.search_exception:
                warnings.warn(
                    "From 2022-06-10 when repo.search doesn't find any result it will "
                    "return an empty list instead of raising an EntityNotFoundError "
                    "exception. To use this behaviour initialize your repository with "
                    "search_exception=False.",
                    UserWarning,
                )
                raise error
            found_entities = []

        # ignore: the type cannot be List[Entity] but it can, I don't know how to fix
        # this
        self.cache.add(found_entities)  # type: ignore

        return found_entities

    @abc.abstractmethod
    def _search(
        self,
        fields: Dict[str, EntityID],
        models: OptionalModelOrModels[Entity] = None,
    ) -> List[Entity]:
        """Get the entities whose attributes match one or several conditions.

        Particular implementation of the database adapter.

        Args:
            models: Entity class or classes to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
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

    def last(self, models: OptionalModelOrModels[Entity] = None) -> Entity:
        """Get the biggest entity from the repository.

        Args:
            models: Entity class or classes to obtain.

        Returns:
            entity: Biggest Entity object of type models.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        warn_on_models(models, "last")
        try:
            return max(self.all(models))
        except ValueError as error:
            models = self._build_models(models)
            raise self._model_not_found(models) from error

    def first(self, models: OptionalModelOrModels[Entity]) -> Entity:
        """Get the smallest entity from the repository.

        Args:
            models: Type of entity object to obtain.

        Returns:
            entity: Smallest Entity object of type models.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        warn_on_models(models, "first")
        try:
            return min(self.all(models))
        except ValueError as error:
            models = self._build_models(models)  # pragma: nocover
            raise self._model_not_found(models) from error  # pragma: nocover

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

    def _model_not_found(
        self, models: OptionalModelOrModels[Entity], append_str: str = ""
    ) -> EntityNotFoundError:
        """Raise the appropriate EntityNotFoundError exception based on models.

        Args:
            models: Type of entity object to obtain.
            append_str: message to append after the message of no entities found.
                Must start with a space

        Raises:
            EntityNotFoundError
        """
        models = self._build_models(models)
        entity_str = ", ".join([model.__name__ for model in models])
        return EntityNotFoundError(
            f"There are no entities of type {entity_str} "
            f"in the repository{append_str}."
        )

    def _build_models(self, models: OptionalModelOrModels[Entity]) -> Models[Entity]:
        """Create the Models from the OptionalModelOrModels."""
        if models is None:
            models = self.models
        elif not isinstance(models, list):
            models = [models]
        return models

    @abc.abstractmethod
    def close(self) -> None:
        """Close the connection to the database."""
        raise NotImplementedError


def warn_on_models(models: OptionalModelOrModels[Entity], method: str) -> None:
    """Warn users that using more than one model is going to be deprecated."""
    if isinstance(models, list):
        warnings.warn(
            f"In 2022-06-10 using repo.{method} with a list of models is going to be "
            "deprecated, please use just one model instead",
            UserWarning,
        )
    elif models is None:
        warnings.warn(
            f"In 2022-06-10 using repo.{method} without any model is going to be "
            "deprecated, please set the model you want to use.",
            UserWarning,
        )
