import pytest

from repository_orm import Entity, FakeRepository, Repository


@pytest.fixture()
def repo() -> FakeRepository:
    return FakeRepository()


class Author(Entity):
    first_name: str


def create_greeting(repo: Repository, author_id: int) -> str:
    author = repo.get(Author, author_id)
    return f"Hi {author.first_name}!"


def test_greetings(repo: FakeRepository) -> None:
    author = Author(id_=20, first_name="Brandon")
    repo.add(author)
    repo.commit()

    result = create_greeting(repo, 20)

    assert result == "Hi Brandon!"
