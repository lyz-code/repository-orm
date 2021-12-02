import os

from repository_orm import File, load_file_repository

repo = load_file_repository("local:/tmp/file_data")

file_ = File(path="test.txt")
file_._content = "File content"

# Save content in the repository

file_ = repo.save(file_)
assert file_.path == "/tmp/file_data/test.txt"
assert os.path.isfile(file_.path)

# Load the content from the repository
file_ = File(path="test.txt")
file_ = repo.load(file_)
assert file_.content == "File content"

# Remove the file content from the repository
repo.delete(file_)
assert not os.path.isfile("/tmp/file_data/test.txt")
