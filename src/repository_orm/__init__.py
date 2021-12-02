"""Library to ease the implementation of the repository pattern in Python projects."""

from .adapters.data.abstract import (
    Models,
    OptionalModelOrModels,
    OptionalModels,
    Repository,
)
from .adapters.data.fake import FakeRepository, FakeRepositoryDB
from .adapters.data.pypika import PypikaRepository
from .adapters.data.tinydb import TinyDBRepository
from .adapters.file.local_file import LocalFileRepository
from .exceptions import AutoIncrementError, EntityNotFoundError
from .model import Entity, EntityID, File
from .services import load_file_repository, load_repository

__all__ = [
    "AutoIncrementError",
    "Entity",
    "EntityID",
    "EntityNotFoundError",
    "FakeRepository",
    "File",
    "FakeRepositoryDB",
    "LocalFileRepository",
    "Models",
    "OptionalModels",
    "OptionalModelOrModels",
    "PypikaRepository",
    "Repository",
    "Repository",
    "TinyDBRepository",
    "load_repository",
    "load_file_repository",
]
