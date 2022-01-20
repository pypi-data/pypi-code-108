""" Constants used by Masterful. """

import os
import typing


def _environment_override(env_variable: str,
                          default: str,
                          type: typing.Type = None) -> str:
  if type is not None:
    return (type(os.environ[env_variable])
            if env_variable in os.environ else default)
  else:
    return (os.environ[env_variable] if env_variable in os.environ else default)


MASTERFUL_ACCOUNT_ID = _environment_override('MASTERFUL_ACCOUNT_ID', '')
MASTERFUL_AUTHORIZATION_KEY = _environment_override(
    'MASTERFUL_AUTHORIZATION_KEY', '')
MASTERFUL_SESSION_ID = ''

MASTERFUL_API_URL = _environment_override(
    'MASTERFUL_API_URL',
    'https://kjsbngy38b.execute-api.us-east-1.amazonaws.com/prod/')
MASTERFUL_LOAD = f'{MASTERFUL_API_URL}/load'
MASTERFUL_LOG_ENTRY = f'{MASTERFUL_API_URL}/log_entry'

MASTERFUL_VERBOSITY = _environment_override('MASTERFUL_VERBOSITY', 0, int)
