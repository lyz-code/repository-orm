from datetime import datetime

from repository_orm import Entity


class Author(Entity):
    name: str
    is_alive: bool = True
    birthday: datetime
    _skip_on_merge = ["birthday"]


author = Author(name="Brandon", birthday=datetime(2020, 1, 1))
new_author = Author(name="Brandon", birthday=datetime(1900, 1, 1), is_alive=False)

author.merge(new_author)
assert author.birthday == datetime(2020, 1, 1)
assert not author.is_alive
