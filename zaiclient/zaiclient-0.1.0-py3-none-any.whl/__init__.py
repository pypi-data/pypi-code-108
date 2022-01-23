'''Copyright (c) 2022 Z.ai Inc. ALL RIGHTS RESERVED

Z.ai official client SDK.
Z.ai's clients can utilize this SDK to easily connect to the provided API endpoints.
'''

__version__ = '0.1.0'

from zaiclient import auth
from zaiclient import client
from zaiclient.client import ZaiClient
from zaiclient import config
from zaiclient import http

if config.API_ENDPOINT[-1] == '/':
    raise ValueError('API enpoint URL must not end with a slash(/).')
