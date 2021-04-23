from repository_orm import Entity, load_repository

repo = load_repository()


class Author(Entity):
    first_name: str


author = Author(first_name="Brandon")

# Add entities
repo.add(author)
repo.commit()

# Retrieve entities by their ID
brandon = repo.get(Author, 0)
assert brandon == author
