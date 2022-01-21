from typing import Optional

import attr
from levo_commons.events import Event


@attr.s()
class CorruptedConfigFile(Exception):
    """Levo's config file appears to be corrupted."""

    path: str = attr.ib()


@attr.s()
class UnexpectedEndOfStream(Exception):
    """Event steam exhausted without yielding a terminal event."""

    last_event: Optional[Event] = attr.ib()


class LevoCustomError(Exception):
    """Customized exception messages"""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message
        else:
            return "LevoCustomError has been raised!"
