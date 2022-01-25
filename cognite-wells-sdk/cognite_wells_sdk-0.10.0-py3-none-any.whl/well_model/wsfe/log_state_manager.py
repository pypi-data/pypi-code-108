import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

from cognite.well_model.wsfe.models import ProcessState, ProcessStatus, Severity


class TimestampFilter(logging.Filter):
    """
    This is a logging filter which will check for a `timestamp` attribute on a
    given LogRecord, and if present it will override the LogRecord creation time
    to be that of the timestamp (specified as a time.time()-style value).
    This allows one to override the date/time output for log entries by specifying
    `timestamp` in the `extra` option to the logging call.
    """

    def filter(self, record):
        if hasattr(record, "timestamp"):
            record.created = record.timestamp.timestamp()
        return True


log = logging.getLogger(__name__)
log.addFilter(TimestampFilter())


class LogStateManager:
    def __init__(self):
        # Map from process id to index in log stream
        self.print_index: Dict[str, int] = {}
        self.time_last_summary = datetime.now()

    def is_complete(self):
        return abs(self.progress - 100) < 0.001

    def add_log(self, states: List[ProcessState]):
        COMPLETE = [ProcessStatus.done, ProcessStatus.error]
        done_count = sum(1 for x in states if x.status in COMPLETE)
        progress = 100.0 * done_count / len(states)
        self.progress = progress
        for state in states:
            state_print_index = self.print_index.get(state.process_id, 0)
            for i in range(state_print_index, len(state.logs)):
                event = state.logs[i]
                logger = self.get_logger_function(event.severity)
                message = event.message
                if not message.startswith("["):
                    message = " " * 8 + message
                logger(
                    f"[{progress:5.1f}%] [{state.file_external_id}] {message}",
                    extra={"timestamp": event.timestamp},
                )
            self.print_index[state.process_id] = len(state.logs)
        self.print_summary_if_its_time(states)

    def get_logger_function(self, severity: Severity):
        map = {
            Severity.info: log.info,
            Severity.warning: log.warning,
            Severity.error: log.error,
        }
        return map.get(severity) or log.info

    def print_summary_if_its_time(self, states: List[ProcessState]):
        dt = datetime.now() - self.time_last_summary
        summary_dt = timedelta(seconds=5)
        if dt > summary_dt:
            self.time_last_summary = datetime.now()
            self.print_summary(states)

    def print_summary(self, states: List[ProcessState]):
        d: Dict[ProcessStatus, int] = defaultdict(lambda: 0)
        for state in states:
            d[state.status] += 1
        log.info(
            f"Ready={d[ProcessStatus.ready]} "
            + f"Processing={d[ProcessStatus.processing]} "
            + f"Done={d[ProcessStatus.done]} "
            + f"Error={d[ProcessStatus.error]}",
        )
