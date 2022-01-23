import logging
import logging.config


class DefaultFormatter(logging.Formatter):
    """Custom logger for exmon system.
    - Color changes based on logging level
    - prints file the log originated from
    - prints severity level
    """

    # https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_(Select_Graphic_Rendition)_parameters
    BLUE = "\x1b[34;22m"
    GREEN = "\x1b[32;22m"
    YELLOW = "\x1b[33;22m"
    RED = "\x1b[31;22m"
    BOLD_RED = "\x1b[31;1m"

    MAGENTA = "\x1b[35;22m"
    CYAN = "\x1b[36;22m"
    WHITE = "\x1b[37;22m"
    DEFAULT = "\x1b[39;22m"

    RESET = "\x1b[0m"

    # logging format
    FORM = "%(asctime)s - %(name)s [%(levelname)s]:\t%(message)s (%(filename)s:%(lineno)d)"

    # combines color, logging format and reset
    FORMATS = {
        logging.DEBUG: BLUE + FORM + RESET,
        logging.INFO: GREEN + FORM + RESET,
        logging.WARNING: YELLOW + FORM + RESET,
        logging.ERROR: RED + FORM + RESET,
        logging.CRITICAL: BOLD_RED + FORM + RESET
    }

    def format(self, record):
        """custom format. calls default format method"""

        # generate logging format string
        log_fmt = self.FORMATS.get(record.levelno)

        # get default logging formatter with new date format
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")

        # call default formatter
        return formatter.format(record)
