[![Actions Status](https://github.com/lyz-code/repository-pattern/workflows/Tests/badge.svg)](https://github.com/lyz-code/repository-pattern/actions)
[![Actions Status](https://github.com/lyz-code/repository-pattern/workflows/Build/badge.svg)](https://github.com/lyz-code/repository-pattern/actions)
[![Coverage Status](https://coveralls.io/repos/github/lyz-code/repository-pattern/badge.svg?branch=master)](https://coveralls.io/github/lyz-code/repository-pattern?branch=master)

Library to ease the implementation of the [repository
pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/)
in python projects.

[The repository
pattern](https://www.cosmicpython.com/book/chapter_02_repository.html) is an
abstraction over persistent storage, allowing us to decouple our model layer
from the data layer. It hides the boring details of data access by pretending
that all of our data is in memory.

It has the following advantages:

* We get a simple interface, which we control, between persistent storage and
    our domain model.
* It's easy to make a fake version of the repository for unit testing, or to
    swap out different storage solutions, because we've fully decoupled the
    model from infrastructure concerns.
* Writing the domain model before thinking about persistence helps us focus on
    the business problem at hand. If we need to change our approach, we can do
    that in our model, without needing to worry about foreign keys or migrations
    until later.
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

*repository-pattern* aims to mitigate the last ones by:

* Supplying classes that already have the common operations for different
    storage solutions.
* Supplying test classes and fixtures so extending the provided repositories is
    easy.

# Installing

```bash
pip install repository-pattern
```

# A Simple Example

```python
{! examples/simple-example.py !} # noqa
```

# Usage

The different repositories share the following operations:

`add`
: Add an `Entity` object to the repository.

`delete`
: Remove an `Entity` object form the repository.

`get`
: Obtain an `Entity` from the repository by it's ID.

`commit`
: Persist the changes into the repository.

`all`
: Obtain all the entities of type `Entity` from the repository.

`search`
: Obtain the entities whose attributes match a condition.

`apply_migrations`
: Run the migrations of the repository schema.

!!! note ""
    Changes in the repository aren't persisted until you run `repo.commit()`.

# References

As most open sourced programs, `repository_pattern` is standing on the shoulders of
giants, namely:

[pydantic](https://pydantic-docs.helpmanual.io/)
: Used for the [Entities](models.md#entities) definition.

[DeepDiff](https://deepdiff.readthedocs.io)
: Used to search strings in complex objects in the
    [FakeRepository](fake_repository.md).

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

[Flakehell](https://github.com/life4/flakehell)
: Python linter with [lots of
    checks](https://lyz-code.github.io/blue-book/devops/flakehell/#plugins).

[Black](https://black.readthedocs.io/en/stable/)
: Python formatter to keep a nice style without effort.

[Autoimport](https://github.com/lyz-code/autoimport)
: Python formatter to automatically fix wrong import statements.

[isort](https://github.com/timothycrosley/isort)
: Python formatter to order the import statements.

[Pip-tools](https://github.com/jazzband/pip-tools)
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
a contribution to *repository-pattern*, see [Contributing to
repository-pattern](https://lyz-code.github.io/repository-pattern/contributing).
