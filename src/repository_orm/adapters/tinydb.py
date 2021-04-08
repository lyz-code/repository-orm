"""Define the TinyDB Repository."""

import logging
import os
from typing import Any, Dict, List, Type, TypeVar, Union

from tinydb import Query, TinyDB
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from ..exceptions import EntityNotFoundError
from ..model import Entity as EntityModel
from .abstract import AbstractRepository

log = logging.getLogger(__name__)

Entity = TypeVar("Entity", bound=EntityModel)


class TinyDBRepository(AbstractRepository):
    """Implement the repository pattern using the TinyDB."""

    def __init__(self, database_url: str) -> None:
        """Initialize the repository attributes.

        Attributes:
            database_url: URL specifying the connection to the database.
        """
        super().__init__(database_url)
        self.database_file = database_url.replace("tinydb:///", "")
        if not os.path.isfile(self.database_file):
            try:
                with open(self.database_file, "a") as file_cursor:
                    file_cursor.close()
            except FileNotFoundError as error:
                raise ConnectionError(
                    f"Could not create the database file: {self.database_file}"
                ) from error

        serialization = SerializationMiddleware(JSONStorage)
        serialization.register_serializer(DateTimeSerializer(), "TinyDate")

        self.db_ = TinyDB(
            self.database_file, storage=serialization, sort_keys=True, indent=4
        )
        self.staged: Dict[str, List[Any]] = {"add": [], "remove": []}

    def add(self, entity: Entity) -> None:
        """Append an entity to the repository.

        Args:
            entity: Entity to add to the repository.
        """
        self.staged["add"].append(entity)

    def delete(self, entity: Entity) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.
        """
        try:
            self.get(type(entity), entity.id_)
        except EntityNotFoundError as error:
            raise EntityNotFoundError(
                f"Unable to delete entity {entity} because it's not in the repository"
            ) from error
        self.staged["remove"].append(entity)

    def get(self, entity_model: Type[Entity], entity_id: Union[str, int]) -> Entity:
        """Obtain an entity from the repository by it's ID.

        Args:
            entity_model: Type of entity object to obtain.
            entity_id: ID of the entity object to obtain.

        Returns:
            entity: Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        try:
            entity_data = self.db_.search(
                (Query().id_ == entity_id)
                & (Query().model_type_ == entity_model.__name__.lower())
            )[0]
        except IndexError as error:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s with id {entity_id} in the"
                " repository."
            ) from error

        return self._build_entity(entity_data, entity_model)

    @staticmethod
    def _build_entity(
        entity_data: Dict[Any, Any], entity_model: Type[Entity]
    ) -> Entity:
        """Create an entity from the data stored in a row of the database.

        Args:
            entity_data: Dictionary with the attributes of the entity.
            entity_model: Type of entity object to obtain.

        Returns:
            entity: Built Entity.
        """
        entity_data.pop("model_type_")

        return entity_model.parse_obj(entity_data)

    def all(self, entity_model: Type[Entity]) -> List[Entity]:
        """Obtain all the entities of a type from the repository.

        Args:
            entity_model: Type of entity objects to obtain.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        entities = []
        entities_data = self.db_.search(
            Query().model_type_ == entity_model.__name__.lower()
        )

        for entity_data in entities_data:
            entities.append(self._build_entity(entity_data, entity_model))

        if len(entities) == 0:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s entities in the repository"
            )
        return entities

    @staticmethod
    def _export_entity(entity: Entity) -> Dict[Any, Any]:
        """Export the attributes of the entity appending the required by TinyDB.

        Args:
            entity: Entity to export.

        Returns:
            entity_data: Dictionary with the attributes of the entity.
        """
        entity_data = entity.dict()
        entity_data["model_type_"] = entity.__class__.__name__.lower()

        return entity_data

    def commit(self) -> None:
        """Persist the changes into the repository."""
        for entity in self.staged["add"]:
            self.db_.upsert(
                self._export_entity(entity),
                Query().model_type_ == entity.__class__.__name__.lower(),
            )
        self.staged["add"].clear()

        for entity in self.staged["remove"]:
            self.db_.remove(
                (Query().model_type_ == entity.__class__.__name__.lower())
                & (Query().id_ == entity.id_)
            )
        self.staged["remove"].clear()

    def search(
        self, entity_model: Type[Entity], fields: Dict[str, Union[str, int]]
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
        entities = []

        query = Query().model_type_ == entity_model.__name__.lower()
        for key, value in fields.items():
            if isinstance(value, str):
                query = query & (Query()[key].search(value))
            else:
                query = query & (Query()[key] == value)
        entities_data = self.db_.search(query)

        for entity_data in entities_data:
            entities.append(self._build_entity(entity_data, entity_model))

        if len(entities) == 0:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s that match the search filter"
                f" {fields}"
            )

        return entities

    def apply_migrations(self, migrations_directory: str) -> None:
        """Run the migrations of the repository schema.

        Args:
            migrations_directory: path to the directory containing the migration
                scripts.
        """
        raise NotImplementedError
