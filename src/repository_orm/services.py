"""Define all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

# W0611: It thinks tat AnyStr is not used, but it is

import warnings
from typing import TYPE_CHECKING, AnyStr, Optional, TypeVar, Union  # noqa: W0611

from .adapters.data.abstract import Models
from .adapters.data.fake import FakeRepository
from .adapters.data.pypika import PypikaRepository
from .adapters.data.tinydb import TinyDBRepository
from .adapters.file.local_file import LocalFileRepository
from .model import Entity as EntityModel

if TYPE_CHECKING:
    from .adapters.file.abstract import FileRepository

Repository = Union[FakeRepository, PypikaRepository, TinyDBRepository]

Entity = TypeVar("Entity", bound=EntityModel)


def load_repository(
    database_url: str = "fake://",
    models: Optional[Models[Entity]] = None,
    search_exception: Optional[bool] = None,
) -> Repository:
    """Load the Repository object that matches the database url protocol.

    Args:
        database_url: Url to connect to the storage backend.

    Returns:
        Repository that understands the url protocol.
    """
    if models is not None:
        warnings.warn(
            "In 2022-12-10 using load_repository with the argument "
            "models is going to be deprecated, please remove argument.",
            UserWarning,
        )
    if search_exception is not None:
        warnings.warn(
            "In 2022-12-10 using load_repository with the argument "
            "search_exception is going to be deprecated as it was a flag to test "
            "a new behaviour that is now implemented, please remove argument.",
            UserWarning,
        )
    if "fake://" in database_url:
        return FakeRepository("", search_exception)
    if "sqlite://" in database_url:
        return PypikaRepository(database_url, search_exception)
    if "tinydb://" in database_url:
        return TinyDBRepository(database_url, search_exception)

    raise ValueError(f"Database URL: {database_url} not recognized.")


def load_file_repository(url: str = "local:.") -> "FileRepository[AnyStr]":
    """Load the FileRepository object that matches the url protocol.

    Args:
        url: Url to connect to the storage backend.

    Returns:
        File Repository that understands the url protocol.
    """
    if "local:" in url:
        return LocalFileRepository(workdir=url.split(":")[1])

    raise ValueError(f"File Repository URL: {url} not recognized.")
