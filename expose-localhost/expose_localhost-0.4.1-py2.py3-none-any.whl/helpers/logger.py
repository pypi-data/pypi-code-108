"""Custom logging setup shared across modules."""

import logging

from expose.helpers.auxiliary import DATETIME_FORMAT

LOGGER = logging.getLogger(__name__)
formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s',
    datefmt=DATETIME_FORMAT
)
handler = logging.StreamHandler()
handler.setFormatter(fmt=formatter)
LOGGER.addHandler(hdlr=handler)
LOGGER.setLevel(level=logging.DEBUG)
