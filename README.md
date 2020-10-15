# Repository Pattern

[![Actions Status](https://github.com/lyz-code/repository-pattern/workflows/Python%20package/badge.svg)](https://github.com/lyz-code/repository-pattern/actions)

Library to ease the implementation of the [repository
pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/).

One of the disadvantages of using the repository pattern is that developers need
to add and maintain a new abstraction to manage how to persist their models
in the storage. *repository-pattern* aims to mitigate this inconvenient by:

* Supplying classes that already have the common operations for different
    storage solutions.
* Supplying test classes and fixtures so extending the provided repositories is
    easy.

## Help

See [documentation](https://lyz-code.github.io/repository-pattern) for more
details.

## Installing

```bash
pip install repository-pattern
```

## Contributing

For guidance on setting up a development environment and how to make
a contribution to *repository-pattern*, see [Contributing to
repository-pattern](https://lyz-code.github.io/repository_pattern/contributing).

## License

GPLv3
