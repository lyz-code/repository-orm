"""Define the interface of the repositories."""

import abc
from typing import Dict, List, Type, TypeVar

from ..exceptions import AutoIncrementError, EntityNotFoundError
from ..model import Entity as EntityModel
from ..model import EntityID

Entity = TypeVar("Entity", bound=EntityModel)


class AbstractRepository(abc.ABC):
    """Gather common methods and define the interface of the repositories.

    Attributes:
        database_url: URL specifying the connection to the database.
    """

    @abc.abstractmethod
    def __init__(self, database_url: str = "") -> None:
        """Initialize the repository attributes.

        Args:
            database_url: URL specifying the connection to the database.
        """
        self.database_url = database_url

    @abc.abstractmethod
    def add(self, entity: Entity) -> None:
        """Append an entity to the repository.

        Args:
            entity: Entity to add to the repository.
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
    def get(self, entity_model: Type[Entity], entity_id: EntityID) -> Entity:
        """Obtain an entity from the repository by it's ID.

        Args:
            entity_model: Type of entity object to obtain.
            entity_id: ID of the entity object to obtain.

        Returns:
            entity: Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def all(self, entity_model: Type[Entity]) -> List[Entity]:
        """Obtain all the entities of a type from the repository.

        Args:
            entity_model: Type of entity objects to obtain.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        """Persist the changes into the repository."""
        raise NotImplementedError

    @abc.abstractmethod
    def search(
        self, entity_model: Type[Entity], fields: Dict[str, EntityID]
    ) -> List[Entity]:
        """Obtain the entities whose attributes match one or several conditions.

        Args:
            entity_model: Type of entity object to obtain.
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

    @abc.abstractmethod
    def last(self, entity_model: Type[Entity], index: bool = True) -> Entity:
        """Get the biggest entity from the repository.

        Args:
            entity_model: Type of entity object to obtain.
            index: Check only commited entities.

        Returns:
            entity: Biggest Entity object of type entity_model.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        try:
            return max(self.all(entity_model))
        except KeyError as error:
            # no cover: it's tested by it's subclasses
            raise EntityNotFoundError(  # pragma: no cover
                f"There are no {entity_model.__name__}s in the repository."
            ) from error

    def first(self, entity_model: Type[Entity]) -> Entity:
        """Get the smallest entity from the repository.

        Args:
            entity_model: Type of entity object to obtain.

        Returns:
            entity: Smallest Entity object of type entity_model.

        Raises:
            EntityNotFoundError: If there are no entities.
        """
        try:
            return min(self.all(entity_model))
        except KeyError as error:
            # no cover: it's tested by it's subclasses
            raise EntityNotFoundError(  # pragma: no cover
                f"There are no {entity_model.__name__}s in the repository."
            ) from error

    def _next_id(self, entity: Entity) -> int:
        """Return one id unit more than the last entity id in the repository index.

        Args:
            entity: Entity whose model we want to get the next entity id.
        """
        try:
            last_id = self.last(type(entity), index=False).id_
        except EntityNotFoundError:
            return 0
        if isinstance(last_id, int):
            return last_id + 1
        raise AutoIncrementError(
            "Auto increment is not yet supported for Entities with string id_s. "
            "Please set the id_ yourself before adding the entities to the "
            "repository."
        )
