import logging

from centaur._.pyvmps.logger._.escape_codes import escape_codes, parse_colors

default_log_colors = {"DEBUG": "green", "INFO": "black", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold_purple"}


class ColorizedRecord(object):
    """
    Wraps a log record, adding named escape codes to the internal dict.
    The internal dict will be used when format the message.
    """

    def __init__(self, record):
        """Add attributes from the escape_codes dict and the record."""
        self.__dict__.update(escape_codes)
        self.__dict__.update(record.__dict__)

        # Keep a reference to the original record so `__getattr__` can access functions that are not in `__dict__`.
        self.__record = record

    def __getattr__(self, name):
        return getattr(self.__record, name)


class ColorizedFormatter(logging.Formatter):
    """
    A formatter that allows colors to be placed in the format string.
    Intended to help in creating more readable logging output.
    """

    def __init__(self, log_colors=None):
        super(ColorizedFormatter, self).__init__(
            "%(log_color)s%(asctime)s %(levelname)-8s %(name)s %(lineno)d %(message)s"
        )

        self.log_colors = log_colors if log_colors is not None else default_log_colors

    def format(self, record):
        """Format a message from a record object."""
        record = ColorizedRecord(record)
        record.log_color = parse_colors(self.log_colors.get(record.levelname))

        message = super(ColorizedFormatter, self).format(record)

        if not message.endswith(escape_codes["reset"]):
            message += escape_codes["reset"]

        return message
