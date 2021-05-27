"""Define the interface of the repositories."""

import abc
from typing import Dict, List, Optional, Type, TypeVar, Union

from ..exceptions import AutoIncrementError, EntityNotFoundError
from ..model import Entity as EntityModel
from ..model import EntityID

# no cover: The lines with the flag are being tested by it's subclasses.

Entity = TypeVar("Entity", bound=EntityModel)
Models = List[Type[Entity]]
OptionalModels = Optional[Models[Entity]]
OptionalModelOrModels = Optional[Union[Type[Entity], Models[Entity]]]


class Repository(abc.ABC):
    """Gather common methods and define the interface of the repositories.

    Attributes:
        database_url: URL specifying the connection to the database.
    """

    @abc.abstractmethod
    def __init__(
        self, models: OptionalModels[Entity] = None, database_url: str = ""
    ) -> None:
        """Initialize the repository attributes.

        Args:
            database_url: URL specifying the connection to the database.
            models: List of stored entity models.
        """
        self.database_url = database_url
        if models is None:
            models = []
        self.models = models

    @abc.abstractmethod
    def add(self, entity: Entity) -> Entity:
        """Append an entity to the repository.

        If the id is not set, autoincrement the last.

        Args:
            entity: Entity to add to the repository.

        Returns:
            entity
        """
        # no cover: it's tested by it's subclasses
        if isinstance(entity.id_, int) and entity.id_ < 0:  # pragma: no cover
            entity.id_ = self._next_id(entity)  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, entity: Entity) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(
        self, id_: EntityID, models: OptionalModelOrModels[Entity] = None
    ) -> Entity:
        """Obtain an entity from the repository by it's ID.

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

    @abc.abstractmethod
    def all(self, models: OptionalModelOrModels[Entity] = None) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Args:
            models: Entity class or classes to obtain.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        """Persist the changes into the repository."""
        raise NotImplementedError

    @abc.abstractmethod
    def search(
        self,
        fields: Dict[str, EntityID],
        models: OptionalModelOrModels[Entity] = None,
    ) -> List[Entity]:
        """Get the entities whose attributes match one or several conditions.

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
        try:
            return max(self.all(models))
        except ValueError as error:
            # no cover: it's tested by it's subclasses
            models = self._build_models(models)  # pragma: nocover
            raise self._model_not_found(models) from error  # pragma: nocover

    def first(self, models: OptionalModelOrModels[Entity]) -> Entity:
        """Get the smallest entity from the repository.

        Args:
            models: Type of entity object to obtain.

        Returns:
            entity: Smallest Entity object of type models.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        try:
            return min(self.all(models))
        except ValueError as error:
            models = self._build_models(models)  # pragma: nocover
            raise self._model_not_found(models) from error  # pragma: nocover

    def _next_id(self, entity: Entity) -> int:
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
        self, models: Models[Entity], append_str: str = ""
    ) -> EntityNotFoundError:
        """Raise the appropriate EntityNotFoundError exception based on models.

        Args:
            models: Type of entity object to obtain.
            append_str: message to append after the message of no entities found.
                Must start with a space

        Raises:
            EntityNotFoundError
        """
        if models == self.models:
            return EntityNotFoundError(  # pragma: no cover
                f"There are no entities in the repository{append_str}."
            )
        if len(models) > 0:
            entity_str = ", ".join([model.__name__ for model in models])
            return EntityNotFoundError(  # pragma: no cover
                f"There are no entities of type {entity_str} "
                f"in the repository{append_str}."
            )
        return EntityNotFoundError(  # pragma: no cover
            f"There are no {models[0].__name__}s in the repository{append_str}."
        )

    def _build_models(self, models: OptionalModelOrModels[Entity]) -> Models[Entity]:
        """Create the Models from the OptionalModelOrModels."""
        if models is None:
            models = self.models
        elif not isinstance(models, list):
            models = [models]
        return models
