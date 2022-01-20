import logging
import logging.handlers
import os

from tasq_cli.utils import get_config_directory, get_config_file_path, get_credentials

KB = 1024
MB = KB * 1024

VERSION = '1.0.30'

# ---
# Logging
# ---


def setup_logger():
    logger = logging.getLogger('Tasq CLI')
    logger.setLevel(logging.DEBUG)

    # create file handler
    fh = logging.handlers.RotatingFileHandler(os.path.join(get_config_directory(), 'cli.log'), maxBytes=10*MB, backupCount=5)
    fh.setLevel(logging.DEBUG)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # set formatters
    fh.setFormatter(logging.Formatter('%(asctime)s::%(name)s::%(levelname)s::%(message)s'))
    ch.setFormatter(logging.Formatter('[%(name)s] %(levelname)s :: %(message)s'))

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

_logger = setup_logger()


def get_logger():
    return _logger


# ---
# Credentials
# ---

# this should be init, so it doesn't break preemptively

creds = get_credentials()

if not creds.get('client_id', None) or not creds.get('access_key', None) or not creds.get('secret_key', None):
    _logger.critical('Credentials not set!')
    _logger.critical(f'Please add valid credentials to {get_config_file_path()}')
    exit(1)

CLIENT_ID = creds['client_id']
BUCKET = creds['bucket_name']
ACCESS_KEY = creds['access_key']
SECRET_KEY = creds['secret_key']
TOKEN = creds['token']

#SERVER = 'http://localhost:8000/api/v2'
SERVER = 'https://console.tasq.ai/api/v2'

# ---
# Settings
# ---

# TODO
## pip distribution

CDN_URL = 'https://assets.tasq.ai/{object_name}'
