import logging

from logging import Handler
from typing import Dict

from imecilabt.gpulab.model.master import Master


class MasterJobEventLogHandler(Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to the common JobEvent handler. (which will write them to the DB)
    """

    terminator = '\n'

    def __init__(self, master: Master, job_id: str):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        Handler.__init__(self)
        if not job_id:
            raise RuntimeError('job_id is mandatory')
        self.job_id = job_id
        self.master = master

    def flush(self):
        """
        Flushes the stream.
        """
        # self.acquire()
        # try:
        #     if self.stream and hasattr(self.stream, "flush"):
        #         self.stream.flush()
        # finally:
        #     self.release()

    def emit(self, record: logging.LogRecord):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            # job_event_type = logginglevel_to_jobeventype(record.levelno)
            self.master.register_logging_event(self.job_id, record.levelno, msg)
        except Exception:
            self.handleError(record)


def _job_log_handler(master: Master, job_id: str) -> Handler:
    return MasterJobEventLogHandler(master, job_id)


_default_handler = None


def setDefaultLogHandler(handler: Handler):
    global _default_handler
    _default_handler = handler


def getLogger(name: str):
    logger = logging.getLogger(name)
    global _default_handler
    if _default_handler:
        logger.addHandler(_default_handler)
    return logger


_logger_cache : Dict[str, logging.Logger] = {}


def getJobLogger(job_id: str, master: Master) -> logging.Logger:
    if job_id in _logger_cache:
        logger = _logger_cache[job_id]
    else:
        _logger_cache[job_id] = logging.getLogger("job"+job_id)
        logger = _logger_cache[job_id]
        logger.addHandler(_job_log_handler(master, job_id))
    return logger
