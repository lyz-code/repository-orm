"""Define all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

# W0611: It thinks that AnyStr is not used, but it is

from typing import TYPE_CHECKING, AnyStr, Union  # noqa: W0611

from .adapters.data.fake import FakeRepository
from .adapters.data.pypika import PypikaRepository
from .adapters.data.tinydb import TinyDBRepository
from .adapters.file.local_file import LocalFileRepository

if TYPE_CHECKING:
    from .adapters.file.abstract import FileRepository

Repository = Union[FakeRepository, PypikaRepository, TinyDBRepository]


def load_repository(
    database_url: str = "fake://",
) -> Repository:
    """Load the Repository object that matches the database url protocol.

    Args:
        database_url: Url to connect to the storage backend.

    Returns:
        Repository that understands the url protocol.
    """
    if "fake://" in database_url:
        return FakeRepository("")
    if "sqlite://" in database_url:
        return PypikaRepository(database_url)
    if "tinydb://" in database_url:
        return TinyDBRepository(database_url)

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
