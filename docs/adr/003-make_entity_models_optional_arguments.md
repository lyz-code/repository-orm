Date: 2021-04-28

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Accepted

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
Some applications need to do operations on all or a subset of entity types in
the repository, for example for the `get`, `search`, `all`, `first` or `last`.

Right now the `entity_model` is a mandatory argument for these methods, that
means that the code calling the repository needs to be aware of all the entity
models inside the repository and call the methods for each of them.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
To solve it, we should change the `entity_model` an argument to a more flexible
type `Union[Type[Entity], List[Type[Entity]], None]`. That change carries some
side effects:

* We need to add logic at repository level to process one, a subset or all the
    entity types.
* Some repositories (tinydb and pypika) used the `entity_model` to build the
    entity, if it's not specified, we need to build the logic that lets them
    build the entities from their data.
* The calls to the methods without specifying the `entity_model` can have
    a worse performance.

## Build the Entities from their data

To build the entities from the data we need those methods to be able to link
that data to a model type, we can either:

* Delegate that functionality to the application using the repository.
* Configure the repositories in a way that we can deduce the model from the data
    stored in itself.

The first solution means that each application will need to implement and
maintain that code, which will lead to more maintenance and duplicated code, but
a simpler repository configuration.

The second solution will mean that the code for the methods is more complex
and/or the repository initialization needs more arguments.

We already store the key information that tells which model does the data belong
to. In the tinydb repo it's stored as an attribute `_model_type`, and in the
pypika repo is stored as tables names. The fake repo doesn't have this problem.

If we initialize the repository with a `models` optional argument, with a list
of the entity models, we can create an internal `models` attribute that holds
a dictionary with the key equal to the value stored in the repos, and the value
the model type. If the user doesn't provide this argument at repo
initialization, it will be supposed that it will give the `entity_model` on each
of the repo methods that require it, otherwise an error will be shown.

## Performance loss

The `entity_model` acted as a filter on the amount of data to perform the
operations, if the user doesn't specify it, the repo needs to work with more
data and therefore be slower. Maybe some of the methods like `all`, `first`, or
`last` will work faster on some repositories based on how they or their
libraries work, but the `get` and `search` will definitely go slower.

In the case of `get` we can mitigate it with an optional callable argument that
can run regexps on the id to select the subset of entity models that contain
id's of that type.

# Decision
<!-- What is the change that we're proposing and/or doing? -->
Change the signatures of the `get`, `search`, `all`, `first` and `last` methods
to accept one, many or no `Entity` subclasses. If none is given, it will assume
that the repository was initialized with the `models` argument, where the user
gives the repo the model of the data it holds.

For the sake of cleanness, we're renaming `entity_models` for `models` in the
function arguments.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
The change makes the library more usable while it retains the performance of the
previous code base.

Two breaking changes were introduced though:

* The argument `entity_model` is no longer the first one for the methods `get`
    and `search`, but the second.
* The argument `database_url` is no longer the first argument in the
    `load_repository` function, but the second, being the first the `models`.
