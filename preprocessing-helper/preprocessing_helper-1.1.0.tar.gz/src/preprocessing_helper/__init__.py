import logging
from .FileNameGenerator import FileNameGenerator
from .RawDataLoader import RawDataLoader

logger = logging.getLogger("preprocessing_helper")
console_handler = logging.StreamHandler()

logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
