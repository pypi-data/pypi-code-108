import os
import socket
import logging
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


@lru_cache()
def local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('180.76.76.76', 80))
        r = s.getsockname()[0]
    return r


def hostname():
    return socket.gethostname()


def str_bool(raw):
    if raw and raw.lower() in ('true', 't', '1'):
        return True
    return False


SCHEMA = os.getenv('APP_SCHEMA', 'public')
APP_ENV = os.getenv('APP_ENV', 'prod')
APP_DEBUG = str_bool(os.getenv('APP_DEBUG'))
APP_PORT = int(os.getenv('APP_PORT', 5000))
CLIENT_ID = os.getenv('CLIENT_ID', hostname())
CLIENT_IP = os.getenv('CLIENT_IP', local_ip())
APP_NAME = os.getenv('APP_NAME', 'app')
IS_WORKER = str_bool(os.getenv('IS_WORKER'))
CONFIG_PATH = '/'.join(['config', APP_NAME.lower(), APP_ENV.lower()])
CACHE_PATH = Path(os.getenv('CACHE_PATH', '/tmp')).resolve()
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=LOG_LEVEL)



__all__ = (
  'SCHEMA',
  'APP_ENV',
  'APP_DEBUG',
  'APP_PORT',
  'CLIENT_ID',
  'CLIENT_IP',
  'APP_NAME',
  'IS_WORKER',
  'CONFIG_PATH',
  'CACHE_PATH',
)
