Testing your code is a hated but good practice. Repository ORM tries to make
your testing experience less cumbersome.

You can use different strategies depending on the level of testing. For unit and
integration tests the [`FakeRepository`](fake_repository.md) may be your best
option, for end-to-end ones, I'd use [`TinyDBRepository`](tinydb_repository.md).

# Unit and integration tests

[Unit tests](https://en.wikipedia.org/wiki/Unit_testing) are meant to test
individual units of code, for example, a function or a method of a class. You'll
probably use them to test your
[models](https://lyz-code.github.io/blue-book/architecture/domain_driven_design/#domain-modeling)
or
[services](https://lyz-code.github.io/blue-book/architecture/service_layer_pattern/).

```python
{! examples/unit_test_fake_repository.py !} # noqa
```

# End-to-end tests

End-to-end tests evaluate the whole functionality of the program from the eyes
of the user. For example, testing a command line or the API endpoint. Usually
the program loads the repository from storage at start time, which means that
the FakeRepository can't be used.

We're going to create a
[click](https://lyz-code.github.io/blue-book/coding/python/click/) command line
program called `greet` that once it's called, it will return the first author in
the repository. It's a little bit more complex but bare with me.

```python
{! examples/e2e_test.py !} # noqa
```

First we define the fixtures, we start with `db_tinydb` that uses the pytest's
[`tmp_path`](https://lyz-code.github.io/blue-book/coding/python/pytest/#the-tmp_path-fixture)
fixture to create a random temporal directory and then sets the database url.
The `repo` fixture uses that database url to create a `TinyDBRepository`
instance.

The model `Author` and service `create_greeting` are similar to the previous
section.

The entrypoint is where we define the command line interface, in this case the
command is going to be called `greet` and it's going to accept an argument
called `database_url`, it will initialize the repository and use the
`create_greeting` to show the message to the user through the terminal.

To test this code, we first need to add an Author, so the function can look for
it. We do it in the first three lines of `test_greetings`. Then we initialize
the
[`runner`](https://lyz-code.github.io/blue-book/coding/python/click/#testing-click-applications)
which simulates a command line call, and we make sure that the program exited
well, and gave the output we expected.
