"""Test the File model."""

import pytest

from repository_orm.exceptions import FileContentNotLoadedError
from repository_orm.model import File


def test_file_basename() -> None:
    """
    Given: A File object
    When: using the basename method
    Then: the name of the file is returned
    """
    file_ = File(path="/tmp/file.txt")

    result = file_.basename

    assert result == "file.txt"


def test_file_dirname() -> None:
    """
    Given: A File object
    When: using the dirname method
    Then: the name of the directory containing the file is returned
    """
    file_ = File(path="/tmp/file.txt")

    result = file_.dirname

    assert result == "/tmp"


def test_file_extension() -> None:
    """
    Given: A File object
    When: using the extension method
    Then: the extension of the file is returned
    """
    file_ = File(path="/tmp/file.txt")

    result = file_.extension

    assert result == "txt"


def test_file_content() -> None:
    """
    Given: A File object with the content loaded.
    When: using the content property
    Then: the content of the file is returned

    The use of a private attribute and the impossibility of loading the content
    at object creation will be fixed on Pydantic 1.9, for more information on how to
    improve this code, read this:
        https://lyz-code.github.io/blue-book/coding/python/pydantic/#define-fields-to-exclude-from-exporting-at-config-level # noqa:E501
    """
    file_ = File(path="/tmp/file.txt")
    # W0212: access to internal method, we need to use it like that
    file_._content = "content"  # noqa: W0212

    result = file_.content

    assert result == "content"


def test_file_content_raises_error_if_empty() -> None:
    """
    Given: A File object without any content loaded.
    When: using the content property
    Then: an exception is raised.
    """
    file_ = File(path="/tmp/file.txt")
    # W0104: statement looks like it's doing nothing, but it is.

    with pytest.raises(
        FileContentNotLoadedError,
        match="The content of the file has not been loaded yet.",
    ):
        file_.content  # noqa: W0104
