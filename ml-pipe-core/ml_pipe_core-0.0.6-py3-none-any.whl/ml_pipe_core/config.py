import logging
import os

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

KAFKA_SERVER_URL = None
broker_str = os.environ.get('PIPE_KAFKA_BROKERS')
if broker_str != None:
    brokers = [b.strip() for b in broker_str.split(',')]
    KAFKA_SERVER_URL = brokers[0]
if KAFKA_SERVER_URL == None:
    raise ValueError(f"No broker is set in PIPE_KAFKA_BROKERS env.")

MYSQL_USER = os.environ.get('SIM_SQL_USER')
if MYSQL_USER == None:
    raise ValueError("Environment value MYSQL_USER isn't set.")
MYSQL_PW = os.environ.get('SIM_SQL_PW')
if MYSQL_PW == None:
    raise ValueError("Environment value SIM_SQL_PW isn't set.")
MYSQL_HOST, MYSQL_PORT = os.environ.get('PIPE_SIMULATION_DB').strip().split(':')
if MYSQL_HOST == None:
    raise ValueError(f"No simulation_db is set in PIPE_SIMULATION_DB env.")
MYSQL_PORT = os.environ.get('SIM_SQL_PORT', 3306)

if os.environ.get('PIPE_LOGSTASH') != None and os.environ.get('PIPE_LOGSTASH'):
    LOGSTASH_SERVER_URL, LOGSTASH_PORT = os.environ.get('PIPE_LOGSTASH').strip().split(':')
else:
    LOGSTASH_SERVER_URL = None
    LOGSTASH_PORT = None

OBSERVER_URL = os.environ.get('OBSERVER_URL')
REGISTER_URL = os.environ.get('REGISTER_URL')
_logger.info(f"KAFKA_SERVER_URL={KAFKA_SERVER_URL}")
_logger.info(f"MYSQL_HOST={MYSQL_HOST}")
_logger.info(f"MYSQL_PORT={MYSQL_PORT}")
_logger.info(f"MYSQL_USER={MYSQL_USER}")
