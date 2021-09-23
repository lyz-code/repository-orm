"""Gather the cases and fixtures needed to test the model Entities."""

import factory

from .model import Author, Book, Genre, ListEntity


class EntityCases:
    """Gather all the entities to test."""

    def case_author(self) -> factory.Factory:
        """Return the Author factory."""
        return AuthorFactory

    def case_book(self) -> factory.Factory:
        """Return the Book factory."""
        return BookFactory

    def case_genre(self) -> factory.Factory:
        """Return the Genre factory."""
        return GenreFactory


class StrEntityCases:
    """Gather all the entities to test with type(id_) == str."""

    def case_author(self) -> factory.Factory:
        """Return the Author factory."""
        return AuthorFactory


class IntEntityCases:
    """Gather all the entities to test with type(id_) == int."""

    def case_book(self) -> factory.Factory:
        """Return the Book factory."""
        return BookFactory

    def case_genre(self) -> factory.Factory:
        """Return the Genre factory."""
        return GenreFactory


class AuthorFactory(factory.Factory):  # type: ignore
    """Factory to generate fake authors."""

    id_ = factory.Faker("sentence")
    name = factory.Faker("sentence")
    last_name = factory.Faker("last_name")
    country = factory.Faker("country")
    rating = factory.Faker("pyint")

    class Meta:
        """Define the entity model object to use."""

        model = Author


class BookFactory(factory.Factory):  # type: ignore
    """Factory to generate fake books."""

    id_ = factory.Faker("pyint")
    name = factory.Faker("sentence")
    summary = factory.Faker("text")
    released = factory.Faker("date_time")
    rating = factory.Faker("pyint")

    class Meta:
        """Define the entity model object to use."""

        model = Book


class GenreFactory(factory.Factory):  # type: ignore
    """Factory to generate fake genres."""

    id_ = factory.Faker("pyint")
    name = factory.Faker("sentence")
    description = factory.Faker("sentence")
    rating = factory.Faker("pyint")

    class Meta:
        """Define the entity model object to use."""

        model = Genre


class ListEntityFactory(factory.Factory):  # type: ignore
    """Factory to generate fake list of entities."""

    id_ = factory.Faker("pyint")
    name = factory.Faker("sentence")
    elements = factory.Faker("pylist", value_types=str)

    class Meta:
        """Define the entity model object to use."""

        model = ListEntity
