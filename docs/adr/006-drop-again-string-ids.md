Date: 2022-06-08

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
Supporting string IDs has made the source code more complex because it:

* We have to handle each case `str`, and `int` independently.
* The signature of the functions is more complex.
* `str` ids don't have the auto-increment feature.

On the other hand, string IDs are useful when the identifying property of
an entity is a string. This gives two benefits:

* You can `repo.get` by that element.
* You can't have two elements with the same attribute.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
We can try to simplify the ID signature to `int` only while giving the users
tools so that they don't loose the benefits of the `str` IDs.

* We already added an optional argument to `repo.get` so that you can get by
    another attribute. This way it would be easy to spot what attributes would
    need their own index.
* We'll need to support uniqueness of entities based on an attribute other than
    `id_`. (We need to refine this idea.)

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
