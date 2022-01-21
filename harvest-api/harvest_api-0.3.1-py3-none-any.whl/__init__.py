import os
import logging
__version__ = '0.3.1'
__name__ = 'harvest_api'
__author__ = 'Ramon Moraes'
__author_email__ = 'ramonmoraes8080@gmail.com'

LOGLEVEL = os.environ.get("HARVEST_LOGLEVEL", "INFO")
logger = logging.getLogger("Harvest API")
logger.setLevel(LOGLEVEL)
