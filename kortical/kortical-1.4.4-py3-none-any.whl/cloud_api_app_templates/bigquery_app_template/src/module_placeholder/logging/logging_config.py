import sys
import logging


class ForwardToStdErr():
    def write(self, s):
        sys.stderr.write(s)

    def isatty(self):
        return sys.stderr.isatty()

    def flush(self):
        sys.stderr.flush()

    def __getattr__(self, name):
        return sys.stderr.__getattribute__(name)


class ForwardToStdOut:
    def write(self, s):
        sys.stdout.write(s)

    def isatty(self):
        return sys.stdout.isatty()

    def flush(self):
        sys.stdout.flush()

    def __getattr__(self, name):
        return sys.stdout.__getattribute__(name)


def init(log_level=logging.DEBUG):
    logging.basicConfig(level=log_level)
    root_logger = logging.getLogger()
    root_logger.handlers = []

    # Create formatter
    formatter = logging.Formatter('%(asctime)s %(process)d %(processName)s %(threadName)s %(levelname)s %(message)s - %(name)s')

    # Create console handlers
    # Send warnings and errors to stderr
    error_stream_handler = logging.StreamHandler(ForwardToStdErr())
    error_stream_handler.setLevel(max(log_level, logging.WARNING))
    error_stream_handler.setFormatter(formatter)
    root_logger.addHandler(error_stream_handler)

    # Send everything else to stdout
    if log_level < logging.WARNING:
        info_stream_handler = logging.StreamHandler(ForwardToStdOut())
        info_stream_handler.setLevel(log_level)
        info_stream_handler.setFormatter(formatter)
        info_stream_handler.addFilter(lambda record: record.levelno < logging.WARNING)
        root_logger.addHandler(info_stream_handler)
