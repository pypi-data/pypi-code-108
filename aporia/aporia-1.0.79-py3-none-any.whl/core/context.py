from .config import Config
from .errors import AporiaError
from .event_loop import EventLoop
from .http_client import HttpClient

global_context = None


class Context:
    """Global context."""

    def __init__(
        self,
        http_client: HttpClient,
        event_loop: EventLoop,
        config: Config,
    ):
        """Initializes the context.

        Args:
            http_client: Http client.
            event_loop: Event loop.
            config: Aporia config.
        """
        self.http_client = http_client
        self.event_loop = event_loop
        self.config = config

        self._open_http_client()

    def _open_http_client(self):
        self.event_loop.run_coroutine(self.http_client.open())

    def shutdown(self):
        """Cleans up objects managed by the context."""
        self.event_loop.run_coroutine(self.http_client.close())


def init_context(http_client: HttpClient, event_loop: EventLoop, config: Config):
    """Initializes the global context.

    Args:
        http_client: Http client
        event_loop: Event loop
        config: Configuration
    """
    global global_context

    global_context = Context(http_client=http_client, event_loop=event_loop, config=config)


def reset_context():
    """Resets the global context."""
    global global_context
    if global_context is None:
        raise AporiaError("Aporia was not initialized.")

    global_context.shutdown()
    global_context = None


def get_context() -> Context:
    """Returns the global context."""
    if global_context is None:
        raise AporiaError("Aporia was not initialized.")

    return global_context
