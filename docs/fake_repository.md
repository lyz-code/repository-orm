The [`FakeRepository`][repository_pattern.adapters.fake.FakeRepository] is the
simplest implementation of the repository pattern, meant to be used for the
tests and early phases of development.

It stores the persisted [Entities][repository_pattern.model.Entity] in the
`entities` object attribute in a dictionary where the keys are the Entity class
and the values are list of that Entity objects. When you try to make changes to
the repository, the actual `entities` dictionary is copied to the `new_entities`
attribute. The changes are made on that new attribute and once you use the
`commit` method, they get copied back to the `entities` attribute.

# Features

Follow the [overview example](index.md#a-simple-example) to see how to use each
method.

[`add`][repository_pattern.adapters.fake.FakeRepository.add]
: Appends the `Entity` object to the `new_entities` attribute.

[`delete`][repository_pattern.adapters.fake.FakeRepository.delete]
: Deletes the `Entity` object from the `new_entities` attribute.

[`get`][repository_pattern.adapters.fake.FakeRepository.get]
: Obtain an `Entity` from the `entities` attribute by it's ID.

[`commit`][repository_pattern.adapters.fake.FakeRepository.commit]
: Persist the changes of `new_entities` into `entities`, clearing up
    `new_entities` afterwards.

[`all`][repository_pattern.adapters.fake.FakeRepository.all]
: Obtain all the entities of type `Entity` from the `entities` attribute.

[`search`][repository_pattern.adapters.fake.FakeRepository.search]
: Obtain the entities whose attributes match one or multiple conditions.

    We use [DeepDiff's](https://deepdiff.readthedocs.io)
    [grep](https://zepworks.com/deepdiff/5.0.0/dsearch.html#deepdiff.search.grep)
    to search for the entities that have the value we're searching for and then
    we search if the key of those entities match the one we're searching for.

[`apply_migrations`][repository_pattern.adapters.fake.FakeRepository.apply_migrations]
: Run the migrations of the repository schema.

    As the fake repository doesn't have any schema this method does nothing.

# Simulating errors

## ConnectionError

To simulate a connection error to the database, initialize the object with the
`wrong_database_url` string.
