from repository_orm import Entity, load_repository


class Author(Entity):
    first_name: str


repo = load_repository([Author])


author = Author(first_name="Brandon")

# Add entities
repo.add(author)
repo.commit()

# Retrieve entities by their ID
brandon = repo.get(0)
assert brandon == author
