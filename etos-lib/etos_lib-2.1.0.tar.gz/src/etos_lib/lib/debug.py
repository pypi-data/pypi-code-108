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
"""ETOS Library debug options.

DEPRECATION WARNING: Some parameters which don't belong here will be removed.
"""
import os
from pathlib import Path
from collections import deque


class Debug:
    """Debug flags for ETOS."""

    __events_published = deque(
        maxlen=int(os.getenv("ETOS_PUBLISHED_EVENT_HISTORY_SIZE", "100"))
    )
    __events_received = deque(
        maxlen=int(os.getenv("ETOS_RECEIVED_EVENT_HISTORY_SIZE", "100"))
    )

    @property
    def default_secret_path(self):
        """Path to k8s secrets."""
        return os.getenv("ETOS_SECRET_PATH", "/etc/")

    @property
    def default_log_path(self):
        """Log path."""
        path = os.getenv("ETOS_LOG_PATH")
        if path is None:
            path = Path.home().joinpath("logs/log.json")
        else:
            path = Path(path)
        return path

    @property
    def routing_key_tag(self):
        """Tag to use for routing key on events sent by ETOS library."""
        return os.getenv("ETOS_ROUTING_KEY_TAG", "_")

    @property
    def disable_sending_events(self):
        """Disable sending eiffel events."""
        return bool(os.getenv("ETOS_DISABLE_SENDING_EVENTS", None))

    @property
    def disable_receiving_events(self):
        """Disable receiving eiffel events."""
        return bool(os.getenv("ETOS_DISABLE_RECEIVING_EVENTS", None))

    @property
    def default_http_timeout(self):
        """Timeout for HTTP requests."""
        # Defaults to 1h
        return int(os.getenv("ETOS_DEFAULT_HTTP_TIMEOUT", "3600"))

    @property
    def default_wait_timeout(self):
        """Timeout for utils.wait."""
        # Defaults to 60s
        return int(os.getenv("ETOS_DEFAULT_WAIT_TIMEOUT", "60"))

    @property
    def default_test_result_timeout(self):
        """Timeout for waiting for test results."""
        # Defaults to 24h
        return int(os.getenv("ETOS_DEFAULT_TEST_RESULT_TIMEOUT", "86400"))

    @property
    def debug_published_event_history_size(self):
        """Maximum number of published events to store in history."""
        return int(os.getenv("ETOS_PUBLISHED_EVENT_HISTORY_SIZE", "100"))

    @property
    def debug_received_event_history_size(self):
        """Maximum number of published events to store in history."""
        return int(os.getenv("ETOS_RECEIVED_EVENT_HISTORY_SIZE", "100"))

    @property
    def debug_store_events_published(self):
        """Store all eiffel events published. Do not use in production."""
        print("debug_store_events_published is DEPRECATED")
        return bool(os.getenv("ETOS_DEBUG_STORE_EVENTS_PUBLISHED", None))

    @property
    def debug_store_events_received(self):
        """Store all eiffel events received. Do not use in production."""
        print("debug_store_events_received is DEPRECATED")
        return bool(os.getenv("ETOS_DEBUG_STORE_EVENTS_RECEIVED", None))

    @property
    def disable_monitor_announce(self):
        """Disable the announcement event from monitor."""
        return bool(os.getenv("ETOS_DISABLE_MONITOR_ANNOUNCE", None))

    @property
    def environment_provider(self):
        """Environment provider host to use."""
        if os.getenv("ETOS_ENVIRONMENT_PROVIDER") is not None:
            return os.getenv("ETOS_ENVIRONMENT_PROVIDER")
        raise Exception("ETOS_ENVIRONMENT_PROVIDER environment variable not set!")

    @property
    def etos_api(self):
        """ETOS API host to use."""
        if os.getenv("ETOS_API") is not None:
            return os.getenv("ETOS_API")
        raise Exception("ETOS_API environment variable not set!")

    @property
    def graphql_server(self):
        """Graphql server to use."""
        if os.getenv("ETOS_GRAPHQL_SERVER") is not None:
            return os.getenv("ETOS_GRAPHQL_SERVER")
        raise Exception("ETOS_GRAPHQL_SERVER environment variable not set!")

    @property
    def database_host(self):
        """Database host."""
        return os.getenv("ETOS_DATABASE_HOST", "localhost")

    @property
    def database_port(self):
        """Database port."""
        return int(os.getenv("ETOS_DATABASE_PORT", "26379"))

    @property
    def events_published(self):
        """All events published if ETOS_DEBUG_STORE_EVENTS_PUBLISHED flag is set."""
        return self.__events_published

    @property
    def events_received(self):
        """All events received if ETOS_DEBUG_STORE_EVENTS_RECEIVED flag is set."""
        return self.__events_received
