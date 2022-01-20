from typing import Optional, Dict
import logging
import sys

from colorama import init, Fore, Back, Style


if sys.platform.startswith("win"):
    init()


class ColoredFormatter(logging.Formatter):
    """Colored log formatter.
    Adapted from https://gist.github.com/joshbode/58fac7ababc700f51e2a9ecdebe563ad.
    """

    def __init__(self, *args, colors: Optional[Dict[str, str]] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.colors = colors if colors else {}

    def format(self, record) -> str:
        """Format the specified record as text."""

        record.color = self.colors.get(record.levelname, '')
        record.reset = Style.RESET_ALL

        return super().format(record)

    @classmethod
    def default_chai_formatter(cls):
        return cls(
            '{asctime} |{color} {levelname:8} {reset}| {name} | {message}',
            style='{', datefmt='%Y-%m-%d %H:%M:%S',
            colors={
                'DEBUG': Fore.CYAN,
                'INFO': Fore.GREEN,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
            }
        )


def get_logger():
    formatter = ColoredFormatter.default_chai_formatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger('chai_py')
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = get_logger()
