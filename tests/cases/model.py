"""Store a default model use case to use in the tests."""

from datetime import datetime
from typing import List, Optional

from pydantic import AnyHttpUrl

from repository_orm import Entity as EntityModel


class Entity(EntityModel):
    """Gather the common attributes of testing models."""

    name: str
    state: str = "open"
    active: bool = True


class Author(Entity):
    """Entity to model the author of a book."""

    id_: str
    last_name: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[int] = None


class Book(Entity):
    """Entity to model a book."""

    id_: int = -1
    summary: Optional[str] = None
    released: Optional[datetime] = None
    rating: Optional[int] = None


class Genre(Entity):
    """Entity to model the genre of a book."""

    id_: int = -1
    description: Optional[str] = None
    rating: Optional[int] = None

    _skip_on_merge: List[str] = ["rating"]


class Article(Entity):
    """Entity to model an internet article."""

    id_: AnyHttpUrl
    description: Optional[str] = None
    rating: Optional[int] = None


class OtherEntity(Entity):
    """Entity to model an entity that is not in the repo."""

    description: Optional[str] = None


class ListEntity(Entity):
    """Entity to model an entity that has a list of strings attribute."""

    elements: List[str]


class BoolEntity(Entity):
    """Entity to model an entity that has a boolean attribute."""

    active: bool = True
