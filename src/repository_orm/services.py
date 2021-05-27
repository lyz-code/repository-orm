"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

from typing import Optional, TypeVar, Union

from .adapters import FakeRepository, Models, PypikaRepository, TinyDBRepository
from .model import Entity as EntityModel

Repository = Union[FakeRepository, PypikaRepository, TinyDBRepository]

Entity = TypeVar("Entity", bound=EntityModel)


def load_repository(
    models: Optional[Models[Entity]] = None, database_url: Optional[str] = None
) -> Repository:
    """Load the Repository object that matches the database_url protocol.

    Args:
        database_url: Url to connect to the storage backend.

    Returns:
        Repository that understands the url protocol.
    """
    if database_url is None or "fake://" in database_url:
        return FakeRepository(models, "")
    if "sqlite://" in database_url:
        return PypikaRepository(models, database_url)
    if "tinydb://" in database_url:
        return TinyDBRepository(models, database_url)

    raise ValueError(f"Database URL: {database_url} not recognized.")
