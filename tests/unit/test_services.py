"""Tests the service layer."""

import sqlite3
from typing import Tuple

import pytest
from tests.cases.model import Author
from tinydb import TinyDB

from repository_orm import (
    FakeRepository,
    LocalFileRepository,
    PypikaRepository,
    TinyDBRepository,
    load_file_repository,
    load_repository,
)


class TestLoadRepository:
    """Test the implementation of the load_repository service."""

    def test_load_repository_loads_fake_by_default(self) -> None:
        """
        Given: Nothing
        When: load_repository is called without argument
        Then: a working FakeRepository instance is returned
        """
        result = load_repository()

        assert isinstance(result, FakeRepository)

    def test_load_repository_loads_fake_with_fake_urls(self) -> None:
        """
        Given: Nothing
        When: load_repository is called without argument
        Then: a working FakeRepository instance is returned
        """
        result = load_repository(database_url="fake://fake.db")

        assert isinstance(result, FakeRepository)

    def test_load_repository_loads_pypika_with_sqlite_urls(
        self, db_sqlite: Tuple[str, sqlite3.Cursor]
    ) -> None:
        """
        Given: Nothing
        When: load_repository is called with a pypika compatible url
        Then: a working PypikaRepository instance is returned
        """
        result = load_repository(database_url=db_sqlite[0])

        assert isinstance(result, PypikaRepository)

    def test_load_repository_loads_tinydb_with_sqlite_urls(
        self, db_tinydb: Tuple[str, TinyDB]
    ) -> None:
        """
        Given: Nothing
        When: load_repository is called with a tinydb compatible url
        Then: a working TinyDBRepository instance is returned
        """
        result = load_repository(database_url=db_tinydb[0])

        assert isinstance(result, TinyDBRepository)
        result.close()

    def test_load_repository_returns_error_if_url_not_recognized(self) -> None:
        """
        Given: Nothing
        When: load_repository is called with an unrecognized url
        Then: An error is raised
        """
        with pytest.raises(ValueError, match="Database URL: .* not recognized."):
            load_repository(database_url="inexistent://path/to/file.db")

    def test_load_repository_loads_models(self) -> None:
        """
        Given: Nothing
        When: load_repository is called with the models.
        Then: a warning is raised not to use it
        """
        with pytest.warns(UserWarning, match="In 2022-12-10.*deprecated"):

            load_repository(models=[Author])  # act

    def test_load_repository_set_search_exception_false(self) -> None:
        """
        Given: Nothing
        When: loading the repository with search_exception not None
        Then: a warning is raised not to use it

        See ADR 005 for more info.
        """
        with pytest.warns(UserWarning, match="In 2022-12-10.*deprecated"):

            load_repository(search_exception=False)  # act


class TestLoadFileRepository:
    """Test the implementation of the load_file_repository service."""

    def test_load_file_repository_loads_local_by_default(self) -> None:
        """
        Given: Nothing
        When: load_repository is called without argument
        Then: a working LocalFileRepository instance is returned
        """
        result = load_file_repository()

        assert isinstance(result, LocalFileRepository)
        assert result.workdir == "."

    def test_load_file_repository_can_specify_local_repository(self) -> None:
        """
        Given: Nothing
        When: load_repository is called with a local directory
        Then: a working LocalFileRepository instance is returned
        """
        result = load_file_repository("local:/tmp/file_data")

        assert isinstance(result, LocalFileRepository)
        assert result.workdir == "/tmp/file_data"

    def test_load_file_repository_returns_error_if_url_not_recognized(self) -> None:
        """
        Given: Nothing
        When: load_file_repository is called with an unrecognized url
        Then: An error is raised
        """
        with pytest.raises(ValueError, match="File Repository URL: .* not recognized."):
            load_file_repository(url="inexistent://path/to/workdir")
