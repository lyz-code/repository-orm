"""Store the repository-orm exceptions."""


class EntityNotFoundError(Exception):
    """Raised when the search or retrieve of an entity fails."""


class TooManyEntitiesError(Exception):
    """Raised when more entities than expected where found."""


class AutoIncrementError(Exception):
    """Raised when the id_ auto increment repository feature fails."""


class FileContentNotLoadedError(Exception):
    """Raised when trying to access the content of a file that has not been loaded."""
