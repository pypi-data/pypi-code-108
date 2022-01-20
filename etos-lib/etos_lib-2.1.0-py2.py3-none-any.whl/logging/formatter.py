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
"""ETOS log formatter."""
import datetime
import json
import logging
import sys
import traceback


# LogRecord fields that we exclude, typically because we offer
# something better.
_EXCLUDED_FIELDS = (
    # Superfluous since we're saving the timestamp in '@timestamp'.
    "asctime",
    # The arguments to the format string can contain arbitrary objects
    # that can't be serialized to JSON. We could pass them to str(),
    # but that assumes that '%s' is used in the format string.
    "args",
    "msg",
    # Exception info is saved in exception.{type,message,stacktrace}
    # instead.
    "exc_info",
    "exc_text",
    "stack_info",
)


class EtosLogFormatter(logging.Formatter):
    """Logging formatter that produces a JSON object.

    The resulting JSON object contains the logging.LogRecord fields
    untouched. The following exception from this rule exist:

        - A '@timestamp' key with the log record's UTC timestamp in ISO8601
          format, digestible by Logstash.
        - If an exception context exists (i.e. sys.exc_info() returns
          something) the resulting JSON object will contain an 'exception'
          key pointing to an object with the following keys:

              - 'type': The fully-qualified type name (i.e. including
                 package and module).
              - 'message': The exception message.
              - 'stacktrace': The formatted stacktrace as a multiline string
                 (not ending in a newline character).
    """

    def format(self, record):
        """Serialize LogRecord data as JSON.

        Overrides the inherited behavior by ignoring any configured
        format string and storing attributes of the passed LogRecord
        object in a dictionary and serializing it to JSON. See class
        docstring for details.
        """
        fields = {
            k: v
            for k, v in record.__dict__.items()
            if k not in _EXCLUDED_FIELDS and not k.startswith("_")
        }
        fields["@timestamp"] = self.formatTime(record)
        fields["message"] = record.getMessage()
        exc_type, exc_message, stack = sys.exc_info()
        if exc_type and exc_message and stack:
            fields["exception"] = {
                "type": f"{exc_type.__module__}.{exc_type.__name__}",
                "message": str(exc_message),
                # format_tb() returns a list of newline-terminated strings.
                # Don't include the final newline.
                "stacktrace": "".join(traceback.format_tb(stack)).rstrip(),
            }
        # No need to append a newline character; that's up to the handler.
        return json.dumps(fields)

    def formatTime(self, record, datefmt=None):
        """Format the log record's timestamp in ISO8601 format, in UTC.

        Overrides the inherited behavior by always returning ISO8601
        strings without allowing custom date formats.
        Raises:
            NotImplementedError: If the `datefmt` parameter is not None.
        """
        if datefmt is not None:
            raise NotImplementedError("Only default time format is supported.")
        # Make Logstash's @timestamp parser happy by including a "T"
        # between the date and the time. Append 'Z' to make it clear
        # that the timestamp is UTC.
        return datetime.datetime.utcfromtimestamp(record.created).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
