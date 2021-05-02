import click
import pytest
from click.testing import CliRunner
from py._path.local import LocalPath

from repository_orm import Entity, Repository, TinyDBRepository, load_repository


# Model
class Author(Entity):
    first_name: str


# Fixtures
@pytest.fixture(name="db_tinydb")
def db_tinydb_(tmpdir: LocalPath) -> str:
    tinydb_file_path = str(tmpdir.join("tinydb.db"))
    return f"tinydb:///{tinydb_file_path}"


@pytest.fixture()
def repo(db_tinydb: str) -> TinyDBRepository:
    return TinyDBRepository([Author], db_tinydb)


# Service
def create_greeting(repo: Repository) -> str:
    first_author = repo.all(Author)[0]
    return f"Hi {first_author.first_name}, you're the first author!"


# Entrypoint
@click.command()
@click.argument("database_url")
def greet(database_url: str) -> None:
    repo = load_repository([Author], database_url)

    print(create_greeting(repo))


# Test
def test_greetings(repo: TinyDBRepository, db_tinydb: str) -> None:
    author = Author(id_=20, first_name="Brandon")
    repo.add(author)
    repo.commit()
    runner = CliRunner()

    result = runner.invoke(greet, [db_tinydb])

    assert result.exit_code == 0
    assert result.output == "Hi Brandon, you're the first author!\n"
