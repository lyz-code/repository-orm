from repository_pattern import Entity, FakeRepository

repo = FakeRepository()


class Author(Entity):
    ID: int
    first_name: str
    last_name: str
    country: str


author = Author(ID=0, first_name="Brandon", last_name="Sanderson", country="US")

# Add entities
repo.add(author)
repo.commit()

# Retrieve entities by their ID
brandon = repo.get(Author, 0)
assert brandon == author

# Search entities
brandon = repo.search(Author, {"first_name": "Brandon"})[0]
assert brandon == author

# Delete entities
repo.delete(brandon)
repo.commit()
assert len(repo.all(Author)) == 0
