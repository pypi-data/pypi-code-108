import re
import sys
import logbook
import sentry_sdk
import typing as T
from sentry_sdk.hub import Hub
from sentry_sdk.integrations.logging import ignore_logger
from logbook import NullHandler
from sentry_sdk.utils import (
    to_string,
    get_lines_from_file,
    event_from_exception,
    current_stacktrace,
    capture_internal_exceptions,
)
from dbt.contracts.results import NodeStatus

from .constants import StatusColor
from .config import NAME, ENV, SENTRY_DSN, APP_VERSION

logger = logbook.Logger("pydbt")

ignore_logger('configured_file')
ignore_logger('configured_std_out')

sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=ENV,
    release=f"{NAME}@{APP_VERSION}",
)


def set_sentry_tags(tags: T.Dict):
    for key, val in tags.items():
        sentry_sdk.set_tag(key, str(val))


def dbt_to_log_status(status: NodeStatus, resource_type: T.Optional[str] = None):
    status_mapper = {
        NodeStatus.Success: logbook.INFO,
        NodeStatus.Error: logbook.ERROR,
        NodeStatus.Fail: logbook.ERROR,
        NodeStatus.Warn: logbook.WARNING,
        NodeStatus.Skipped: logbook.WARNING,
        NodeStatus.Pass: logbook.INFO,
        NodeStatus.RuntimeErr: logbook.CRITICAL,
    }

    return status_mapper.get(status, logbook.NOTSET)


def logbook_status_to_color(status: int):
    status_mapper = {
        logbook.CRITICAL: StatusColor.CRITICAL,
        logbook.ERROR: StatusColor.ERROR,
        logbook.WARNING: StatusColor.WARNING,
        logbook.NOTICE: StatusColor.NOTICE,
        logbook.INFO: StatusColor.INFO,
        logbook.DEBUG: StatusColor.DEBUG,
        logbook.NOTSET: StatusColor.DEBUG,
    }

    return status_mapper.get(status, StatusColor.INFO)


class SentryHandler(logbook.Handler):
    def emit(self, record):
        with capture_internal_exceptions():
            self.format(record)
            return self._emit(record)

    def _emit(self, record):
        hub = Hub.current
        if hub.client is None:
            return

        client_options = hub.client.options
        trace = record.kwargs.pop("trace", None)

        # exc_info might be None or (None, None, None)
        if record.exc_info is not None and record.exc_info[0] is not None:
            event, hint = event_from_exception(
                record.exc_info,
                client_options=client_options,
                mechanism={"type": "logbook", "handled": True},
            )
        elif record.exc_info and record.exc_info[0] is None:
            event = {}
            hint = {}
            with capture_internal_exceptions():
                event["threads"] = {
                    "values": [
                        {
                            "stacktrace": current_stacktrace(
                                client_options["with_locals"]
                            ),
                            "crashed": False,
                            "current": True,
                        }
                    ]
                }
        else:
            event = {}
            hint = {}

        if trace:
            context = record.kwargs.pop("context", {})
            pre_context, context_line, post_context = get_lines_from_file(
                context.get("abs_path", None), 1
            )
            event["exception"] = {
                "type": to_string(record.msg),
                "value": trace,
                "stacktrace": {
                    "frames": [
                        {
                            "function": "run",
                            "module": "dbt",
                            "pre_context": pre_context,
                            "context_line": to_string(trace),
                            "post_context": post_context,
                            "abs_path": context.get("abs_path", None),
                            "filename": context.get("filename", None),
                            "lineno": 1,
                            "in_app": True,
                        }
                    ],
                },
            }

        hint["log_record"] = record

        event["level"] = logbook.get_level_name(record.level).lower()
        event["type"] = logbook.get_level_name(record.level).lower()
        event["logger"] = record.channel
        event["logentry"] = {"message": to_string(record.msg), "params": record.args}
        event["extra"] = {
            "lineno": record.lineno,
            "filename": record.filename,
            "function": record.func_name,
            "process": record.process,
            "process_name": record.process_name,
        }

        hub.capture_event(event, hint=hint)


class FormatMessage(logbook.Processor):
    def process(self, record):
        ansi_escape = re.compile(
            r"""
            \x1B    # ESC
            [@-_]   # 7-bit C1 Fe
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        """,
            re.VERBOSE,
        )
        clean = ansi_escape.sub("", str(record.msg))
        record.msg = clean.lower()


class LogManager(logbook.NestedSetup):
    def __init__(self, tags=T.Dict, stdout=sys.stdout, stderr=sys.stderr):
        self.tags = tags
        self.stdout = stdout
        self.stderr = stderr

        set_sentry_tags(tags)

        self._null_handler = NullHandler()
        self._sentry_handler = SentryHandler(level=logbook.WARNING, bubble=True)
        self._format_processor = FormatMessage()
        self._clean_message_processor = CleanMessage()

        super().__init__(
            [
                self._null_handler,
                self._sentry_handler,
                self._format_processor,
                self._clean_message_processor,
            ]
        )

    def format_json(self):
        for handler in self.objects:
            if hasattr(handler, "format_json"):
                handler.format_json()


class AppendTags(logbook.Processor):
    def __init__(self, tags: T.Dict):
        self.tags = tags
        set_sentry_tags(tags)
        super().__init__()

    def process(self, record):
        record.extra["tags"] = self.tags


class CleanMessage(logbook.Processor):
    def process(self, record):
        record.msg = str(record.msg)
        record.msg = record.msg.replace("*", "")
        record.msg = record.msg.replace("`", "")


GLOBAL_LOGGER = logger
