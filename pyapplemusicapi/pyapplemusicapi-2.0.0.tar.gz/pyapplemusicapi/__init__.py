# -*- coding: utf-8 -*-
"""A simple Python interface to search the Apple Music and Apple TV libraries"""

__name__ = 'pyapplemusicapi'
__doc__ = 'A simple Python interface to search the Apple Music and Apple TV libraries'
__author__ = ["Vinyl Da.i'gyu-Kazotetsu", 'Jonathan Nappi', 'Oscar Celma']
__version__ = '2.0.0'
__license__ = 'GPLv3'
__maintainer__ = "Vinyl Da.i'gyu-Kazotetsu"
__email__ = ['queen@gooborg.com', 'moogar@comcast.net', 'ocelma@bmat.com']
__status__ = 'Stable'
__url__ = 'https://github.com/queengooborg/pyapplemusicapi'

#: API Info
API_VERSION = '2' # API Version
COUNTRY = 'US'    # Store Country Code
API_HOST_NAME = 'https://itunes.apple.com'

# Client hostname
HOST_NAME = 'https://music.apple.com'

from pyapplemusicapi.base import *  # NOQA
from pyapplemusicapi.exceptions import *  # NOQA
from pyapplemusicapi.search import *  # NOQA
