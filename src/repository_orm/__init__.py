"""Library to ease the implementation of the repository pattern in Python projects."""

from .adapters import (
    FakeRepository,
    FakeRepositoryDB,
    Models,
    OptionalModelOrModels,
    OptionalModels,
    PypikaRepository,
    Repository,
    TinyDBRepository,
)
from .exceptions import AutoIncrementError, EntityNotFoundError
from .model import Entity, EntityID
from .services import load_repository

__all__ = [
    "AutoIncrementError",
    "Entity",
    "EntityID",
    "EntityNotFoundError",
    "FakeRepository",
    "FakeRepositoryDB",
    "Models",
    "OptionalModels",
    "OptionalModelOrModels",
    "PypikaRepository",
    "Repository",
    "Repository",
    "TinyDBRepository",
    "load_repository",
]
