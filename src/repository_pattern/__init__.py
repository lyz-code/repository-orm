"""Library to ease the implementation of the repository pattern in python projects.."""

from typing import TypeVar

from .adapters import AbstractRepository
from .adapters.fake import FakeRepository, FakeRepositoryDB
from .adapters.pypika import PypikaRepository
from .exceptions import EntityNotFoundError
from .model import Entity

Repository = TypeVar("Repository", PypikaRepository, FakeRepository)

__all__ = [
    "AbstractRepository",
    "Entity",
    "EntityNotFoundError",
    "FakeRepository",
    "FakeRepositoryDB",
    "PypikaRepository",
    "Repository",
]
