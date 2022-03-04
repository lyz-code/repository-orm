When modeling the application logic through [Domain Driven
Design](https://lyz-code.github.io/blue-book/architecture/domain_driven_design/),
you usually need the following object types:

* *Value object*: Any domain object that is uniquely identified by the data it
    holds, so it has no conceptual identity. They should be treated as
    immutable. We can still have complex behaviour in value objects.
    In fact, it's common to support operations, for example, mathematical
    operators.

* *Entity*: An object that is not defined by it's attributes, but rather by
    a thread of continuity and it's identity. Unlike values, they have *identity
    equality*. We can change their values, and they are still recognizably the
    same thing.

# Entities

The [Entity][repository_orm.model.Entity] class is based on the
pydantic's `BaseModel` to enforce that they have the `id_` attribute of type
`int`, `str` or `AnyHttpUrl`, used for comparison and hashing of entities.

They also have a private `model_name` property with the name of the model.

If you use integer IDs (which is the default), you don't need to define the
`id_` at object creation. When you add the entity to the repository, it will
populate it.

```python
{! examples/auto_increment_id.py !} # noqa
```

!!! warning "This will only work with `int` ids! For the rest of the cases you
need to give the `id_` yourself."

## Merging entities

Entities have a `merge` method that let's you update it's attributes with
the ones of another entity.

```python
{! examples/merge_entities.py !} # noqa
```

For two entities to be mergeable, they need to belong from the same model and
have the same `id_`. The previous example worked because by default the `id_` is
`-1` until the entity is added to the repository. If you want to check other
attribute to see if the objects are mergeable, probably that attribute should be
the `id_` instead.

If you don't want to propagate some attributes when merging, add them to the
`_skip_on_merge` configuration option of the model:

```python
{! examples/merge_entities_skip_attribute.py !} # noqa
```

# Files

The [File][repository_orm.model.File] class is a special
[Entity][repository_orm.model.Entity] model used to work with computer files.

It has useful attributes like:

* `path`.
* `created_at`.
* `updated_at`.
* `owner`.
* `group`.
* `permissions`.

And methods:

* `basename`.
* `dirname`.
* `extension`.

Until Pydantic `1.9` is released, you need to store the content in the file
using the `_content` attribute, to access the content, you can use `content`
directly.
