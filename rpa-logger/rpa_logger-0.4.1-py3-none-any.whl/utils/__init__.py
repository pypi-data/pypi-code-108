'''Utilities to make `rpa_logger` usage easier.
'''

from datetime import datetime


def timestamp():
    '''Get UTC ISO-8601 timestamp for current time.

    Returns:
        String with UTC ISO-8601 timestamp for current time
    '''
    return f'{datetime.utcnow().isoformat()}Z'
