"""Store a default model use case to use in the tests."""

from datetime import datetime
from typing import Optional

from repository_orm import Entity as EntityModel


class Entity(EntityModel):
    """Gather the common attributes of testing models."""

    name: str


class Author(Entity):
    """Entity to model the author of a book."""

    id_: str
    last_name: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[int] = None


class Book(Entity):
    """Entity to model a book."""

    summary: Optional[str] = None
    released: Optional[datetime] = None
    rating: Optional[int] = None


class Genre(Entity):
    """Entity to model the genre of a book."""

    description: Optional[str] = None
    rating: Optional[int] = None
