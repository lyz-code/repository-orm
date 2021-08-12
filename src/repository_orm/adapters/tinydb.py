"""Define the TinyDB Repository."""

import logging
import os
import re
from contextlib import suppress
from typing import Any, Dict, Iterable, List

from pydantic import ValidationError
from tinydb import Query, TinyDB
from tinydb.queries import QueryInstance
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from repository_orm.exceptions import TooManyEntitiesError

from ..exceptions import EntityNotFoundError
from ..model import EntityID
from .abstract import Entity, Models, OptionalModelOrModels, OptionalModels, Repository

log = logging.getLogger(__name__)


class TinyDBRepository(Repository):
    """Implement the repository pattern using the TinyDB."""

    def __init__(
        self, models: OptionalModels[Entity] = None, database_url: str = ""
    ) -> None:
        """Initialize the repository attributes.

        Args:
            database_url: URL specifying the connection to the database.
            models: List of stored entity models.
        """
        super().__init__(models, database_url)
        self.database_file = os.path.expanduser(database_url.replace("tinydb://", ""))
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

    def add(self, entity: Entity) -> Entity:
        """Append an entity to the repository.

        If the id is not set, autoincrement the last.

        Args:
            entity: Entity to add to the repository.

        Returns:
            entity
        """
        if isinstance(entity.id_, int) and entity.id_ < 0:
            entity.id_ = self._next_id(entity)
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
        models = self._build_models(models)
        model_query = self._build_model_query(models)

        matching_entities_data = self.db_.search((Query().id_ == id_) & (model_query))

        if len(matching_entities_data) == 1:
            return self._build_entity(matching_entities_data[0], models)
        elif len(matching_entities_data) == 0:
            raise self._model_not_found(models, f" with id {id_}")
        else:
            raise TooManyEntitiesError(
                f"More than one entity was found with the id {id_}"
            )

    def _build_entity(
        self,
        entity_data: Dict[Any, Any],
        models: OptionalModelOrModels[Entity] = None,
    ) -> Entity:
        """Create an entity from the data stored in a row of the database.

        Args:
            entity_data: Dictionary with the attributes of the entity.
            models: Type of entity object to obtain.

        Returns:
            entity: Built Entity.
        """
        # If we don't copy the data, the all method stop being idempotent.
        entity_data = entity_data.copy()
        model_name = entity_data.pop("model_type_")
        models = self._build_models(models)

        for model in models:
            if model.schema()["title"].lower() == model_name:
                model = model
                break
        try:
            return model.parse_obj(entity_data)
        except ValidationError as error:
            log.error(
                f"Error loading the model {model_name.capitalize()} "
                f"for the register {str(entity_data)}"
            )
            raise error

    def all(self, models: OptionalModelOrModels[Entity] = None) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Args:
            models: Entity class or classes to obtain.
        """
        entities: List[Entity] = []
        models = self._build_models(models)

        if models == self.models:
            entities_data = self.db_.all()
        else:
            query = self._build_model_query(models)
            entities_data = self.db_.search(query)

        for entity_data in entities_data:
            entities.append(self._build_entity(entity_data, models))

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
        entity_data["model_type_"] = entity._model_name.lower()

        return entity_data

    def commit(self) -> None:
        """Persist the changes into the repository."""
        for entity in self.staged["add"]:
            self.db_.upsert(
                self._export_entity(entity),
                (Query().model_type_ == entity._model_name.lower())
                & (Query().id_ == entity.id_),
            )
        self.staged["add"].clear()

        for entity in self.staged["remove"]:
            self.db_.remove(
                (Query().model_type_ == entity._model_name.lower())
                & (Query().id_ == entity.id_)
            )
        self.staged["remove"].clear()

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
        entities: List[Entity] = []
        models = self._build_models(models)
        query = self._build_search_query(fields, models)

        # Build entities
        entities_data = self.db_.search(query)

        for entity_data in entities_data:
            entities.append(self._build_entity(entity_data, models))

        if len(entities) == 0:
            raise self._model_not_found(
                models, f" that match the search filter {fields}"
            )

        return entities

    def _build_search_query(
        self,
        fields: Dict[str, EntityID],
        models: Models[Entity],
    ) -> QueryInstance:
        """Build the Query parts for a repository search.

        Select only the models that contain the fields. If the field type is a list,
        change the query accordingly.

        Args:
            models: Type of entity object to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            Query based on the type of models and fields.
        """
        query_parts = []

        for model in models:
            model_query_parts = []
            schema = model.schema()["properties"]
            for field, value in fields.items():
                if field not in schema.keys():
                    continue

                with suppress(KeyError):
                    if schema[field]["type"] == "array":
                        model_query_parts.append(
                            (Query().model_type_ == model.__name__.lower())
                            & (Query()[field].test(_regexp_in_list, value))
                        )
                        continue

                if isinstance(value, str):
                    model_query_parts.append(
                        (Query().model_type_ == model.__name__.lower())
                        & (Query()[field].search(value))
                    )
                else:
                    model_query_parts.append(Query()[field] == value)
            if len(model_query_parts) != 0:
                query_parts.append(self._merge_query(model_query_parts, mode="and"))
        if len(query_parts) == 0:
            raise self._model_not_found(
                models, f" that match the search filter {fields}"
            )

        return self._merge_query(query_parts, mode="or")

    def _build_model_query(
        self,
        models: Models[Entity],
    ) -> QueryInstance:
        """Build the Query parts from the models.

        Args:
            models: Type of entity object to obtain.

        Returns:
            List of query parts based on the type of models
        """
        query_parts = []

        for model in models:
            query_parts.append(Query().model_type_ == model.__name__.lower())

        return self._merge_query(query_parts, mode="or")

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
            last_index_entity: Entity = super().last(models)
        except EntityNotFoundError as empty_repo:
            try:
                # Empty repo but entities staged to be commited.
                return max(self.staged["add"])
            except ValueError as no_staged_entities:
                # Empty repo and no entities staged.
                raise empty_repo from no_staged_entities

        try:
            last_staged_entity = max(self.staged["add"])
        except ValueError:
            # Full repo and no staged entities.
            return last_index_entity

        # Full repo and staged entities.
        return max([last_index_entity, last_staged_entity])


def _regexp_in_list(list_: Iterable[Any], regular_expression: str) -> bool:
    """Test if regexp matches any element of the list."""
    regexp = re.compile(regular_expression)

    try:
        return any(regexp.search(element) for element in list_)
    except TypeError:
        return False
