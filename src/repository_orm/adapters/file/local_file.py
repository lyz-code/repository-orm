"""Define the local filesystem adapter."""

import logging
import os
from typing import AnyStr

from ...model import File
from .abstract import FileRepository

log = logging.getLogger(__name__)


class LocalFileRepository(FileRepository[AnyStr]):
    """Define the local filesystem adapter."""

    def __init__(self, workdir: str) -> None:
        """Initialize the object.

        Creates the working directory if it doesn't exist.
        """
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        super().__init__(workdir=workdir)

    def load(self, file_: File[AnyStr]) -> File[AnyStr]:
        """Load the content of the file from the persistence system."""
        log.debug(f"Loading content of file {file_.path}")
        file_ = self.fix_path(file_)
        if file_.is_bytes:
            mode = "rb"
            encoding = None
        else:
            mode = "r"
            encoding = "utf-8"

        with open(
            os.path.expanduser(file_.path), mode, encoding=encoding
        ) as file_descriptor:
            # W0212: Access to private attribute, but it's managed by us so it's OK
            file_._content = file_descriptor.read()  # noqa: W0212
        return file_

    def save(self, file_: File[AnyStr]) -> File[AnyStr]:
        """Save the content of the file into the persistence system."""
        log.debug(f"Saving the content of file {file_.path}")
        file_ = self.fix_path(file_)
        if file_.is_bytes:
            mode = "wb+"
        else:
            mode = "w+"

        with open(os.path.expanduser(file_.path), mode) as file_descriptor:
            file_descriptor.write(file_.content)

        return file_

    def delete(self, file_: File[AnyStr]) -> None:
        """Delete the file from the persistence system."""
        log.debug(f"Deleting the content of file {file_.path}")
        try:
            os.remove(os.path.expanduser(file_.path))
        except FileNotFoundError:
            log.warning(
                f"Can't remove the file {file_.path} as it doesn't exist "
                "in the file repository."
            )
