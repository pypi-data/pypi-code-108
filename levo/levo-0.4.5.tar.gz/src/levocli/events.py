from typing import Any, Callable, Generator, List

import attr
from levo_commons.events import Event, Interrupted

from .errors import UnexpectedEndOfStream
from .handlers import EventHandler
from .logger import get_logger

log = get_logger(__name__)


@attr.s(slots=True)
class EventStream:
    """Levo event stream.

    Provides an API to control the execution flow.
    """

    inner: Any = attr.ib()
    map: Callable[[Any], Event] = attr.ib()

    def __next__(self) -> Event:
        event = next(self.inner)
        return self.map(event)

    def __iter__(self) -> Generator[Event, None, None]:
        for event in self.inner:
            yield self.map(event)

    def stop(self) -> None:
        raise NotImplementedError

    def finish(self) -> Event:
        """Stop the event stream & return the last event."""
        self.stop()
        return next(self)


def handle(
    handlers: List[EventHandler],
    event_stream: EventStream,
    context,
):
    """Execute handlers against the given event stream.

    The implementation is generic for any handler & event stream.
    """

    def shutdown() -> None:
        for _handler in handlers:
            log.debug(f"Shutting down the handler: {_handler.get_name()}")
            _handler.shutdown()

    event = None
    try:
        for event in event_stream:
            log.debug("Received the event.", event_data=event)
            for handler in handlers:
                handler.handle_event(context, event)

            if event.is_terminal or isinstance(event, Interrupted):
                break
    except KeyboardInterrupt:
        return handle_interrupt(handlers, event_stream, context)
    finally:
        shutdown()
    if event is not None and (event.is_terminal or isinstance(event, Interrupted)):
        return event
    raise UnexpectedEndOfStream(event)


def handle_interrupt(handlers: List[EventHandler], event_stream: EventStream, context):
    # User might interrupt the process and how we handle the case depends on where it has happened:
    #   - Inside the event stream. By convention, it is converted to `Interrupted` event and handled by handlers;
    #   - Inside a handler. It is likely for handlers that block on the current thread with non-trivial tasks.
    # If this `except` clause is executed, then it is the latter case.
    # Note that we don't handle another interrupt that may happen below - assume the user wants a hard shutdown.
    interrupted = Interrupted()
    for handler in handlers:
        handler.handle_event(context, interrupted)
    finished = event_stream.finish()
    for handler in handlers:
        handler.handle_event(context, finished)
    return finished
