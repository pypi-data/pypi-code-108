import io
import re
import time
from datetime import datetime
import pytz
import os

# Log levels
LOGS_TYPE_OUTPUT = "output"
LOGS_TYPE_ERROR = "error"
LOGS_TYPE_INFO = "info"
LOGS_TYPE_WARNING = "warning"

# Log filter types
FILTER_LOGS_STDOUT = "stdout"
FILTER_LOGS_CNVRG_ERROR = "cnvrg-error"
FILTER_LOGS_CNVRG_INFO = "cnvrg-info"


MAX_LOGS_PER_SEND = int(os.environ.get("CNVRG_MAX_LOGS_PER_SEND") or 500)

ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


def timestamp_for_logs():
    """
    @return: A string representing current UTC time
    """
    return datetime.utcnow().replace(tzinfo=pytz.utc).strftime("%Y-%m-%dT%H:%M:%S%z")


def extract_lines(block):
    """
    Extracts logs from a log buffer
    @param block: String of buffered logs, from stdout/stderr
    @return: List of parsed logs
    """
    return [ANSI_ESCAPE.sub('', line) for line in block.strip().split("\n")]


def log_buffer(workflow, log_type, buffer):
    """
    Function that parses a buffer holding logs and sends them to the corresponding workflow at the server
    The function will run until the buffer is closed or eof is present.
    @param workflow: Current workflow's object. Used to send logs to the server
    @param log_type: The log level to be written
    @param buffer: The buffer to be parsed (StringIo or BufferedReader)
    @return: None
    """
    if isinstance(buffer, io.StringIO):
        seek = 0
        while True:
            buffer_value = buffer.getvalue()
            lines = extract_lines(buffer_value[seek:].strip('\0'))
            workflow.write_logs(lines, log_type=log_type)
            seek = len(buffer_value)

            if '\0' in buffer_value:
                break
            time.sleep(0.5)
    else:
        # Is BufferedReader
        for log in buffer:
            log = log.decode("utf-8")
            workflow.write_logs(log, log_type=log_type)
