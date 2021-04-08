"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

from typing import Optional, Union

from .adapters import FakeRepository, PypikaRepository, TinyDBRepository

Repository = Union[FakeRepository, PypikaRepository, TinyDBRepository]


def load_repository(database_url: Optional[str] = None) -> Repository:
    """Load the Repository object that matches the database_url protocol.

    Args:
        database_url: Url to connect to the storage backend.

    Returns:
        Repository that understands the url protocol.
    """
    if database_url is None or "fake://" in database_url:
        repo: Repository = FakeRepository()
    elif "sqlite://" in database_url:
        repo = PypikaRepository(database_url)
    elif "tinydb://" in database_url:
        repo = TinyDBRepository(database_url)

    return repo
