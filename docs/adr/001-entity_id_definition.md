Date: 2021-04-15

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Accepted

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
Right now the `Entity` class has a mandatory `id_` attribute of types `str` or
`int`. That prevents the user to create entities a model level as they are not
aware of the existent entities in the repository.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
We can:

* Assume that the model functions that create the new entities receive the
    new entity id as an argument.
* Change the definition of the `id_` attribute so that it can be set by the
    repository at the moment of adding it to the repository.

I've started using the first in [pydo](https://github.com/lyz-code/pydo) and
found it cumbersome.

The first approximation for the second can be to assume that the `id_` is an
integer, by default is set to a negative value, marking it as invalid, and when
the repository sees it, gets the last id and increments it in a unit.

This can't be easily done if the `id_` is a `str`. So I'm temporarily dropping
support for this types of IDs. If anyone needs them, we can create a workaround
like converting them to an ascii integer and increasing it by one.

If we want more complex objects to be used as ids, we may think of letting the
user specify a callable to increase the ids.

# Decision
<!-- What is the change that we're proposing and/or doing? -->
We're setting a default `id_` value of `-1` on Entities, the repository will
react to these ids, getting the last valid ID and increasing it by one.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
As a side effect, we're temporarily dropping support for `str` `id_` attributes.
