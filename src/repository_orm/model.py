"""Store the common business model of all entities."""

import os
from datetime import datetime
from typing import Any, AnyStr, Generic, Optional, Union

from pydantic import BaseModel, PrivateAttr

from .exceptions import FileContentNotLoadedError

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
        return hash(f"{self._model_name}-{self.id_}")


class File(Entity, Generic[AnyStr]):
    """Model a computer file."""

    path: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    owner: Optional[str] = None
    group: Optional[str] = None
    permissions: Optional[str] = None

    # The use of a private attribute and the impossibility of loading the content
    # at object creation will be fixed on Pydantic 1.9.
    # We will be able to define the excluded attribute content in the Config of the
    # model.
    #
    # For more information on how to improve this code, read this:
    # https://lyz-code.github.io/blue-book/coding/python/pydantic/#define-fields-to-exclude-from-exporting-at-config-level # noqa:E501
    _content: Optional[AnyStr] = PrivateAttr(None)
    # If the content is of type bytes
    is_bytes: bool = False

    @property
    def basename(self) -> str:
        """Return the name of the file."""
        return os.path.basename(self.path)

    @property
    def dirname(self) -> str:
        """Return the name of the file."""
        return os.path.dirname(self.path)

    @property
    def extension(self) -> str:
        """Return the name of the file."""
        return self.basename.split(".")[-1]

    @property
    def content(self) -> AnyStr:
        """Return the content of the file.

        Returns:
            The content of the file.

        Raises:
            FileContentNotLoadedError: if the content is not yet loaded.
        """
        if self._content is None:
            raise FileContentNotLoadedError(
                "The content of the file has not been loaded yet."
            )
        return self._content
