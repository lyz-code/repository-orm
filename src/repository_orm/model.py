"""Module to store the common business model of all entities."""

from typing import Any, Union

from pydantic import BaseModel, PrivateAttr

EntityID = Union[int, str]


class Entity(BaseModel):
    """Model of any object no defined by it's attributes whom instead has an identity.

    Unlike value objects, they have *identity equality*. We can change their values, and
    they are still recognizably the same thing.

    An entity with a negative id means that the id needs to be set by the repository.
    """

    id_: EntityID = -1
    _model_name: str = PrivateAttr()

    def __init__(self, **data: Any) -> None:
        """Set the _model_name attribute."""
        super().__init__(**data)
        self._model_name = self.__class__.__name__

    def __lt__(self, other: "Entity") -> bool:
        """Assert if an object is smaller than us.

        Args:
            other: Entity to compare.

        Raises:
            TypeError: If the id type of the objects is not compatible.
        """
        if not isinstance(other.id_, type(self.id_)):
            raise TypeError(f"{self} and {other} have incompatible ID types")
        # ignore: we've checked that both elements are of the same type
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
        # ignore: we've checked that both elements are of the same type
        return self.id_ > other.id_  # type: ignore

    def __hash__(self) -> int:
        """Create an unique hash of the class object."""
        return hash(self.id_)
