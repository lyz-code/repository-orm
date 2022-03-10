"""Test the implementation of the FileRepositories."""

import os
from typing import AnyStr

import pytest
from _pytest.logging import LogCaptureFixture
from py._path.local import LocalPath

from repository_orm import File, LocalFileRepository
from repository_orm.adapters.file.abstract import FileRepository

from ..cases.testers import FileRepositoryTester


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("file content", id="string"),
        pytest.param(b"file content", id="bytes"),
    ],
)
class TestFileRepositories:
    """Test the implementation of the file repositories."""

    def test_repo_can_save_file_content(
        self,
        file_repo: FileRepository[AnyStr],
        file_repo_tester: FileRepositoryTester[AnyStr],
        content: AnyStr,
    ) -> None:
        """
        Given: A File and a FileRepository
        When: Saving the File into the repository
        Then: The content of the File is persisted, and the File's path attribute
            is complemented with the working dir.
        """
        is_bytes = isinstance(content, bytes)
        file_ = File(path="test.txt", is_bytes=is_bytes)
        # W0212: Access to protected method, but we control it
        file_._content = content  # type: ignore # noqa: W0212

        result = file_repo.save(file_)  # type: ignore

        assert file_repo_tester.content(file_) == content  # type: ignore
        assert result.path == f"{file_repo.workdir}/test.txt"

    def test_repo_can_load_file_content(
        self,
        file_repo: FileRepository[AnyStr],
        file_repo_tester: FileRepositoryTester[AnyStr],
        content: AnyStr,
    ) -> None:
        """
        Given: A File in the Repository
        When: Loading the File content
        Then: The content of the File is loaded
        """
        is_bytes = isinstance(content, bytes)
        file_repo_tester.save(content, "test.txt", file_repo.workdir)
        file_ = File(path="test.txt", is_bytes=is_bytes)

        file_repo.load(file_)  # type: ignore # act

        assert file_.content == content

    def test_repo_can_delete_file_content(
        self,
        file_repo: FileRepository[AnyStr],
        file_repo_tester: FileRepositoryTester[AnyStr],
        content: AnyStr,
    ) -> None:
        """
        Given: A File in the Repository
        When: Deleting the file content
        Then: The content of the File is removed
        """
        is_bytes = isinstance(content, bytes)
        file_repo_tester.save(content, "test.txt", file_repo.workdir)
        file_ = File(path="test.txt", is_bytes=is_bytes)

        file_repo.delete(file_)  # type: ignore # act

        assert not file_repo_tester.exists("test.txt")


def test_repo_raises_error_when_loading_unexistent_file(
    file_repo: FileRepository[AnyStr],
) -> None:
    """
    Given: Nothing in the Repository
    When: Loading the File content
    Then: An error is raised, as there is nothing to load.
    """
    file_ = File(path="test.txt")

    with pytest.raises(FileNotFoundError):
        file_repo.load(file_)  # type: ignore


def test_repo_raises_error_when_removing_unexistent_file(
    file_repo: FileRepository[AnyStr],
    caplog: LogCaptureFixture,
) -> None:
    """
    Given: Nothing in the Repository
    When: Removing the File content
    Then: A warning is raised, as there is nothing to remove.
    """
    file_ = File(path="test.txt")

    file_repo.delete(file_)  # type: ignore # act

    assert caplog.record_tuples == [
        (
            "repository_orm.adapters.file.local_file",
            30,
            "Can't remove the file test.txt as it "
            "doesn't exist in the file repository.",
        )
    ]


class TestLocalFileRepository:
    """Test particular details of the LocalFileRepository."""

    def test_creates_workdir_if_it_doesnt_exist(self, tmpdir: LocalPath) -> None:
        """
        Given: Nothing
        When: Initializing the repository with an inexistent directory
        Then: The directory is created
        """
        workdir = f"{tmpdir}/unexistent_dir"

        result = LocalFileRepository(workdir=workdir)

        assert result.workdir == workdir
        assert os.path.exists(result.workdir)
