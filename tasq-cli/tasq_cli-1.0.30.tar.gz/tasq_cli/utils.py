import configparser
import os
from datetime import datetime


def timestamp_for_file_name():
    return datetime.now().strftime('%Y%m%d-%H%M%S')


def get_config_directory():
    tasq_dir = os.path.join(os.path.expanduser('~'), '.tasq')
    os.makedirs(tasq_dir, exist_ok=True)
    return tasq_dir


def get_config_file_path():
    return os.path.join(get_config_directory(), 'config.ini')


def write_default_config():
    config = configparser.ConfigParser()

    config.add_section('credentials')
    config['credentials']['client_id'] = ''
    config['credentials']['bucket_name'] = ''
    config['credentials']['access_key'] = ''
    config['credentials']['secret_key'] = ''
    config['credentials']['token'] = ''

    with open(get_config_file_path(), 'w') as f:
        config.write(f)


def get_credentials():
    if not os.path.isfile(get_config_file_path()):
        write_default_config()

    config = configparser.ConfigParser()
    config.read(get_config_file_path())

    return {
        'client_id': config.get('credentials', 'client_id', fallback=''),
        'bucket_name': config.get('credentials', 'bucket_name', fallback=''),
        'access_key': config.get('credentials', 'access_key', fallback=''),
        'secret_key': config.get('credentials', 'secret_key', fallback=''),
        'token': config.get('credentials', 'token', fallback=''),
    }
