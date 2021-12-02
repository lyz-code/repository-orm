The [`TinyDBRepository`][repository_orm.adapters.data.tinydb.TinyDBRepository] is the
implementation of the repository pattern for the local NoSQL
[TinyDB](https://tinydb.readthedocs.io/en/latest/usage.html) database. You can
use it in the early stages of the project where the data schema is yet unstable
and you don't have enough entities to have performance issues.

It stores the persisted [Entities][repository_orm.model.Entity] into
a json file.

Load it with:

```python
from repository_orm import load_repository

repo = load_repository('tinydb://path/to/database.db')
```

# Features

Follow the [overview example](index.md#a-simple-example) to see how to use each
method.

[`add`][repository_orm.adapters.data.tinydb.TinyDBRepository.add]
: Appends the `Entity` object to the default table by translating its attributes
    to a valid json row. If it already exists, it uses the [upsert
    statement](https://tinydb.readthedocs.io/en/latest/usage.html?highlight=upsert#upserting-data)
    to update it's attributes in the table.

[`delete`][repository_orm.adapters.data.tinydb.TinyDBRepository.delete]
: Deletes the `Entity` object from the collection by searching the row that
    matches the object ID.

[`get`][repository_orm.adapters.data.tinydb.TinyDBRepository.get]
: Obtain an `Entity` by extracting the row that matches the ID and build the
    `Entity` object with that data.

[`commit`][repository_orm.adapters.data.tinydb.TinyDBRepository.commit]
: Persist the changes into the database.

[`all`][repository_orm.adapters.data.tinydb.TinyDBRepository.all]
: Obtain all the entities of type `Entity`. Similar to the `get` method but for
    all entities.

[`search`][repository_orm.adapters.data.tinydb.TinyDBRepository.search]
: Obtain the entities whose attributes match one or multiple conditions. We
    create a query with all the desired criteria and then build the entities with
    the obtained data.

[`apply_migrations`][repository_orm.adapters.data.tinydb.TinyDBRepository.apply_migrations]
: We don't yet [support migrations on the
    schema](https://github.com/lyz-code/repository-orm/issues/27), so the models
    should be flexible enough to absorb the changes, or you can code your
    migrations in your program, or even better, help us solve
    [#27](https://github.com/lyz-code/repository-orm/issues/27).

# Internal workings

This section is meant for the people that you to expand the functionality of the
TinyDBRepository. It explains how it works under the hood.

Once the object is initialized with the database url with the format
`tinydb:///path_to_database_file`, an [`TinyDB` object](https://tinydb.readthedocs.io/en/latest/api.html#tinydb.database.TinyDB)
is created in the `db_` attribute, the path to the database is saved in
`database_file` and a empty dictionary of staged changes is created in `staged`.

## Saving entities

All entities are saved in the same default table `_default`, to avoid `id_`
collision, before storing the objects, an `model_type_` attribute is appended
with the lowercase name of the entity class. When retrieving objects with `get`
and `all`, the attribute is deleted.

## Committing

TinyDB doesn't have the concept of transactions, the
[tinyrecord](https://tinydb.readthedocs.io/en/latest/extensions.html#tinyrecord)
plugin does, but you need to run everything in the same context manager, which
doesn't suit our case. So whenever we `add` or `remove` an entity from the
repository, they are stored in the `staged` attribute, and once `commit` is
called, they are persisted into the database.

# References

* [TinyDB documentation](https://tinydb.readthedocs.io/en/latest/api.html#tinydb.database.TinyDB)
