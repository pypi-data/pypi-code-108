class ContextError(Exception):
    """Base class for all Context errors"""


class ContextNotInitializedError(ContextError):
    """Raised when trying to get unitialized context"""


class ClosedContext(ContextError):
    """Raised when trying to use closed context"""

    def __init__(self, exc: Exception, *args: object) -> None:
        self.exc = exc
        super().__init__(*args)


class InvalidState(ContextError):
    """Raised when state is somehow invalid"""


class NoProviderInState(InvalidState):
    """State App does not have provider"""
