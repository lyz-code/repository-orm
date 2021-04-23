Date: 2021-04-16

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Accepted

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
In version 0.3.0 we dropped support for string ids, and that was a bad decision,
as there are already projects that use it.

The reason of deprecation was because the new feature to auto increment the ID of
the entities that hadn't set it, wasn't "easy" to implement for strings.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
Restore the support for string ids, but without the auto increment feature. If
you're using string ids is probably because you have an id generator or you're
getting them from outside sources.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
