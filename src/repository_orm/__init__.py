"""Library to ease the implementation of the repository pattern in Python projects."""

from .adapters import (
    AbstractRepository,
    FakeRepository,
    FakeRepositoryDB,
    PypikaRepository,
    Repository,
    TinyDBRepository,
)
from .exceptions import AutoIncrementError, EntityNotFoundError
from .model import Entity, EntityID
from .services import load_repository

__all__ = [
    "AbstractRepository",
    "AutoIncrementError",
    "Entity",
    "EntityID",
    "EntityNotFoundError",
    "FakeRepository",
    "FakeRepositoryDB",
    "PypikaRepository",
    "TinyDBRepository",
    "Repository",
    "load_repository",
]
