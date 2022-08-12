[![Actions Status](https://github.com/lyz-code/repository-orm/workflows/Tests/badge.svg)](https://github.com/lyz-code/repository-orm/actions)
[![Actions Status](https://github.com/lyz-code/repository-orm/workflows/Build/badge.svg)](https://github.com/lyz-code/repository-orm/actions)
[![Coverage Status](https://coveralls.io/repos/github/lyz-code/repository-orm/badge.svg?branch=main)](https://coveralls.io/github/lyz-code/repository-orm?branch=main)

Library to persist [Pydantic](https://pydantic-docs.helpmanual.io/) models into
different storage backends following the [repository
pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/).

# Installing

```bash
pip install repository-orm
```

# A Simple Example

```python
{! examples/simple-example.py !}
```

# Repository pattern theory

[The repository
pattern](https://www.cosmicpython.com/book/chapter_02_repository.html) is an
abstraction over persistent storage, allowing you to decouple the model layer
from the data layer. It hides the boring details of data access by pretending
that all of our data is in memory.

It has the following advantages:

* Give a simple interface, which you control, between persistent storage and
    our domain model.
* It's easy to make a fake version of the repository for unit testing, or to
    swap out different storage solutions, because the model is fully decoupled
    from the infrastructure.
* Writing the domain model before thinking about persistence helps focus on
    the problem at hand. If we need to change our approach, we can do that in
    our model, without needing to worry about foreign keys or migrations until
    later.
* Our database schema is simple because we have complete control over how
    we map our object to tables.
* Speeds up and makes more clean the business logic tests.
* It's easy to implement.

But the following disadvantages:

* An ORM already buys you some decoupling. Changing foreign keys might be hard,
    but it should be pretty easy to swap between MySQL and Postres if you ever
    need to.
* Maintaining ORM mappings by hand requires extra work and extra code.
* An extra layer of abstraction is introduced, and although we may hope it will
    reduce complexity overall, it does add complexity locally. Furthermore it
    adds the *WTF factor* for Python programmers who've never seen this pattern
    before.

*repository-orm* aims to mitigate the last ones by:

* Supplying classes that already have the common operations for different
    storage solutions.
* Supplying test classes and fixtures so extending the provided repositories is
    easy.

# Repositories

There are two kinds of repositories:

* [*Data repositories*](repositories.md): Give a common interface to store the
    models in databases.
* [*File repositories*](file_repositories.md): Give a common interface to store
    computer file contents.

# Projects using `repository-orm`

If you want to see the library being used in a simple project, check
[pynbox](https://github.com/lyz-code/pynbox) code. Other projects using
`repository-orm` are:

* [clinv](https://github.com/lyz-code/clinv): A DevSecOps command line asset
    inventory tool.
* [pydo](https://lyz-code.github.io/pydo/): A free software command line task
    manager built in Python.

If you use the library and want to be listed here, [open an
issue](https://github.com/lyz-code/repository-orm/issues/new/choose).

# References

As most open sourced programs, `repository-orm` is standing on the shoulders of
giants, namely:

[pydantic](https://pydantic-docs.helpmanual.io/)
: Used for the [Entities](models.md#entities) definition.

[DeepDiff](https://deepdiff.readthedocs.io)
: Used to search strings in complex objects in the
    [FakeRepository](fake_repository.md).

[TinyDB](https://tinydb.readthedocs.io/en/latest/usage.html)
: Used to interact with the NoSQL database in the
    [TinyDBRepository](tinydb_repository.md)

[Pypika](https://pypika.readthedocs.io/en/latest/)
: Used to build the SQL queries in the [PypikaRepository](pypika_repository.md).

[Yoyo](https://ollycope.com/software/yoyo/latest)
: Used to manage the schema changes of the
    [PypikaRepository](pypika_repository.md).

[Pytest](https://docs.pytest.org/en/latest)
: Testing framework, enhanced by the awesome
    [pytest-cases](https://smarie.github.io/python-pytest-cases/) library that made
    the parametrization of the tests a lovely experience.

[Mypy](https://mypy.readthedocs.io/en/stable/)
: Python static type checker.

[Flakeheaven](https://github.com/flakeheaven/flakeheaven)
: Python linter with [lots of
    checks](https://lyz-code.github.io/blue-book/devops/flakeheaven#plugins).

[Black](https://black.readthedocs.io/en/stable/)
: Python formatter to keep a nice style without effort.

[Autoimport](https://lyz-code.github.io/autoimport)
: Python formatter to automatically fix wrong import statements.

[isort](https://github.com/timothycrosley/isort)
: Python formatter to order the import statements.

[PDM](https://pdm.fming.dev/)
: Command line tool to manage the dependencies.

[Mkdocs](https://www.mkdocs.org/)
: To build this documentation site, with the
[Material theme](https://squidfunk.github.io/mkdocs-material).

[Safety](https://github.com/pyupio/safety)
: To check the installed dependencies for known security vulnerabilities.

[Bandit](https://bandit.readthedocs.io/en/latest/)
: To finds common security issues in Python code.

[Yamlfix](https://github.com/lyz-code/yamlfix)
: YAML fixer.

# Contributing

For guidance on setting up a development environment, and how to make
a contribution to *repository-orm*, see [Contributing to
repository-orm](https://lyz-code.github.io/repository-orm/contributing).
