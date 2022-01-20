# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS Library monitoring system."""
import time
import sys
import signal
from contextlib import contextmanager
from .config import Config
from .events import Events
from .debug import Debug
from .exceptions import (
    AliveMessageMissing,
    PublisherNotStarted,
    SubscriberDied,
    PublisherDied,
)


class Monitor:
    """Monitor processes, health check and send status messages."""

    announcement = None

    def __init__(self):
        """Initialize debug and config instances."""
        self.debug = Debug()
        self.config = Config()

    def __del__(self):
        """Delete config reference."""
        self.config = None

    def keep_alive(self, alive_message=None):
        """Keep subscriber and publishers alive forever.

        :param alive_message: Body of the announcement published event.
        :type alive_message: str
        """
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        if not self.debug.disable_monitor_announce and alive_message is None:
            raise AliveMessageMissing
        with self.announce(alive_message):
            while True:
                time.sleep(0.1)
                try:
                    self.check_publisher_liveness()
                except PublisherDied:
                    self.probe()
                    raise
                try:
                    self.check_subscriber_liveness()
                except SubscriberDied:
                    self.probe()
                    raise

    def probe(self):
        """Probe the environment for debug data."""
        self.config.dump()

    @contextmanager
    def announce(self, body):
        """Announce the status of this service if 'with_announcement' is True.

        :param body: Body of the announcement event.
        :type body: str
        """
        if self.debug.disable_monitor_announce:
            yield

        publisher = self.config.get("publisher")
        if publisher is None:
            raise PublisherNotStarted

        events = Events(publisher)
        self.announcement = events.send_announcement_published(
            f"{self.config.get('service_name')} is up and running.", body, "MINOR"
        )
        try:
            yield
        except Exception as exception:  # pylint:disable=broad-except
            events.send_announcement_published(
                f"{self.config.get('service_name')} stopped running unexpectedly.",
                f"{exception}\n",
                "CRITICAL",
                links={"modified_announcement": self.announcement},
            )

    def _handle_shutdown(self, *_, **__):
        """Signal handler for SIGINT and SIGTERM.

        Send an announcement that the service has shut down, if 'with_announcement' is set.
        sys.exit(0) will exit this service cleanly, this will make sure that kubernetes does not
        restart the service.
        """
        if not self.debug.disable_monitor_announce:
            publisher = self.config.get("publisher")
            if publisher is None:
                raise PublisherNotStarted

            events = Events(publisher)
            events.send_announcement_published(
                f"{self.config.get('service_name')} was shut down.",
                (
                    f"{self.config.get('service_name')} has stopped sending and"
                    "listening to Eiffel events."
                ),
                "CLOSED",
                links={"modified_announcement": self.announcement},
            )
        sys.exit(0)

    def check_publisher_liveness(self):
        """Check if publisher is alive and well."""

    def check_subscriber_liveness(self):
        """Check if subscriber is alive and well."""
        subscriber = self.config.get("subscriber")
        if subscriber is not None:
            if not subscriber.is_alive():
                raise SubscriberDied
