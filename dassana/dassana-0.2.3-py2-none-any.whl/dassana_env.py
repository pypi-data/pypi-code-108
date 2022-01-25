import os

def get_endpoint():
    if 'DASSANA_ENDPOINT' not in os.environ:
        raise KeyError("DASSANA_ENDPOINT environment variable is not set. Review your Lambda configuration.")
    return os.environ['DASSANA_ENDPOINT']

def get_app_id():
    if 'DASSANA_APP_ID' not in os.environ:
        raise KeyError("DASSANA_APP_ID environment variable is not set. Review your Lambda configuration.")
    return os.environ['DASSANA_APP_ID']

def get_token():
    if 'DASSANA_TOKEN' not in os.environ:
        raise KeyError("DASSANA_TOKEN environment variable is not set. Review your Lambda configuration.")
    return os.environ['DASSANA_TOKEN']

def get_ssl():
    return get_endpoint().startswith('https')