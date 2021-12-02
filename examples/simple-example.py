from repository_orm import Entity, load_repository


class Author(Entity):
    first_name: str
    last_name: str
    country: str


repo = load_repository()

author = Author(first_name="Brandon", last_name="Sanderson", country="US")

# Add entities
repo.add(author)
repo.commit()

# Retrieve entities by their ID
brandon = repo.get(0, Author)
assert brandon == author

# Search entities
brandon = repo.search({"first_name": "Brandon"}, Author)[0]
assert brandon == author

# Delete entities
repo.delete(brandon)
repo.commit()
assert len(repo.all()) == 0
