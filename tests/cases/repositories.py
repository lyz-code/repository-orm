"""Gather the repository cases."""

import sqlite3
from typing import Tuple

from repository_pattern import (
    Entity,
    FakeRepository,
    FakeRepositoryDB,
    PypikaRepository,
)

from .testers import FakeRepositoryTester, PypikaRepositoryTester


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

    def case_pypika(
        self,
        db_sqlite: Tuple[str, sqlite3.Cursor],
        empty_repo_pypika: PypikaRepository,
        repo_pypika: PypikaRepository,
    ) -> Tuple[str, PypikaRepository, PypikaRepository, PypikaRepositoryTester]:
        """Return the objects to test the FakeRepository.

        Returns:
            db: The url to connect to the database as we need to create the database
                connection in the tester.
            empty_repo: An PypikaRepository without the schema applied.
            repo: A PypikaRepository with the schema applied.
            repo_tester: The tester class for the PypikaRepository.
        """
        # Return a clean database connection
        return db_sqlite[0], empty_repo_pypika, repo_pypika, PypikaRepositoryTester()
