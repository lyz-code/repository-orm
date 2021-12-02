The [`LocalFileRepository`][repository_orm.adapters.file.LocalFileRepository] stores the file contents in the local file system.

It stores the [File][repository_orm.model.File]'s contents in a file in the
local file system.

Imagine you want to save the contents in `/srv/file_data`, you'll then
initialize the repository with:

```python
from repository_orm import load_file_repository

repo = load_file_repository("local:/srv/file_data")
```

# Features

Follow the [overview example](file_repositories.md#a-simple-example) to see how to use each
method.

[`load`][repository_orm.adapters.file.local_file.LocalFileRepository.load]
: Load the content of the File from a file in the local filesystem.

[`save`][repository_orm.adapters.file.local_file.LocalFileRepository.save]
: Save the content of the File to a file in the local filesystem.

[`delete`][repository_orm.adapters.file.local_file.LocalFileRepository.delete]
: Delete the file from the local filesystem.
