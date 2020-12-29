"""Gather the tester classes used by the repository tests."""

import abc
import logging
import sqlite3
from typing import Any, Generator, Generic, List, Type, TypeVar

from _pytest.logging import LogCaptureFixture
from pypika import Query, Table

from repository_pattern import (
    Entity,
    FakeRepository,
    FakeRepositoryDB,
    PypikaRepository,
    Repository,
)
from repository_pattern.exceptions import EntityNotFoundError

RepositoryTester = TypeVar(
    "RepositoryTester",
    "FakeRepositoryTester",
    "PypikaRepositoryTester",
)


class AbstractRepositoryTester(abc.ABC, Generic[Repository]):
    """Gather common methods and define the interface of the repository testers."""

    @abc.abstractmethod
    def assert_schema_exists(self, database: Any, caplog: LogCaptureFixture) -> None:
        """Make sure that the repository has a valid schema."""
        raise NotImplementedError

    @abc.abstractmethod
    def apply_migrations(self, repo: Repository) -> None:
        """Apply the repository migrations."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_entity(self, database: Any, entity: Entity) -> Entity:
        """Get the entity object from the data stored in the repository by it's id."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_all(self, database: Any, entity_model: Type[Entity]) -> List[Entity]:
        """Get all the entities of type entity_model from the database."""
        raise NotImplementedError

    @abc.abstractmethod
    def insert_entity(self, database: Any, entity: Entity) -> None:
        """Insert the data of an entity into the repository."""
        raise NotImplementedError


# E1136: false positive: https://github.com/PyCQA/pylint/issues/2822
# R0201: We can't define the method as a class function to maintain the parent interface
# W0613: We require these arguments to maintain the parent interface.
class FakeRepositoryTester(AbstractRepositoryTester[FakeRepository]):  # noqa: E1136
    """Gathers methods needed to test the implementation of the FakeRepository."""

    def apply_migrations(self, repo: FakeRepository) -> None:
        """Apply the repository migrations."""

    def assert_schema_exists(  # noqa: R0201
        self,
        database: FakeRepositoryDB[Entity],  # noqa: W0613
        caplog: LogCaptureFixture,  # noqa: W0613
    ) -> None:
        """Make sure that the repository has a valid schema."""
        # The fake repository has no schema
        assert True

    def get_entity(  # noqa: R0201
        self, database: FakeRepositoryDB[Entity], entity: Entity
    ) -> Entity:
        """Get the entity object from the data stored in the repository by it's id."""
        try:
            return database[type(entity)][entity.id_]
        except (TypeError, KeyError) as error:
            raise EntityNotFoundError() from error

    def get_all(  # noqa: R0201
        self, database: FakeRepositoryDB[Entity], entity_model: Type[Entity]
    ) -> List[Entity]:
        """Get all the entities of type entity_model from the database."""
        try:
            return [entity for entity_id, entity in database[entity_model].items()]
        except (TypeError, KeyError) as error:
            raise EntityNotFoundError() from error

    def insert_entity(  # noqa: R0201
        self, database: FakeRepositoryDB[Entity], entity: Entity
    ) -> None:
        """Insert the data of an entity into the repository."""
        try:
            database[type(entity)]
        except KeyError:
            database[type(entity)] = {}

        database[type(entity)][entity.id_] = entity


# E1136 false positive: https://github.com/PyCQA/pylint/issues/2822
class PypikaRepositoryTester(AbstractRepositoryTester[PypikaRepository]):  # noqa: E1136
    """Gathers methods needed to test the implementation of the PypikaRepository."""

    @staticmethod
    def build_cursor(database_url: str) -> Generator[sqlite3.Cursor, None, None]:
        """Create a cursor to connect to the database."""
        connection = sqlite3.connect(database_url.replace("sqlite:///", ""))

        yield connection.cursor()

        connection.close()

    @staticmethod
    def apply_migrations(repo: PypikaRepository) -> None:
        """Apply the repository migrations."""
        repo.apply_migrations("tests/migrations/pypika")

    def assert_schema_exists(
        self,
        database: str,
        caplog: LogCaptureFixture,
    ) -> None:
        """Make sure that the repository has a valid schema."""
        cursor = next(self.build_cursor(database))
        assert len(cursor.execute("SELECT * from _yoyo_log").fetchall()) > 0
        assert (
            "repository_pattern.adapters.pypika",
            logging.DEBUG,
            "Complete running database migrations",
        ) in caplog.record_tuples

    def build_entities(
        self, database: str, entity_model: Type[Entity], query: Query
    ) -> List[Entity]:
        """Build Entity objects from the data extracted from the database.

        Args:
            entity_model: The model of the entity to build
            query: pypika query of the entities you want to build
        """
        cursor = next(self.build_cursor(database))
        cursor = cursor.execute(str(query))

        entities_data = cursor.fetchall()
        attributes = [description[0] for description in cursor.description]

        entities: List[Entity] = []
        for entity_data in entities_data:
            entity_dict = {
                attributes[index]: entity_data[index]
                for index in range(0, len(entity_data))
            }
            entity_dict["id_"] = entity_dict.pop("id")

            entities.append(entity_model(**entity_dict))
        return entities

    def get_entity(self, database: str, entity: Entity) -> Entity:
        """Get the entity object from the data stored in the repository by it's id."""
        table = Table(entity.__class__.__name__.lower())
        entities = self.build_entities(
            database,
            type(entity),
            Query.from_(table).select("*").where(table.id == entity.id_),
        )
        try:
            return entities[0]
        except IndexError as error:
            raise EntityNotFoundError() from error

    def get_all(self, database: str, entity_model: Type[Entity]) -> List[Entity]:
        """Get all the entities of type entity_model from the database."""
        table = Table(entity_model.__name__.lower())
        entities = self.build_entities(
            database,
            entity_model,
            Query.from_(table).select("*"),
        )
        return entities

    def insert_entity(self, database: str, entity: Entity) -> None:
        """Insert the data of an entity into the repository."""
        table = Table(entity.__class__.__name__.lower())
        cursor = next(self.build_cursor(database))
        columns = list(entity.dict().keys())
        columns[columns.index("id_")] = "id"
        values = [value for key, value in entity.dict().items()]
        query = Query.into(table).columns(tuple(columns)).insert(tuple(values))
        cursor.execute(str(query))
        cursor.connection.commit()
