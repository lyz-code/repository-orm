Date: 2022-03-10

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Accepted

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
Right now we raise an `EntityNotFoundError` exception if `search`
returns no results, which forces the user to catch this exception when it makes
more sense to return an empty list as these methods are usually used on loops.

We're also having some issues with the types of the return values of these
methods as we allowed them to be of type `Union[Type[Entity],
List[Type[Entity]], None]` since
[003](003-make_entity_models_optional_arguments.md), both when writing the code
as the type hints are difficult to write and debug and also when doing
operations on the returned objects, as the returned list contains objects with
different models that as they have different attributes and objects they need to
be dealt differently. This last point means that the user has to split the
results using `isinstance` at some point.

Using many models in `get` is only a good idea when you're sure that id's are
unique across all models, that way you can do `repo.get(id, models)` and get the
only entity that matches, when we initialized the repository with the available
models, you could go even further and only use `repo.get(id)`. This has the next
disadvantages:

* The current code requires that each repository needs to implement the logic
    of:
    * Dealing with many models, which we want to remove. It could be delegated
        to `get` at `abstract.py` level and make `_get` only accept one model.
    * What happens when more than one entity is found. This could be mitigated if
        we change the signature of `_get` to always return a `List[Entity]` and do
        the checking at `get` level in `abstract.py`.
* You don't know the type of the returned object at type checker level. It's
    a nuisance but not critical, as it should be acceptable if you're using
    `get` this way.

The `last` and `first` methods are used over the `all` method not over the
`search` which would be useful too.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

## Return a list instead of exception

`search` will return an empty list if there are no results instead of
an `EntityNotFoundError` exception.

## Only allow one model in search and all

We could revert [003](003-make_entity_models_optional_arguments.md) and only
allow one model in `search` and `all` but that will mean that the context of
that ADR won't be met anymore which was that some applications need to do
operations on all or a subset of entity types. They will then be forced to run
the desired method once for each entity type which has the next disadvantages:

* The user has to write more code. Which may not true, as even though you
    have to run `repo.search` and `repo.all` more than once, right now you also
    have to write additional code to tell apart the returned objects. This last
    statement may not be true if the user has asked for a group of entities that
    share some common attributes with whom it wants to work with.

    After migrating some code I've seen that at user level the change is from:

    ```python
    active_resources = repo.search({"state": "active"}, models)
    ```

    To:

    ```python
    active_resources = [
        entity for model in models for entity in repo.search({"state": "active"}, model)
    ]
    ```

    Which I think it's assumable given that it can be considered a corner case.

* Instead of running everything on a query, many will be done. The potential
    downside of that is performance loss, but in reality:

    * The pypika and fake repos are already doing many queries.
    * The tinydb repo is doing everything in one query but then from the
        gathered data it has to go model by model building the ones that match.

    So probably we won't have any performance loss.

And the next advantages:

* We've introduced a great deal of complexity on
    [003](003-make_entity_models_optional_arguments.md) both on functions and
    type hints, removing them will improve maintainability and peace of mind
    when coding.

## Only allow one model in get

If we only allow one model in `get` we'll remove complexity in terms of:

* No need to loop over the models.

The management of the case of more than one entity found has to be still
managed, as we can only enforce this case in pypika, fake and tinydb doesn't
have that kind of constrain at database level.

The case that it makes sense to keep the feature is a corner case as most of
databases use integer ids. And if you've made the ids unique between
models it should be straight forward to make a function that gives you the model
for that ID, or you're free to iterate over the models and suppress the
`EntityNotFoundError` exception.

Therefore it makes no sense to keep complexity for a corner case.

## Leave last and first as they are

Even though it's true that they could be used on the `search` result, let's be
honest, using `[0]` and `[-1]` is not that difficult, and if there are no
elements it will return an `IndexError` a common used exception. As `first` and
`last` are already coded and it's easy to maintain I'll leave them as they are
and assume that `search` won't have them.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

* Revert the changes of [003](003-make_entity_models_optional_arguments.md).
* `search` will return an empty list if there are no results instead of
    an `EntityNotFoundError` exception.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->

Pros:

* More maintainable code.
    * Less complexity in the data adapters.
    * Less problems with the type hints.

* Remove the model conflicts of `get`

Cons:

* Users will need to update their code as the signature of `get`, `all`,
    `search`, `first`, and `last` will change.

The users will have 3 months to do the changes.
