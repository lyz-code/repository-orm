"""Define the abstract interface for file repositories."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, AnyStr, Generic

from pydantic import BaseModel  # noqa: E0611

if TYPE_CHECKING:
    from ...model import File


class FileRepository(BaseModel, ABC, Generic[AnyStr]):
    """Define the interface of the file repositories."""

    workdir: str = "."

    @abstractmethod
    def load(self, file_: "File[AnyStr]") -> "File[AnyStr]":
        """Load the content of the file from the persistence system."""
        raise NotImplementedError

    @abstractmethod
    def save(self, file_: "File[AnyStr]") -> "File[AnyStr]":
        """Save the content of the file into the persistence system."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, file_: "File[AnyStr]") -> None:
        """Delete the file from the persistence system."""
        raise NotImplementedError

    def fix_path(self, file_: "File[AnyStr]") -> "File[AnyStr]":
        """Update the path to include the workdir."""
        if self.workdir not in file_.path:
            file_.path = f"{self.workdir}/{file_.path}"
        return file_
