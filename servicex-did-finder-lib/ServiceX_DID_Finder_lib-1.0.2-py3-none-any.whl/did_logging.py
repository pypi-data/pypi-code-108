import logging
import os


class DIDFormatter(logging.Formatter):
    """
    Need a customer formatter to allow for logging with request ids that vary.
    Normally log messages are "level instance component request_id msg" and
    request_id gets set by initialize_logging but we need a handler that'll let
    us pass in the request id and have that embedded in the log message
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format record with request id if present, otherwise assume None

        :param record: LogRecord
        :return: formatted log message
        """

        if hasattr(record, "requestId"):
            return super().format(record)
        else:
            setattr(record, "requestId", None)
            return super().format(record)


def initialize_root_logger(did_scheme: str):
    """
    Get a logger and initialize it so that it outputs the correct format
    :param did_scheme: The scheme name to identify his did finder in log messages.
    :return: logger with correct formatting that outputs to console
    """

    log = logging.getLogger()
    instance = os.environ.get('INSTANCE_NAME', 'Unknown')
    formatter = DIDFormatter('%(levelname)s ' +
                             f"{instance} {did_scheme}_did_finder " +
                             '%(requestId)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log
