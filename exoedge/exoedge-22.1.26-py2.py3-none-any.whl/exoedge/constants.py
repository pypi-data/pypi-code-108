# pylint: disable=C0325, C0103, C0111

""" Constants """
import copy
import json
import os

import pureyaml
from appdirs import user_data_dir

OPTION_PRECEDENCE = ['cli', 'env', 'ini', 'dft']

OPTION_TYPE_MAP = {
    'debug': str,
    'murano_host': str,
    'murano_id': str,
    'config_io_file': str,
    'config_applications_file': str,
    'ini_file': str,
    'murano_token': str,
    'watchlist': list,
    'http_timeout': int,
    'certfile': str,
    'pkeyfile': str,
    'murano_cacert': str,
    'murano_port': int,
    'queuing': bool,
    'queuing_batch_amount': int,
    'queuing_db_max_size': int,
    'queuing_db_path': str,
    'queuing_record_rate': int,
    'queuing_remove_unused_device': bool,
    'queuing_drop_strategy': str,
    'no-logrotate': bool,
    'log-filename': str,
    'log-max-bytes': int,
    'log-max-backups': int,
}

OPTION_NAME_MAPPER = {
    'env': lambda d, x: d.get('EDGED_{}'.format(x.upper()), None),
    'cli': lambda d, x: d.get('--{}'.format(x.replace('_', '-')), None),
    'dft': lambda d, x: d.get(x, None),
    'ini': lambda d, x: d.get(x)
}

def _ini_get(I, string):
    try:
        s, o = string.split('.')
        if s in I.sections():
            return I.get(s, o)
    except:
        return None
    return None


DEFAULTS = {
    'debug': os.environ.get('EDGED_LOG_DEBUG', 'CRITICAL').upper(),
    'config_io_file': 'config_io.json',
    'config_applications_file': 'config_applications.json',
    'watchlist': ['config_io', 'data_out', 'config_applications'],
    'http_timeout': 60*5*1000,
    'ini_file': 'edged.ini',
    'no-logrotate': False,
    'log-filename': os.environ.get('EDGED_LOG_FILENAME') or 'stdout',
    'log-max-bytes': int(os.environ.get('EDGED_LOG_MAX_BYTES', 1024*1000)),
    'log-max-backups': int(os.environ.get('EDGED_LOG_MAX_BACKUPS', 3)),
    'queuing_batch_amount': 0,
    'queuing_db_max_size': 20000000,
    'queuing_db_path': user_data_dir('exoedge', 'exosite'),
    'queuing_drop_strategy': 'oldest',
    'queuing_record_rate': 1,
    'queuing_remove_unused_device': False
}
