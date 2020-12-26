First make sure you've read the [contributing guidelines](contributing.md).

All repository types are run against the [same
tests](https://github.com/lyz-code/repository-pattern/tree/master/tests/integration/test_repository.py).

Using the awesome library
[pytest-cases](https://lyz-code.github.io/blue-book/coding/python/pytest_cases/),
we were able to separate the test cases from the test functions. The result is
not simple to understand, but bear with me, as once you understand it, you may
love it.

The test cases are in the
[`cases`](https://github.com/lyz-code/repository-pattern/tree/master/tests/cases)
directory below `tests`. There are two files:

* [`entities.py`](https://github.com/lyz-code/repository-pattern/tree/master/tests/cases/entities.py):
    Where we define the different Entity objects to test through the methods of
    the `EntityCases` class.
* [`repositories.py`](https://github.com/lyz-code/repository-pattern/tree/master/tests/cases/repositories.py):
    Where we define the different Repository objects to test through the methods of
    the `RepositoryCases` class.

The Entity cases, return a [factory](https://github.com/lyz-code/repository-pattern/tree/master/tests/factories.py)
defined with
[Factoryboy](https://lyz-code.github.io/blue-book/coding/python/factoryboy)
together with the Entity model, to create arbitrary objects with *real* values
generated through [Faker](https://lyz-code.github.io/blue-book/coding/python/faker/).

The Repository cases are a little more complex, each of them returns a tuple
with the following objects:

* `db`: A storage connection object to run direct queries in the tests.
* `empty_repo`: A repository instance without the schema applied.
* `repo`: A repository instance with the schema applied.
* `repo_tester`: A class to particularize the testing interface to each
    repository.

Each repository needs different assertions to ensure that a functionality works
as expected, this fact makes it really difficult to parametrize the tests. The
solution I've found is to write the tests
Making generic tests for

The Entities to test are defined in the
The interface definition of all repositories is done at the
[AbstractRepository][repository_pattern.adapters.AbstractRepository] class.
