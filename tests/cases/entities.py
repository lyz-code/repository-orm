"""Gather the cases and fixtures needed to test the model Entities."""

import factory

from .model import Author, Book, Genre


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


class AuthorFactory(factory.Factory):  # type: ignore
    """Factory to generate fake authors."""

    ID = factory.Faker("word")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    country = factory.Faker("country")

    class Meta:
        """Define the entity model object to use."""

        model = Author


class BookFactory(factory.Factory):  # type: ignore
    """Factory to generate fake books."""

    ID = factory.Faker("pyint")
    title = factory.Faker("sentence")
    summary = factory.Faker("text")
    released = factory.Faker("date_time")

    class Meta:
        """Define the entity model object to use."""

        model = Book


class GenreFactory(factory.Factory):  # type: ignore
    """Factory to generate fake genres."""

    ID = factory.Faker("pyint")
    name = factory.Faker("name")
    description = factory.Faker("sentence")

    class Meta:
        """Define the entity model object to use."""

        model = Genre
