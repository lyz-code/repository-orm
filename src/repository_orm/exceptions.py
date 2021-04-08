"""
Module to store the repository-orm exceptions.

Exceptions:
    EntityNotFoundError
"""


class EntityNotFoundError(Exception):
    """Raised when the search or retrieve of an entity fails."""
