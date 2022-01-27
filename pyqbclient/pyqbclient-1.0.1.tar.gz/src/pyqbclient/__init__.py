from .pyqbclient import *
import logging
from logging import NullHandler
logging.getLogger("pyqbclient").addHandler(NullHandler())