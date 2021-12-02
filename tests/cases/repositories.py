"""Gather the repository cases."""

import sqlite3
from typing import AnyStr, Tuple, TypeVar

from tinydb import TinyDB

from repository_orm import (
    FakeRepository,
    FakeRepositoryDB,
    LocalFileRepository,
    PypikaRepository,
    TinyDBRepository,
)

from .model import Entity as EntityModel
from .testers import (
    FakeRepositoryTester,
    LocalFileRepositoryTester,
    PypikaRepositoryTester,
    TinyDBRepositoryTester,
)

Entity = TypeVar("Entity", bound=EntityModel)


class RepositoryCases:
    """Gather all the repositories to test."""

    def case_fake(
        self, repo_fake: FakeRepository
    ) -> Tuple[
        FakeRepositoryDB[Entity], FakeRepository, FakeRepository, FakeRepositoryTester
    ]:
        """Return the objects to test the FakeRepository.

        Returns:
            db: The Fakerepository database instance.
            empty_repo: A Fakerepository without the schema applied.
            repo: A Fakerepository with the schema applied. Fake doesn't have schema
                so it's the same as the empty repository.
            repo_tester: The tester class for the Fakerepository.
        """
        return repo_fake.entities, repo_fake, repo_fake, FakeRepositoryTester()

    def case_tinydb(
        self,
        db_tinydb: Tuple[str, TinyDB],
        repo_tinydb: TinyDBRepository,
    ) -> Tuple[str, TinyDBRepository, TinyDBRepository, TinyDBRepositoryTester]:
        """Return the objects to test the FakeRepository.

        Returns:
            db: path to the database file.
            empty_repo: An TinyDBRepository without the schema applied.
            repo: A TinyDBRepository with the schema applied.
            repo_tester: The tester class for the TinyDBRepository.
        """
        return db_tinydb[0], repo_tinydb, repo_tinydb, TinyDBRepositoryTester()

    def case_pypika(
        self,
        db_sqlite: Tuple[str, sqlite3.Cursor],
        empty_repo_pypika: PypikaRepository,
        repo_pypika: PypikaRepository,
    ) -> Tuple[str, PypikaRepository, PypikaRepository, PypikaRepositoryTester]:
        """Return the objects to test the FakeRepository.

        Returns:
            db: path to the database file.
            empty_repo: An PypikaRepository without the schema applied.
            repo: A PypikaRepository with the schema applied.
            repo_tester: The tester class for the PypikaRepository.
        """
        # Return a clean database connection
        return db_sqlite[0], empty_repo_pypika, repo_pypika, PypikaRepositoryTester()


class FileRepositoryCases:
    """Gather all the file repositories to test."""

    def case_local_file(
        self, repo_local_file: LocalFileRepository[AnyStr]
    ) -> Tuple[LocalFileRepository[AnyStr], LocalFileRepositoryTester[AnyStr]]:
        """Return the objects to test the LocalFileRepository.

        Returns:
            repo: A LocalFileRepository with the workdir configured.
            repo_tester: The tester class for the LocalFilerepository.
        """
        return repo_local_file, LocalFileRepositoryTester()
