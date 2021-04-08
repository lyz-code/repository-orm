# Repository ORM

[![Actions Status](https://github.com/lyz-code/repository-orm/workflows/Tests/badge.svg)](https://github.com/lyz-code/repository-orm/actions)
[![Actions Status](https://github.com/lyz-code/repository-orm/workflows/Build/badge.svg)](https://github.com/lyz-code/repository-orm/actions)
[![Coverage Status](https://coveralls.io/repos/github/lyz-code/repository-orm/badge.svg?branch=master)](https://coveralls.io/github/lyz-code/repository-orm?branch=master)

Library to ease the implementation of the [repository
pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/).

One of the disadvantages of using the repository pattern is that developers need
to add and maintain a new abstraction to manage how to persist their models
in the storage. *repository-orm* aims to mitigate this inconvenient by:

* Supplying classes that already have the common operations for different
    storage solutions.
* Supplying test classes and fixtures so extending the provided repositories is
    easy.

## Help

See [documentation](https://lyz-code.github.io/repository-orm) for more details.

## Installing

```bash
pip install repository-orm
```

## Contributing

For guidance on setting up a development environment, and how to make
a contribution to *repository-orm*, see [Contributing to
repository-orm](https://lyz-code.github.io/repository-orm/contributing).

## License

GPLv3
