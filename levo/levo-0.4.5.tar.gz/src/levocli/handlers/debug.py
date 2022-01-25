"""
Module to log all the tests in debug mode to a file.
"""
import json

import attr
from click.utils import LazyFile

from .base import EventHandler


@attr.s(slots=True)
class DebugOutputHandler(EventHandler):
    """
    Handler to log test output to a file.
    """

    file_handle: LazyFile = attr.ib()

    def handle_event(self, context, event) -> None:
        stream = self.file_handle.open()
        data = event.asdict()
        stream.write(json.dumps(data))
        stream.write("\n")

    def shutdown(self) -> None:
        self.file_handle.close()
