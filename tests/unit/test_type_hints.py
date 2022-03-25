"""Test type hints issues."""

from typing import List

from tests.cases.entities import BookFactory
from tests.cases.model import Book

from repository_orm import FakeRepository


def get_books() -> List[Book]:
    """Return some books."""
    return BookFactory.batch(5)


def test_add_works_with_return_value_of_function(repo_fake: FakeRepository) -> None:
    """
    Given: A Fake repository and a function that returns a list of entities
    When: Using repo.add on the result of the function
    Then: no mypy error is returned
    """
    books = get_books()

    result = repo_fake.add(books)

    assert len(result) == 5
