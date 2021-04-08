"""Module to store the functions shared by the different adapters.

Abstract Classes:
    AbstractRepository: Gathers common methods and define the interface of the
        repositories.

References:
* https://lyz-code.github.io/blue-book/architecture/repository_pattern/
"""

import logging
from typing import TypeVar

from .abstract import AbstractRepository
from .fake import FakeRepository, FakeRepositoryDB
from .pypika import PypikaRepository
from .tinydb import TinyDBRepository

log = logging.getLogger(__name__)

Repository = TypeVar("Repository", PypikaRepository, FakeRepository, TinyDBRepository)

__all__ = [
    "AbstractRepository",
    "PypikaRepository",
    "FakeRepository",
    "FakeRepositoryDB",
    "TinyDBRepository",
]
