Date: 2022-08-23

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We currently use Abstract classes to define the interface of the adapters, we
also rely heavily on class inheritance. After reading [hynek's subclassing in
Python Redux](https://hynek.me/articles/python-subclassing-redux/) I think using
composition and Protocols will make the code cleaner, easier to read and to
maintain.

For example, we have an Abstract class `Repository` that defines both the
interface and is used to share code between the implementations of the
repositories. So we're mixing two types of subclassing, which is not a good
idea. It's showing that there is some functionality that is common to all
repositories and the implementation of each of them has to do only with the
storage backend. To tell apart the repository methods and the implementations
we're using an underscore, for example `def add(...)` is the repository that
calls the `def _add(...)` that needs to be implemented by each of the
particularizations. This is hard to read and understand.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

## Use the Storage Protocol

The idea is to create a `Repository` class that holds all the functionality of
a repository, and extracting the storage functionality of each storage
particularization to a `store` attribute whose interface is defined by
a `Protocol`:

```python
class Repository:
    store: Storage
```

```python
class Storage(Protocol):

    def add(self, entity: EntityT) -> None: ...
    def delete(self, entity: EntityT) -> None: ...
    def get(self,
        value: EntityAttr,
        model: Type[EntityT],
        attribute: str = "id_",
    ) -> List[EntityT]: ...
    def all(self, model: Type[EntityT]) -> List[EntityT]: ...
    def commit(self) -> None: ...
    def search(
        self,
        fields: Dict[str, EntityAttr],
        model: Type[EntityT],
    ) -> List[EntityT]: ...
    def apply_migrations(self, migrations_directory: str) -> None: ...
    def last(self, model:Type[EntityT]) -> EntityT: ...
    def first(self, model:Type[EntityT]) -> EntityT: ...
    def close(self) -> None: ...

    @property
    def is_closed(self) -> bool: ...

    def empty(self) -> None: ...
```

Where `EntityAttr` is each of the supported entity attributes.

### Implementation

#### Entrypoint

I've thought of instead of using `load_repository` as an entrypoint, we could
directly use `Repository('tinydb://...')` but then we'd need to import all the
adapters into `model.py` which I think it's breaking the independence between
components. Furthermore, if we keep the `load_repository` function we don't
change the entrypoint for existent users.

#### Storage names

We can take the chance to change the name of the storages from the technology
they use to the backend they use. I think this is more clear to users, which
they won't care if we use TinyDB or other library to manage the resulting JSON
but instead that the data is stored in JSON, therefore the next changes will be
done:

* `FakeRepository` -> `MemoryStore`
* `TinyDBRepository` -> `JSONStore`
* `PypikaRepository` -> `SQLStore`




# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
