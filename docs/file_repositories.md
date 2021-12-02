---
title: File Repositories
date: 20211202
author: Lyz
---

File repositories give a common interface to store computer file contents.

They only persist the content of [File][repository_orm.model.File] objects into the
different backends. The metadata however is not stored, so you'll need to use
a [data repository](repositories.md) for that.

# A Simple Example

```python
{! examples/file_repository.py !} # noqa
```

# Usage

The different repositories share the next operations:

`load`
: Load the content of the file from the persistence system.

`save`
: Save the content of the file into the persistence system.

`delete`
: Delete the file from the persistence system.

# Repositories

To change the repository you only need to change the url passed to
`load_file_repository`. We have the next repositories:

* [LocalFileRepository](local_file_repository.md): stores the file contents in
    the local file system.
