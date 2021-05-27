"""Define the Pypika Repository."""

import logging
import os
import re
import sqlite3
from contextlib import suppress
from sqlite3 import OperationalError
from typing import Dict, List, Type, Union

from pypika import Query, Table
from yoyo import get_backend, read_migrations

from ..exceptions import EntityNotFoundError, TooManyEntitiesError
from ..model import EntityID
from .abstract import Entity, OptionalModelOrModels, OptionalModels, Repository

log = logging.getLogger(__name__)


def _regexp(expression: str, item: str) -> bool:
    """Implement the REGEXP filter for SQLite.

    Args:
        expression: regular expression to check.
        item: element to check.

    Returns:
        if the item matches the regular expression.
    """
    reg = re.compile(expression)
    return reg.search(item) is not None


class PypikaRepository(Repository):
    """Implement the repository pattern using the Pypika query builder."""

    def __init__(
        self, models: OptionalModels[Entity] = None, database_url: str = ""
    ) -> None:
        """Initialize the repository attributes.

        Args:
            database_url: URL specifying the connection to the database.
            models: List of stored entity models.
        """
        super().__init__(models, database_url)
        database_file = database_url.replace("sqlite:///", "")
        if not os.path.isfile(database_file):
            try:
                with open(database_file, "a") as file_cursor:
                    file_cursor.close()
            except FileNotFoundError as error:
                raise ConnectionError(
                    f"Could not create the database file: {database_file}"
                ) from error
        self.connection = sqlite3.connect(database_file)
        self.connection.create_function("REGEXP", 2, _regexp)
        self.cursor = self.connection.cursor()

    def _execute(self, query: Union[Query, str]) -> sqlite3.Cursor:
        """Execute an SQL statement from a Pypika query object.

        Args:
            query: Pypika query
        """
        return self.cursor.execute(str(query))

    @staticmethod
    def _table(entity: Entity) -> Table:
        """Return the table of the selected entity object."""
        return Table(entity._model_name.lower())

    @staticmethod
    def _table_model(model: Type[Entity]) -> Table:
        """Return the table of the selected entity class."""
        return Table(model.__name__.lower())

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
        table = self._table(entity)
        columns = list(entity.dict().keys())
        columns[columns.index("id_")] = "id"
        values = [value for key, value in entity.dict().items()]
        insert_query = Query.into(table).columns(tuple(columns)).insert(tuple(values))
        # Until https://github.com/kayak/pypika/issues/535 is solved we need to write
        # The upsert statement ourselves.
        # nosec: B608:hardcoded_sql_expressions, Possible SQL injection vector through
        #   string-based query construction. We're not letting the user define the
        #   values of the query, the only variable inputs are the keys, that are
        #   defined by the developer, so it's not probable that he chooses an
        #   entity attributes that are an SQL injection. Once the #535 issue is
        #   solved, we should get rid of this error too.
        upsert_query = (
            str(insert_query)
            + " ON CONFLICT(id) DO UPDATE SET "  # nosec
            + ", ".join([f"{key}=excluded.{key}" for key in columns])
        )
        self._execute(upsert_query)

        return entity

    def delete(self, entity: Entity) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        table = self._table(entity)
        try:
            self.get(entity.id_, type(entity))
        except EntityNotFoundError as error:
            raise EntityNotFoundError(
                f"Unable to delete entity {entity} because it's not in the repository"
            ) from error
        query = Query.from_(table).delete().where(table.id == entity.id_)
        self._execute(query)

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
        matching_entities = []
        models = self._build_models(models)

        for model in models:
            table = self._table_model(model)
            query = Query.from_(table).select("*").where(table.id == id_)
            matching_entities += self._build_entities(model, query)

        if len(matching_entities) == 1:
            return matching_entities[0]
        elif len(matching_entities) == 0:
            raise self._model_not_found(models, f" with id {id_}")
        else:
            raise TooManyEntitiesError(
                f"More than one entity was found with the id {id_}"
            )

    def all(self, models: OptionalModelOrModels[Entity] = None) -> List[Entity]:
        """Get all the entities from the repository whose class is included in models.

        Args:
            models: Entity class or classes to obtain.
        """
        entities = []
        models = self._build_models(models)

        for model in models:
            table = self._table_model(model)
            query = Query.from_(table).select("*")
            entities += self._build_entities(model, query)

        return entities

    def _build_entities(self, model: Type[Entity], query: Query) -> List[Entity]:
        """Build Entity objects from the data extracted from the database.

        Args:
            models: The model of the entity to build
            query: pypika query of the entities you want to build
        """
        cursor = self._execute(query)

        entities_data = cursor.fetchall()
        attributes = [description[0] for description in cursor.description]

        entities: List[Entity] = []
        for entity_data in entities_data:
            entity_dict = {
                attributes[index]: entity_data[index]
                for index in range(0, len(entity_data))
            }
            entity_dict["id_"] = entity_dict.pop("id")

            entities.append(model(**entity_dict))
        return entities

    def commit(self) -> None:
        """Persist the changes into the repository."""
        self.connection.commit()

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

        for model in models:
            table = self._table_model(model)
            query = Query.from_(table).select("*")

            for key, value in fields.items():
                if key == "id_":
                    key = "id"
                if isinstance(value, str):
                    query = query.where(getattr(table, key).regexp(value))
                else:
                    query = query.where(getattr(table, key) == value)

            with suppress(OperationalError):
                entities += self._build_entities(model, query)

        if len(entities) == 0:
            raise self._model_not_found(
                models, f" that match the search filter {fields}"
            )

        return entities

    def apply_migrations(self, migrations_directory: str) -> None:
        """Run the migrations of the repository schema.

        Args:
            migrations_directory: path to the directory containing the migration
                scripts.
        """
        backend = get_backend(self.database_url)
        migrations = read_migrations(migrations_directory)

        with backend.lock():
            log.info("Running database migrations")
            try:
                backend.apply_migrations(backend.to_apply(migrations))
            except Exception as error:  # noqa: W0703
                # We need to add tests for this function and use a less generic
                # exception
                log.error("Error running database migrations")
                log.error(error)

                log.debug("Rolling back the database migrations")
                try:
                    backend.rollback_migrations(backend.to_rollback(migrations))
                except Exception as error:  # noqa: W0703
                    # We need to add tests for this function and use a less generic
                    # exception
                    log.error("Error rolling back database migrations")
                    log.error(error)
                    raise error
            log.debug("Complete running database migrations")
