import os

def get_env_var(key, default=None):
    if key not in os.environ:
        return default
    return os.environ[key]

API_SERVER_ADDRESS = get_env_var('API_SERVER_ADDRESS', '140.96.29.151')
API_BASE_URL = 'http://{}/api'.format(API_SERVER_ADDRESS)
DATA_PORT = get_env_var('DATA_PORT', '5000')
