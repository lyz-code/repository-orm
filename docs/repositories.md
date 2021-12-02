---
title: Data Repositories
date: 20211202
author: Lyz
---

Data repositories give a common interface to store the models in databases.

# Usage

The different repositories share the next operations:

`add`
: Add an `Entity` object to the repository, if it already exist, it updates the
    stored attributes.

`delete`
: Remove an `Entity` object form the repository.

`get`
: Obtain an `Entity` from the repository by it's ID.

`commit`
: Persist the changes into the repository.

`all`
: Get all the entities of a type or types from the repository. If no argument is
given, it will return all entities.

`search`
: Get the entities whose attributes match a condition or regular expression.

`first`
: Get the first entity of a type or types of the repository. If no argument is
given, it will return the first of any type of entity.

`last`
: Get the last entity of a type or types of the repository. If no argument is
given, it will return the first of any type of entity.

`apply_migrations`
: Run the migrations of the repository schema.

!!! note ""
    Changes in the repository aren't persisted until you run `repo.commit()`.

# Repositories

To change the repository you only need to change the url passed to
`load_repository`. We have the next repositories:

* [FakeRepository](fake_repository.md): is the simplest implementation of the
    repository pattern, meant to be used for the tests and early phases of
    development.
* [TinyDBRepository](tinydb_repository.md): is the implementation of the
    repository pattern for the local NoSQL
    [TinyDB](https://tinydb.readthedocs.io/en/latest/usage.html) database. You
    can use it in the early stages of the project where the data schema is yet
    unstable and you don't have enough entities to have performance issues.
* [PypikaRepository](pypika_repository.md): is the implementation of the
    repository pattern for the relational databases. It's meant for the stages
    of the project where the schema is more stable and you need the improved
    performance of these types of databases.
