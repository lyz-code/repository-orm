"""Module to store the common business model of all entities."""

from typing import Union

from pydantic import BaseModel  # noqa: E0611

# E0611: No name 'BaseModel' in module 'pydantic'
# https://github.com/samuelcolvin/pydantic/issues/1961


class Entity(BaseModel):
    """Model of any object no defined by it's attributes whom instead has an identity.

    Unlike value objects, they have *identity equality*. We can change their values, and
    they are still recognizably the same thing.
    """

    id_: Union[int, str]

    def __lt__(self, other: "Entity") -> bool:
        """Assert if an object is smaller than us.

        Args:
            other: Entity to compare.

        Raises:
            TypeError: If the id type of the objects is not compatible.
        """
        if not isinstance(other.id_, type(self.id_)):
            raise TypeError(f"{self} and {other} have incompatible ID types")
        return self.id_ < other.id_  # type: ignore

    def __gt__(self, other: "Entity") -> bool:
        """Assert if an object is greater than us.

        Args:
            other: Entity to compare.

        Raises:
            TypeError: If the id type of the objects is not compatible.
        """
        if not isinstance(other.id_, type(self.id_)):
            raise TypeError(f"{self} and {other} have incompatible ID types")
        return self.id_ > other.id_  # type: ignore

    def __hash__(self) -> int:
        """Create an unique hash of the class object."""
        return hash(self.id_)
