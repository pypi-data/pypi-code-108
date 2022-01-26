"""
Short for Seeq PYthon, the SPy library provides methods to interact with data that is exposed to the Seeq Server.
"""
from typing import Optional

from seeq.sdk import ApiClient
from seeq.sdk.configuration import Configuration
from seeq.sdk.models import UserOutputV1
from seeq.spy import addons
from seeq.spy import assets
from seeq.spy import docs
from seeq.spy import jobs
from seeq.spy import utils
from seeq.spy import widgets
from seeq.spy import workbooks
from seeq.spy._common import PATH_ROOT, DEFAULT_WORKBOOK_PATH, GLOBALS_ONLY, GLOBALS_AND_ALL_WORKBOOKS
from seeq.spy._config import Options
from seeq.spy._login import login, logout
from seeq.spy._plot import plot
from seeq.spy._pull import pull
from seeq.spy._push import push
from seeq.spy._search import search
from seeq.spy._session import Session
from seeq.spy._status import Status

# noinspection DuplicatedCode
session: Session = Session(client_configuration=Configuration())
options: Options = session.options
client: Optional[ApiClient] = None
user: Optional[UserOutputV1] = None
server_version: Optional[str] = None

__all__ = ['addons', 'assets', 'docs', 'workbooks', 'widgets', 'login', 'logout', 'plot', 'pull', 'push', 'search',
           'PATH_ROOT', 'DEFAULT_WORKBOOK_PATH', 'GLOBALS_ONLY', 'GLOBALS_AND_ALL_WORKBOOKS', 'Session', 'Status',
           'options', 'session', 'client', 'user', 'server_version', 'jobs', 'utils']

__version__ = '%d.%d.%d.%d.%d' % (int('$SQ(VERSION_MAJOR)'), int('$SQ(VERSION_MINOR)'), int('$SQ(VERSION_PATCH)'),
                                  int('$SQ(VERSION_MAJOR_PYPI)'), int('$SQ(VERSION_MINOR_PYPI)'))
