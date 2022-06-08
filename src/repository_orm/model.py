"""Store the common business model of all entities."""

import os
from datetime import datetime
from typing import Any, AnyStr, Dict, Generic, List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, PrivateAttr

from .exceptions import FileContentNotLoadedError

EntityID = Union[int, str, AnyHttpUrl]


class Entity(BaseModel):
    """Model of any object no defined by it's attributes whom instead has an identity.

    Unlike value objects, they have *identity equality*. We can change their values, and
    they are still recognizably the same thing.

    An entity with a negative id means that the id needs to be set by the repository.

    The _defined_values are used to know which attributes were set by the user at the
    time of merging objects.
    """

    id_: EntityID = -1
    _defined_values: Dict[str, Any] = PrivateAttr()
    _skip_on_merge: List[str] = []

    # ANN401: Any not allowed, but it's what we have.
    def __init__(self, **data: Any) -> None:  # noqa: ANN401
        """Initialize the defined values."""
        super().__init__(**data)
        self._defined_values = data

    def __lt__(self, other: "Entity") -> bool:
        """Assert if an object is smaller than us.

        Args:
            other: Entity to compare.
        """
        if isinstance(other.id_, int) and isinstance(self.id_, int):
            return self.id_ < other.id_
        return str(self.id_) < str(other.id_)

    def __gt__(self, other: "Entity") -> bool:
        """Assert if an object is greater than us.

        Args:
            other: Entity to compare.
        """
        if isinstance(other.id_, int) and isinstance(self.id_, int):
            return self.id_ > other.id_
        return str(self.id_) > str(other.id_)

    def __hash__(self) -> int:
        """Create an unique hash of the class object."""
        return hash(f"{self.model_name}-{self.id_}")

    # ANN401: Any not allowed, but it's what we have.
    def __setattr__(self, attribute: str, value: Any) -> None:  # noqa: ANN401
        """Store the set attribute into the _defined_values."""
        if attribute != "_defined_values":
            self._defined_values[attribute] = value
        super().__setattr__(attribute, value)

    @property
    def model_name(self) -> str:
        """Return the entity model name."""
        return self.schema()["title"]

    def merge(self, other: "Entity") -> "Entity":
        """Update the attributes with the ones manually set by the user of other.

        If the other object has default values not set by the user, they won't be
        propagated to `self`.

        Args:
            other: Entity to compare.
        """
        if not isinstance(other, type(self)):
            raise ValueError(
                "Can't merge objects of different models "
                f"({self.model_name} with {other.model_name})."
            )
        if self.id_ != other.id_:
            raise ValueError(f"Can't merge two {self.model_name}s with different ids")

        # Merge objects
        # W0212: access to an internal property, but it's managed by us so there is
        # no problem on it.
        for attribute, value in other._defined_values.items():  # noqa: W0212
            if attribute not in self._skip_on_merge:
                setattr(self, attribute, value)

        return self

    @property
    def defined_values(self) -> Dict[str, Any]:
        """Return the entity defined values."""
        return self._defined_values

    def clear_defined_values(self) -> None:
        """Remove all references to defined values.

        I tried to return self so that it can be used chained with repo.get(), but I get
        a mypy error `Incompatible return value type (got "Entity", expected "Entity")`
        """
        self._defined_values = {}


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
