"""Gather the cases and fixtures needed to test the model Entities."""

from typing import Any, Type

from pydantic_factories import ModelFactory

from .model import Article, Author, Book, Genre, ListEntity


class EntityCases:
    """Gather all the entities to test."""

    def case_author(self) -> Type[ModelFactory[Any]]:
        """Return the Author factory."""
        return AuthorFactory

    def case_book(self) -> Type[ModelFactory[Any]]:
        """Return the Book factory."""
        return BookFactory

    def case_genre(self) -> Type[ModelFactory[Any]]:
        """Return the Genre factory."""
        return GenreFactory

    def case_article(self) -> Type[ModelFactory[Any]]:
        """Return the Genre factory."""
        return ArticleFactory


class StrEntityCases:
    """Gather all the entities to test with type(id_) == str."""

    def case_author(self) -> Type[ModelFactory[Any]]:
        """Return the Author factory."""
        return AuthorFactory


class IntEntityCases:
    """Gather all the entities to test with type(id_) == int."""

    def case_book(self) -> Type[ModelFactory[Any]]:
        """Return the Book factory."""
        return BookFactory

    def case_genre(self) -> Type[ModelFactory[Any]]:
        """Return the Genre factory."""
        return GenreFactory


class AuthorFactory(ModelFactory[Any]):
    """Factory to generate fake authors."""

    __model__ = Author


class BookFactory(ModelFactory[Any]):
    """Factory to generate fake books."""

    __model__ = Book


class GenreFactory(ModelFactory[Any]):
    """Factory to generate fake genres."""

    __model__ = Genre


class ListEntityFactory(ModelFactory[Any]):
    """Factory to generate fake list of entities."""

    __model__ = ListEntity


class ArticleFactory(ModelFactory[Any]):
    """Factory to generate fake list of entities."""

    __model__ = Article
