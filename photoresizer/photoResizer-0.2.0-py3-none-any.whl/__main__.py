"""
Main entry point for the :mod:`photoResizer` application.

:creationdate: 2021-12-13 20:06
:moduleauthor: François GUÉRIN <frague59@gmail.com>
:modulename: photoResizer.__main__
"""
import logging
import sys

from photoResizer.cli import resize_images

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    sys.exit(resize_images())  # pragma: no cover
