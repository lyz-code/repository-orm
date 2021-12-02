The [`PypikaRepository`][repository_orm.adapters.data.pypika.PypikaRepository] is the
implementation of the repository pattern for the relational databases. It's
meant for the stages of the project where the schema is more stable and you need
the improved performance of these types of databases.

It stores the persisted [Entities][repository_orm.model.Entity] into
a SQLite database tables ([Mysql support will
come in the future](https://github.com/lyz-code/repository-orm/issues/1)).

It uses the [Pypika](https://pypika.readthedocs.io/en/latest/) [query
builder](https://lyz-code.github.io/blue-book/architecture/orm_builder_query_or_raw_sql/#query-builder)
to generate the raw SQL statements and then sends them to the database through
an [sqlite3](https://lyz-code.github.io/blue-book/sqlite3/) connection. If
you're wondering why we don't want to use
[SQLAlchemy](https://lyz-code.github.io/blue-book/coding/python/sqlalchemy) or
raw sql statements, check
[this](https://lyz-code.github.io/blue-book/architecture/orm_builder_query_or_raw_sql/)
article.

Load it with:

```python
from repository_orm import load_repository

repo = load_repository('sqlite://path/to/database.db')
```

# Database schema

The repository assumes there is a specific schema, where the table names are
the same as the [Entity][repository_orm.model.Entity] clases in lowercase,
and the columns are called as the attributes. All tables must have an `id`
column. Following the [overview example](index.md#a-simple-example), the
database should contain one table called `author` with the columns `id`,
`first_name`, `last_name` and `country`.

For it's simplicity, we've decide to use
[yoyo](https://lyz-code.github.io/blue-book/coding/python/yoyo) to maintain the
schema. This means that you need to write the migration scripts yourself :(.
Look at the [migration
script](https://github.com/lyz-code/repository-orm/tree/master/tests/migrations/pypika/0001_initial_schema.py)
of the tests if you need an example.

# Features

Follow the [overview example](index.md#a-simple-example) to see how to use each
method.

[`add`][repository_orm.adapters.data.pypika.PypikaRepository.add]
: Appends the `Entity` object to its table by translating its attributes to the
    columns. If it already exists, use the [upsert
    statement](https://www.sqlite.org/lang_UPSERT.html) to update it's
    attributes in the table.

[`delete`][repository_orm.adapters.data.pypika.PypikaRepository.delete]
: Deletes the `Entity` object from its table by searching the row that matches
    the object ID.

[`get`][repository_orm.adapters.data.pypika.PypikaRepository.get]
: Obtain an `Entity` by extracting the row that matches the ID and build the
    `Entity` object with that data.

[`commit`][repository_orm.adapters.data.pypika.PypikaRepository.commit]
: Persist the changes into the database.

[`all`][repository_orm.adapters.data.pypika.PypikaRepository.all]
: Obtain all the entities of type `Entity`. Similar to the `get` method but for
    all entities.

[`search`][repository_orm.adapters.data.pypika.PypikaRepository.search]
: Obtain the entities whose attributes match one or multiple conditions. We
    create a query with all the desired criteria and then build the entities with
    the obtained data.

[`apply_migrations`][repository_orm.adapters.data.pypika.PypikaRepository.apply_migrations]
: Run the migrations of the repository schema. Creates a yoyo connection and
    runs all the scripts in the `migrations` directory.

# Internal workings

This section is meant for the people that you to expand the functionality of the
PypikaRepository. It explains how it works under the hood.

Once the object is initialized with the database url with the format
`sqlite:///path_to_database_file`, an `sqlite3`
[`Connection`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection)
object is saved in the `connection` attribute, and a first
[`Cursor`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor) is
saved to the `cursor` attribute.

If you need to execute new queries, use the `_execute` method, it accepts
a Pypika `Query` object. To extract the Pypika `Table` from an identity object, use the
`_table` static method, or the `_table_model` if you use an identity class
instead.

!!! warning ""
    Keep in mind that if you use the internal methods, like `_execute`, in your
    program, you're breaking the [Liskov substitution
    principle](https://lyz-code.github.io/blue-book/architecture/solid/#liskov-substitutionlsp)
    and you won't be able to switch to other type of repository.

    If you need a functionality that is not implemented, create a public method
    and define it for the repositories that you want to use. Take a look at the
    [contributing](contributing.md) page, and think of adding it to the library.

There is also the `_build_entities` method that accepts an `Entity` class and
a `Query` and returns a list of the entities built from the data of the query.

# References

* [Pypika documentation](https://pypika.readthedocs.io/en/latest/index.html)
* [Yoyo documentation](https://ollycope.com/software/yoyo/latest)
