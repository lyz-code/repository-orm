from repository_orm import Entity


class Author(Entity):
    name: str
    is_alive: bool = True


author = Author(name="Brandon")

# Imagine a complex process here that creates an updated version of the author object
new_author = Author(name="New name", is_alive=False)

author.merge(new_author)
assert author.name == "New name"
assert not author.is_alive

# Nevertheless the default values are not merged!
author.merge(Author(name="Brandon"))
assert not author.is_alive

# Unless specified by the user
author.merge(Author(name="Brandon", is_alive=True))
assert author.is_alive
