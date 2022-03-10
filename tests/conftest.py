"""Store the classes and fixtures used throughout the tests."""

import os
import sqlite3
from typing import Any, AnyStr, Generator, List, Tuple, Type

import pytest
from py._path.local import LocalPath
from pydantic_factories import ModelFactory
from pytest_cases import fixture, parametrize_with_cases, unpack_fixture
from tinydb import TinyDB

from repository_orm import (
    FakeRepository,
    LocalFileRepository,
    PypikaRepository,
    Repository,
    TinyDBRepository,
)
from repository_orm.adapters.file.abstract import FileRepository

from .cases import (
    Entity,
    EntityCases,
    IntEntityCases,
    RepositoryCases,
    RepositoryTester,
    StrEntityCases,
)
from .cases.repositories import FileRepositoryCases
from .cases.testers import FileRepositoryTester

# ---------------------
# - Database fixtures -
# ---------------------


@pytest.fixture(name="db_sqlite")
def db_sqlite_(tmpdir: LocalPath) -> Generator[Tuple[str, sqlite3.Cursor], None, None]:
    """Create an SQLite database engine.

    It also sets the environmental variable REPOSITORY_DATABASE_URL.

    Returns:
        database_url: Url used to connect to the database.
        cursor: An sqlite cursor to execute direct queries.
    """
    sqlite_file_path = str(tmpdir.join("sqlite.db"))  # type: ignore
    with open(sqlite_file_path, "a", encoding="utf-8") as file_cursor:
        file_cursor.close()

    sqlite_url = f"sqlite:///{sqlite_file_path}"
    os.environ["REPOSITORY_DATABASE_URL"] = sqlite_url

    connection = sqlite3.connect(sqlite_file_path)

    yield sqlite_url, connection.cursor()

    connection.close()


@pytest.fixture(name="db_tinydb")
def db_tinydb_(tmpdir: LocalPath) -> Tuple[str, TinyDB]:
    """Create an TinyDB database engine.

    It also sets the environmental variable REPOSITORY_DATABASE_URL.

    Returns:
        database_url: Url used to connect to the database.
        cursor: An tinydb cursor to execute direct queries.
    """
    # ignore: Call of untyped join function in typed environment.
    # Until they give typing information there is nothing else to do.
    tinydb_file_path = str(tmpdir.join("tinydb.db"))  # type: ignore
    with open(tinydb_file_path, "a", encoding="utf-8") as file_cursor:
        file_cursor.close()

    tinydb_url = f"tinydb:///{tinydb_file_path}"
    os.environ["REPOSITORY_DATABASE_URL"] = tinydb_url

    return tinydb_url, TinyDB(tinydb_file_path)


# -----------------------
# - Repository fixtures -
# -----------------------
@pytest.fixture()
def repo_fake() -> Generator[FakeRepository, None, None]:
    """Return an instance of the FakeRepository."""
    fake_repo = FakeRepository()

    yield fake_repo

    fake_repo.close()


@pytest.fixture(name="repo_tinydb")
def repo_tinydb_(
    db_tinydb: Tuple[str, TinyDB]
) -> Generator[TinyDBRepository, None, None]:
    """Return an instance of the TinyDBRepository."""
    tiny_repo = TinyDBRepository(database_url=db_tinydb[0])

    yield tiny_repo

    tiny_repo.close()


@pytest.fixture(name="empty_repo_pypika")
def empty_repo_pypika_(
    db_sqlite: Tuple[str, sqlite3.Cursor]
) -> Generator[PypikaRepository, None, None]:
    """Configure an empty instance of the PypikaRepository."""
    sqlite_url = db_sqlite[0]
    pika_repo = PypikaRepository(database_url=sqlite_url)

    yield pika_repo

    pika_repo.close()


@pytest.fixture()
def repo_pypika(
    empty_repo_pypika: PypikaRepository,
) -> Generator[PypikaRepository, None, None]:
    """Configure an instance of the PypikaRepository with the migrations applied."""
    empty_repo_pypika.apply_migrations("tests/migrations/pypika/")

    yield empty_repo_pypika

    empty_repo_pypika.close()


@fixture
@parametrize_with_cases(
    "database_, empty_repo_, repo_, repo_tester_", cases=RepositoryCases
)
def repo_test_fixture(
    database_: Any,
    empty_repo_: Repository,
    repo_: Repository,
    repo_tester_: RepositoryTester[Repository],
) -> Tuple[Any, Repository, Repository, RepositoryTester[Repository]]:
    """Generate the required fixtures to test the repositories.

    It creates a tuple containing:

    * A cursor to execute direct queries to the database
    * An empty repository
    * A configured repository
    * A tester object

    For each repository type.
    """
    return database_, empty_repo_, repo_, repo_tester_


# W0632: We know they are going to return four objects.
database, empty_repo, repo, repo_tester = unpack_fixture(  # noqa: W0632
    "database,empty_repo,repo,repo_tester", repo_test_fixture
)


# ----------------------------
# - File Repository fixtures -
# ----------------------------
@pytest.fixture(name="repo_local_file")
def repo_local_file_(tmpdir: LocalPath) -> LocalFileRepository[AnyStr]:
    """Configure a temporal LocalFileRepository."""
    return LocalFileRepository(workdir=str(tmpdir))


@fixture
@parametrize_with_cases("file_repo_, file_repo_tester_", cases=FileRepositoryCases)
def file_repo_test_fixture(
    file_repo_: FileRepository[AnyStr],
    file_repo_tester_: FileRepositoryTester[AnyStr],
) -> Tuple[FileRepository[AnyStr], FileRepositoryTester[AnyStr]]:
    """Generate the required fixtures to test the file repositories.

    It creates a tuple containing:

    * A configured repository
    * A tester object

    For each file repository type.
    """
    return file_repo_, file_repo_tester_


# W0632: We know they are going to return four objects.
file_repo, file_repo_tester = unpack_fixture(  # noqa: W0632
    "file_repo,file_repo_tester", file_repo_test_fixture
)


# -------------------
# - Entity fixtures -
# -------------------


@fixture(name="entity")
@parametrize_with_cases("entity_factory", cases=EntityCases)
def entity_(entity_factory: Type[ModelFactory[Any]]) -> Entity:
    """Return one entity for each entity type defined in the EntityCases."""
    return entity_factory.build()


@fixture(name="str_entity")
@parametrize_with_cases("entity_factory", cases=StrEntityCases)
def str_entity_(entity_factory: Type[ModelFactory[Any]]) -> Entity:
    """Return one entity for each entity type defined in the StrEntityCases."""
    return entity_factory.build()


@fixture(name="int_entity")
@parametrize_with_cases("entity_factory", cases=IntEntityCases)
def int_entity_(entity_factory: Type[ModelFactory[Any]]) -> Entity:
    """Return one entity for each entity type defined in the IntEntityCases."""
    return entity_factory.build()


@fixture(name="entities")
@parametrize_with_cases("entity_factory", cases=EntityCases)
def entities_(entity_factory: Type[ModelFactory[Any]]) -> List[Entity]:
    """Return three entities for each entity type defined in the EntityCases."""
    return sorted(entity_factory.batch(3))


@fixture(name="str_entities")
@parametrize_with_cases("entity_factory", cases=StrEntityCases)
def str_entities_(entity_factory: Type[ModelFactory[Any]]) -> List[Entity]:
    """Return three entities for each entity type defined in the StrEntityCases."""
    return sorted(entity_factory.batch(3))


@fixture(name="int_entities")
@parametrize_with_cases("entity_factory", cases=IntEntityCases)
def int_entities_(entity_factory: Type[ModelFactory[Any]]) -> List[Entity]:
    """Return three entities for each entity type defined in the IntEntityCases."""
    return sorted(entity_factory.batch(3))


@fixture(name="inserted_entity")
# I don't know how to avoid the W0621 error with pytest-cases
def inserted_entity_(
    entity: Entity,
    database: Any,  # noqa: W0621
    repo_tester: RepositoryTester[Repository],  # noqa: W0621
) -> Entity:
    """Insert one entity in the repository and return it.

    For each entity type defined in the EntityCases.
    """
    repo_tester.insert_entity(database, entity)
    return entity


@fixture
# I don't know how to avoid the W0621 error with pytest-cases
def inserted_int_entity(
    int_entity: Entity,
    database: Any,  # noqa: W0621
    repo_tester: RepositoryTester[Repository],  # noqa: W0621
) -> Entity:
    """Insert one entity with int id_ in the repository and return it.

    For each entity type defined in the EntityCases.
    """
    repo_tester.insert_entity(database, int_entity)
    return int_entity


@fixture
# I don't know how to avoid the W0621 error with pytest-cases
def inserted_str_entity(
    str_entity: Entity,
    database: Any,  # noqa: W0621
    repo_tester: RepositoryTester[Repository],  # noqa: W0621
) -> Entity:
    """Insert one entity with str id_ in the repository and return it.

    For each entity type defined in the EntityCases.
    """
    repo_tester.insert_entity(database, str_entity)
    return str_entity


@fixture
# I don't know how to avoid the W0621 error with pytest-cases
def inserted_entities(
    entities: List[Entity],
    database: Any,  # noqa: W0621
    repo_tester: RepositoryTester[Repository],  # noqa: W0621
) -> List[Entity]:
    """Insert three entities in the repository and return them.

    For each entity type defined in the EntityCases.
    """
    for entity_to_insert in entities:
        repo_tester.insert_entity(database, entity_to_insert)
    return sorted(entities)
