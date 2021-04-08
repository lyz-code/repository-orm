"""Tests the service layer."""

import sqlite3
from typing import Tuple

from tinydb import TinyDB

from repository_pattern import (
    FakeRepository,
    PypikaRepository,
    TinyDBRepository,
    load_repository,
)


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
    result = load_repository("fake://fake.db")

    assert isinstance(result, FakeRepository)


def test_load_repository_loads_pypika_with_sqlite_urls(
    db_sqlite: Tuple[str, sqlite3.Cursor]
) -> None:
    """
    Given: Nothing
    When: load_repository is called without argument
    Then: a working FakeRepository instance is returned
    """
    result = load_repository(db_sqlite[0])

    assert isinstance(result, PypikaRepository)


def test_load_repository_loads_tinydb_with_sqlite_urls(
    db_tinydb: Tuple[str, TinyDB]
) -> None:
    """
    Given: Nothing
    When: load_repository is called without argument
    Then: a working FakeRepository instance is returned
    """
    result = load_repository(db_tinydb[0])

    assert isinstance(result, TinyDBRepository)
