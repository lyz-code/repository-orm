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

Using that type in `get` is a bad idea too, as many entities may have the same
`id_`, and when you `get` you just want one entity, otherwise you'd use
`search`.

The `last` and `first` methods are used over the `all` method not over the
`search` which would be useful too.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

## Return a list instead of exception

`search` will return an empty list if there are no results instead of
an `EntityNotFoundError` exception.

## Only allow one model

We could revert [003](003-make_entity_models_optional_arguments.md) and only
allow one model in `search` and `all` but that will mean that the context of
that ADR won't be met anymore which was that some applications need to do
operations on all or a subset of entity types. They will then be forced to run
the desired method once for each entity type which has the next disadvantages:

* The user has to write more code. Which is not true, as even though you truly
    have to run `repo.search` and `repo.all` more than once, right now you also
    have to write additional code to tell apart the returned objects.
* Instead of running everything on a query, many will be done. The potential
    downside of that is performance loss, but in reality the current
    implementation is already doing many queries as it's not able to do
    everything at once.

And the next advantages:

* We've introduced a great deal of complexity on
    [003](003-make_entity_models_optional_arguments.md) both on functions and
    type hints, removing them will improve maintainability and peace of mind
    when coding.
* Remove conflicts on `get`.

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
