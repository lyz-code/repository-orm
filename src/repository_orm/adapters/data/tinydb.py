"""Define the TinyDB Repository."""

import logging
import os
import re
from contextlib import suppress
from typing import Any, Dict, Iterable, List, Optional, Type

from pydantic import ValidationError
from tinydb import Query, TinyDB
from tinydb.queries import QueryInstance
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from ...exceptions import EntityNotFoundError
from ...model import EntityID
from .abstract import Entity, Repository, warn_on_models

log = logging.getLogger(__name__)


class TinyDBRepository(Repository):
    """Implement the repository pattern using the TinyDB."""

    def __init__(
        self,
        database_url: str = "",
        search_exception: Optional[bool] = None,
    ) -> None:
        """Initialize the repository attributes.

        Args:
            database_url: URL specifying the connection to the database.
        """
        super().__init__(database_url, search_exception)
        self.database_file = os.path.expanduser(database_url.replace("tinydb://", ""))
        if not os.path.isfile(self.database_file):
            try:
                with open(self.database_file, "a", encoding="utf-8") as file_cursor:
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

    def _add(self, entity: Entity) -> Entity:
        """Append an entity to the repository.

        If the id is not set, autoincrement the last.

        Args:
            entity: Entity to add to the repository.

        Returns:
            entity
        """
        self.staged["add"].append(entity)

        return entity

    def delete(self, entity: Entity) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.
        """
        try:
            self.get(entity.id_, type(entity))
        except EntityNotFoundError as error:
            raise EntityNotFoundError(
                f"Unable to delete entity {entity} because it's not in the repository"
            ) from error
        self.staged["remove"].append(entity)

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
        model_query = Query().model_type_ == model.__name__.lower()

        matching_entities_data = self.db_.search(
            (Query()[attribute] == value) & (model_query)
        )

        return [
            self._build_entity(entity_data, model)
            for entity_data in matching_entities_data
        ]

    @staticmethod
    def _build_entity(
        entity_data: Dict[Any, Any],
        model: Type[Entity],
    ) -> Entity:
        """Create an entity from the data stored in a row of the database.

        Args:
            entity_data: Dictionary with the attributes of the entity.
            model: Type of entity object to obtain.

        Returns:
            entity: Built Entity.
        """
        # If we don't copy the data, the all method stop being idempotent.
        entity_data = entity_data.copy()
        try:
            return model.parse_obj(entity_data)
        except ValidationError as error:
            log.error(
                f"Error loading the model {model.__name__} "
                f"for the register {str(entity_data)}"
            )
            raise error

    def _all(self, model: Type[Entity]) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Particular implementation of the database adapter.

        Args:
            models: Entity class to obtain.
        """
        entities: List[Entity] = []

        query = Query().model_type_ == model.__name__.lower()
        entities_data = self.db_.search(query)

        for entity_data in entities_data:
            entities.append(self._build_entity(entity_data, model))

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
        entity_data["model_type_"] = entity.model_name.lower()

        return entity_data

    def commit(self) -> None:
        """Persist the changes into the repository."""
        for entity in self.staged["add"]:
            self.db_.upsert(
                self._export_entity(entity),
                (Query().model_type_ == entity.model_name.lower())
                & (Query().id_ == entity.id_),
            )
        self.staged["add"].clear()

        for entity in self.staged["remove"]:
            self.db_.remove(
                (Query().model_type_ == entity.model_name.lower())
                & (Query().id_ == entity.id_)
            )
        self.staged["remove"].clear()

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
        entities: List[Entity] = []
        try:
            query = self._build_search_query(fields, model)
        except EntityNotFoundError:
            return []

        # Build entities
        entities_data = self.db_.search(query)

        for entity_data in entities_data:
            entities.append(self._build_entity(entity_data, model))

        return entities

    def _build_search_query(
        self,
        fields: Dict[str, EntityID],
        model: Type[Entity],
    ) -> QueryInstance:
        """Build the Query parts for a repository search.

        If the field type is a list, change the query accordingly.

        Args:
            model: Type of entity object to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            Query based on the type of model and fields.
        """
        query_parts = []

        schema = model.schema()["properties"]
        for field, value in fields.items():
            if field not in schema.keys():
                continue

            with suppress(KeyError):
                if schema[field]["type"] == "array":
                    query_parts.append(
                        (Query().model_type_ == model.__name__.lower())
                        & (Query()[field].test(_regexp_in_list, value))
                    )
                    continue

            if isinstance(value, str):
                query_parts.append(
                    (Query().model_type_ == model.__name__.lower())
                    & (Query()[field].search(value, flags=re.IGNORECASE))
                )
            else:
                query_parts.append(
                    (Query().model_type_ == model.__name__.lower())
                    & (Query()[field] == value)
                )
        if len(query_parts) != 0:
            return self._merge_query(query_parts, mode="and")

        raise EntityNotFoundError(
            f"There are no entities of type {model.__name__} in the repository "
            f" that match the search filter {fields}"
        )

    @staticmethod
    def _merge_query(
        query_parts: List[QueryInstance], mode: str = "and"
    ) -> QueryInstance:
        """Join all the query parts into a query.

        Args:
            query_parts: List of queries to concatenate.
            mode: "and" or "or" for the join method.

        Returns:
            A query object that joins all parts.
        """
        query = query_parts[0]

        for query_part in query_parts[1:]:
            if mode == "and":
                query = query & query_part
            else:
                query = query | query_part

        return query

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
            last_index_entity: Entity = super().last(model)
        except EntityNotFoundError as empty_repo:
            try:
                # Empty repo but entities staged to be commited.
                return max(
                    entity for entity in self.staged["add"] if entity.__class__ == model
                )
            except ValueError as no_staged_entities:
                # Empty repo and no entities staged.
                raise empty_repo from no_staged_entities

        try:
            last_staged_entity = max(
                entity for entity in self.staged["add"] if entity.__class__ == model
            )
        except ValueError:
            # Full repo and no staged entities.
            return last_index_entity

        # Full repo and staged entities.
        return max([last_index_entity, last_staged_entity])

    def close(self) -> None:
        """Close the connection to the database."""
        self.db_.close()

    @property
    def is_closed(self) -> bool:
        """Inform if the connection is closed."""
        try:
            self.db_.tables()
            return False
        except ValueError:
            return True

    def empty(self) -> None:
        """Remove all entities from the repository."""
        self.db_.truncate()


def _regexp_in_list(list_: Iterable[Any], regular_expression: str) -> bool:
    """Test if regexp matches any element of the list."""
    regexp = re.compile(regular_expression)

    return any(regexp.search(element) for element in list_)
