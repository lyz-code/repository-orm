"""Tests the service layer."""

import sqlite3
from typing import Tuple

import pytest
from tinydb import TinyDB

from repository_orm import (
    FakeRepository,
    PypikaRepository,
    TinyDBRepository,
    load_repository,
)

from ..cases.model import Author


def test_load_repository_loads_fake_by_default() -> None:
    """
    Given: Nothing
    When: load_repository is called without argument
    Then: a working FakeRepository instance is returned
    """
    result = load_repository()

    assert isinstance(result, FakeRepository)


def test_load_repository_loads_fake_with_fake_urls() -> None:
    """
    Given: Nothing
    When: load_repository is called without argument
    Then: a working FakeRepository instance is returned
    """
    result = load_repository(database_url="fake://fake.db")

    assert isinstance(result, FakeRepository)


def test_load_repository_loads_pypika_with_sqlite_urls(
    db_sqlite: Tuple[str, sqlite3.Cursor]
) -> None:
    """
    Given: Nothing
    When: load_repository is called with a pypika compatible url
    Then: a working PypikaRepository instance is returned
    """
    result = load_repository(database_url=db_sqlite[0])

    assert isinstance(result, PypikaRepository)


def test_load_repository_loads_tinydb_with_sqlite_urls(
    db_tinydb: Tuple[str, TinyDB]
) -> None:
    """
    Given: Nothing
    When: load_repository is called with a tinydb compatible url
    Then: a working TinyDBRepository instance is returned
    """
    result = load_repository(database_url=db_tinydb[0])

    assert isinstance(result, TinyDBRepository)


def test_load_repository_returns_error_if_url_not_recognized() -> None:
    """
    Given: Nothing
    When: load_repository is called with an unrecognized url
    Then: An error is raised
    """
    with pytest.raises(ValueError, match="Database URL: .* not recognized."):
        load_repository(database_url="inexistent://path/to/file.db")


def test_load_repository_loads_models() -> None:
    """
    Given: Nothing
    When: load_repository is called with the models.
    Then: they are saved
    """
    models = [Author]

    result = load_repository(models=models)

    assert result.models == models
