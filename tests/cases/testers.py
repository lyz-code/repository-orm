"""Gather the tester classes used by the repository tests."""

import abc
import datetime
import json
import logging
import os
import sqlite3
from typing import Any, AnyStr, Dict, Generator, Generic, List, Type, TypeVar

from _pytest.logging import LogCaptureFixture
from pypika import Query, Table

from repository_orm import Entity as EntityModel
from repository_orm import (
    EntityNotFoundError,
    FakeRepository,
    FakeRepositoryDB,
    File,
    PypikaRepository,
    TinyDBRepository,
)

Entity = TypeVar("Entity", bound=EntityModel)
Repository = TypeVar("Repository")
FileRepository = TypeVar("FileRepository")


class RepositoryTester(abc.ABC, Generic[Repository]):
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


# R0201: We can't define the method as a class function to maintain the parent interface
# W0613: We require these arguments to maintain the parent interface.
class FakeRepositoryTester(RepositoryTester[FakeRepository]):
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

        database[type(entity)][entity.id_] = entity.copy()


class TinyDBRepositoryTester(RepositoryTester[TinyDBRepository]):
    """Gathers methods needed to test the implementation of the TinyDBRepository."""

    def assert_schema_exists(
        self, database: Any, caplog: LogCaptureFixture  # noqa: W0613
    ) -> None:
        """Make sure that the repository has a valid schema."""
        # The fake repository has no schema
        assert True

    def apply_migrations(self, repo: Repository) -> None:
        """Apply the repository migrations."""

    @staticmethod
    def _build_cursor(database_url: str) -> Dict[Any, Any]:
        """Load the database data as a python object."""
        database_file = database_url.replace("tinydb:///", "")

        with open(database_file, "r", encoding="utf-8") as file_cursor:
            content = file_cursor.read()
            if content == "":
                content = '{"_default": {}}'
            return json.loads(content)

    def get_entity(self, database: str, entity: Entity) -> Entity:
        """Get the entity object from the data stored in the repository by it's id."""
        cursor = self._build_cursor(database)
        for _document_id, entry in cursor["_default"].items():
            if (
                entry["id_"] == entity.id_
                and entry["model_type_"] == entity.model_name.lower()
            ):
                return self._build_entity(entry, entity.__class__)
        raise EntityNotFoundError()

    @staticmethod
    def _build_entity(
        entity_data: Dict[Any, Any], entity_model: Type[Entity]
    ) -> Entity:
        """Create an Entity object from the data stored in the database.

        Args:
            entity_data: database row.
            entity_model: Entity class to populate

        Returns:
            entity: Entity object built from the data.
        """
        entity_data.pop("model_type_")
        for key, value in entity_data.items():
            if isinstance(value, str) and "TinyDate" in value:
                value = value.replace("{TinyDate}:", "")
                entity_data[key] = datetime.datetime.fromisoformat(value)

        return entity_model.parse_obj(entity_data)

    def get_all(self, database: str, entity_model: Type[Entity]) -> List[Entity]:
        """Get all the entities of type entity_model from the database."""
        cursor = self._build_cursor(database)
        entities = []
        for _document_id, entry in cursor["_default"].items():
            if entry["model_type_"] == entity_model.__name__.lower():
                entities.append(self._build_entity(entry, entity_model))
        return entities

    def insert_entity(self, database: str, entity: Entity) -> None:
        """Insert the data of an entity into the repository."""
        cursor = self._build_cursor(database)

        database_entry = entity.dict()
        database_entry["model_type_"] = entity.model_name.lower()
        for key, value in database_entry.items():
            if isinstance(value, datetime.datetime):
                database_entry[key] = "{TinyDate}:" + value.isoformat()

        try:
            max_document = int(max(key for key in cursor["_default"]))
        except ValueError:
            max_document = -1

        cursor["_default"][max_document + 1] = database_entry

        database_file = database.replace("tinydb:///", "")
        with open(database_file, "w+", encoding="utf-8") as file_cursor:
            file_cursor.write(json.dumps(cursor))


class PypikaRepositoryTester(RepositoryTester[PypikaRepository]):
    """Gathers methods needed to test the implementation of the PypikaRepository."""

    @staticmethod
    def _build_cursor(database_url: str) -> Generator[sqlite3.Cursor, None, None]:
        """Create a cursor to connect to the database."""
        connection = sqlite3.connect(database_url.replace("sqlite:///", ""))

        yield connection.cursor()

        connection.close()

    def apply_migrations(self, repo: PypikaRepository) -> None:
        """Apply the repository migrations."""
        repo.apply_migrations("tests/migrations/pypika")

    def assert_schema_exists(
        self,
        database: str,
        caplog: LogCaptureFixture,
    ) -> None:
        """Make sure that the repository has a valid schema."""
        cursor = next(self._build_cursor(database))
        assert len(cursor.execute("SELECT * from _yoyo_log").fetchall()) > 0
        assert (
            "repository_orm.adapters.data.pypika",
            logging.DEBUG,
            "Complete running database migrations",
        ) in caplog.record_tuples

    def _build_entities(
        self, database: str, entity_model: Type[Entity], query: Query
    ) -> List[Entity]:
        """Build Entity objects from the data extracted from the database.

        Args:
            entity_model: The model of the entity to build
            query: pypika query of the entities you want to build
        """
        cursor = next(self._build_cursor(database))
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
        table = Table(entity.model_name.lower())
        entities = self._build_entities(
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
        entities = self._build_entities(
            database,
            entity_model,
            Query.from_(table).select("*"),
        )
        return entities

    def insert_entity(self, database: str, entity: Entity) -> None:
        """Insert the data of an entity into the repository."""
        table = Table(entity.model_name.lower())
        cursor = next(self._build_cursor(database))
        columns = list(entity.dict().keys())
        columns[columns.index("id_")] = "id"
        values = [value for key, value in entity.dict().items()]
        query = Query.into(table).columns(tuple(columns)).insert(tuple(values))
        cursor.execute(str(query))
        cursor.connection.commit()


class FileRepositoryTester(abc.ABC, Generic[AnyStr]):
    """Define common methods and interface of the file repository testers."""

    @abc.abstractmethod
    def content(self, file_: File[AnyStr]) -> AnyStr:
        """Return the content of the file."""
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, content: AnyStr, path: str, workdir: str) -> None:
        """Save the content of the file in the path."""
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, path: str) -> bool:
        """Test if the file exists in the repository."""
        raise NotImplementedError


class LocalFileRepositoryTester(FileRepositoryTester[AnyStr]):
    """Define methods needed to test the implementation of the LocalFileRepository."""

    def content(self, file_: File[AnyStr]) -> AnyStr:
        """Return the content of the file."""
        if file_.is_bytes:
            mode = "rb"
        else:
            mode = "r"
        with open(file_.path, mode) as file_descriptor:
            return file_descriptor.read()

    def save(self, content: AnyStr, path: str, workdir: str) -> None:
        """Save the content of the file in the path."""
        if isinstance(content, str):
            mode = "w+"
            encoding = "utf-8"
        else:
            mode = "wb+"
            encoding = None

        with open(f"{workdir}/{path}", mode, encoding=encoding) as file_descriptor:
            file_descriptor.write(content)

    def exists(self, path: str) -> bool:
        """Test if the file exists in the repository."""
        return os.path.isfile(path)
