"""Store the classes and fixtures used throughout the tests."""

import os
import sqlite3
from typing import Any, Generator, List, Tuple

import factory
import pytest
from py._path.local import LocalPath
from pytest_cases import fixture, parametrize_with_cases, unpack_fixture
from tinydb import TinyDB

from repository_orm import (
    FakeRepository,
    PypikaRepository,
    Repository,
    TinyDBRepository,
)

from .cases import (
    Entity,
    EntityCases,
    IntEntityCases,
    RepositoryCases,
    RepositoryTester,
    StrEntityCases,
)
from .cases.model import Author, Book, Genre, OtherEntity

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
    with open(sqlite_file_path, "a") as file_cursor:
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
    with open(tinydb_file_path, "a") as file_cursor:
        file_cursor.close()

    tinydb_url = f"tinydb:///{tinydb_file_path}"
    os.environ["REPOSITORY_DATABASE_URL"] = tinydb_url

    return tinydb_url, TinyDB(tinydb_file_path)


# -----------------------
# - Repository fixtures -
# -----------------------
models = [Author, Book, Genre, OtherEntity]


@pytest.fixture()
def repo_fake() -> FakeRepository:
    """Return an instance of the FakeRepository."""
    return FakeRepository(models=models)


@pytest.fixture(name="repo_tinydb")
def repo_tinydb_(db_tinydb: Tuple[str, TinyDB]) -> TinyDBRepository:
    """Return an instance of the TinyDBRepository."""
    return TinyDBRepository(database_url=db_tinydb[0], models=models)


@pytest.fixture(name="empty_repo_pypika")
def empty_repo_pypika_(db_sqlite: Tuple[str, sqlite3.Cursor]) -> PypikaRepository:
    """Configure an empty instance of the PypikaRepository."""
    sqlite_url = db_sqlite[0]
    return PypikaRepository(database_url=sqlite_url, models=models)


@pytest.fixture()
def repo_pypika(empty_repo_pypika: PypikaRepository) -> PypikaRepository:
    """Configure an instance of the PypikaRepository with the migrations applied."""
    empty_repo_pypika.apply_migrations("tests/migrations/pypika/")
    return empty_repo_pypika


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


# We know they are going to return four objects.
database, empty_repo, repo, repo_tester = unpack_fixture(  # noqa: W0632
    "database,empty_repo,repo,repo_tester", repo_test_fixture
)


# -------------------
# - Entity fixtures -
# -------------------


@fixture
@parametrize_with_cases("entity_factory", cases=EntityCases)
def entity(entity_factory: factory.Factory) -> Entity:
    """Return one entity for each entity type defined in the EntityCases."""
    return entity_factory.create()


@fixture
@parametrize_with_cases("entity_factory", cases=StrEntityCases)
def str_entity(entity_factory: factory.Factory) -> Entity:
    """Return one entity for each entity type defined in the StrEntityCases."""
    return entity_factory.create()


@fixture
@parametrize_with_cases("entity_factory", cases=IntEntityCases)
def int_entity(entity_factory: factory.Factory) -> Entity:
    """Return one entity for each entity type defined in the IntEntityCases."""
    return entity_factory.create()


@fixture
@parametrize_with_cases("entity_factory", cases=EntityCases)
def entities(entity_factory: factory.Factory) -> List[Entity]:
    """Return three entities for each entity type defined in the EntityCases."""
    return sorted(entity_factory.create_batch(3))


@fixture
@parametrize_with_cases("entity_factory", cases=StrEntityCases)
def str_entities(entity_factory: factory.Factory) -> List[Entity]:
    """Return three entities for each entity type defined in the StrEntityCases."""
    return sorted(entity_factory.create_batch(3))


@fixture
@parametrize_with_cases("entity_factory", cases=IntEntityCases)
def int_entities(entity_factory: factory.Factory) -> List[Entity]:
    """Return three entities for each entity type defined in the IntEntityCases."""
    return sorted(entity_factory.create_batch(3))


@fixture
# I don't know how to avoid the W0621 error with pytest-cases
def inserted_entity(
    entity: Entity,
    database: Any,
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
    database: Any,
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
    database: Any,
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
    database: Any,
    repo_tester: RepositoryTester[Repository],  # noqa: W0621
) -> List[Entity]:
    """Insert three entities in the repository and return them.

    For each entity type defined in the EntityCases.
    """
    for entity_to_insert in entities:
        repo_tester.insert_entity(database, entity_to_insert)
    return entities
