# Copyright 2022 Henix, henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""opentf-ctl networking"""

import sys

from urllib.parse import urlparse

import requests.exceptions

from opentf.tools.ctlcommons import _error
from opentf.tools.ctlconfig import CONFIG, HEADERS


########################################################################


def _make_hostport(service):
    """Adjust server port for service."""
    server = CONFIG['orchestrator']['server']
    if 'ports' in CONFIG['orchestrator']:
        port = str(CONFIG['orchestrator']['ports'].get(service, ''))
        if port:
            url = urlparse(server)
            new = url._replace(netloc=url.netloc.split(':')[0] + ':' + port)
            server = new.geturl()
    return server.strip('/')


def _receptionist():
    return _make_hostport('receptionist')


def _observer():
    return _make_hostport('observer')


def _killswitch():
    return _make_hostport('killswitch')


def _eventbus():
    return _make_hostport('eventbus')


def _agentchannel():
    return _make_hostport('agentchannel')


########################################################################


def _get(service, path='', msg=None, statuses=(200,), handler=None, raw=False):
    if msg is None:
        msg = f'Could not query {service}{path}'
    try:
        what = requests.get(
            service + path,
            headers=HEADERS,
            verify=not CONFIG['orchestrator']['insecure-skip-tls-verify'],
        )
        if what.status_code in statuses:
            if not raw:
                what = what.json()
        elif handler is not None:
            handler(what)
        else:
            _error(
                msg + ', got %d: %s.',
                what.status_code,
                what.text,
            )
            sys.exit(1)
    except requests.exceptions.ConnectionError as err:
        _could_not_connect(service, err)
    except Exception as err:
        _error(msg + ': %s.', err)
        sys.exit(2)

    return what


def _post(service, path='', msg=None, statuses=(200,), handler=None, files=None):
    if msg is None:
        msg = f'Could not post to {service}{path}'
    try:
        what = requests.post(
            service + path,
            files=files,
            headers=HEADERS,
            verify=not CONFIG['orchestrator']['insecure-skip-tls-verify'],
        )
        if what.status_code in statuses:
            what = what.json()
        elif handler is not None:
            handler(what)
        else:
            _error(
                msg + ', got %d: %s.',
                what.status_code,
                what.text,
            )
            sys.exit(1)
    except requests.exceptions.ConnectionError as err:
        _could_not_connect(service, err)
    except Exception as err:
        _error(msg + ': %s.', err)
        sys.exit(2)

    return what


def _delete(service, path='', msg=None, statuses=(200,), handler=None):
    if msg is None:
        msg = f'Could not delete {service}{path}'
    try:
        what = requests.delete(
            service + path,
            headers=HEADERS,
            verify=not CONFIG['orchestrator']['insecure-skip-tls-verify'],
        )
        if what.status_code in statuses:
            what = what.json()
        elif handler is not None:
            handler(what)
        elif what.status_code == 404:
            _error(msg + ': not found.')
            sys.exit(1)
        else:
            _error(
                msg + ', got %d: %s.',
                what.status_code,
                what.text,
            )
            sys.exit(1)
    except requests.exceptions.ConnectionError as err:
        _could_not_connect(service, err)
    except Exception as err:
        _error(service + ': %s.', err)
        sys.exit(2)

    return what


########################################################################


def _could_not_connect(target, err):
    if isinstance(err, requests.exceptions.ProxyError):
        _error('A proxy error occurred: %s.', str(err))
        _error(
            '(You can use the HTTP_PROXY or the HTTPS_PROXY environment variables'
            ' to set a proxy.)'
        )
    elif isinstance(err, requests.exceptions.SSLError):
        _error('A SSL error occurred: %s.', str(err))
        _error(
            '(You can disable SSL verification by using the "--insecure-skip-tls-verify=true"'
            ' command-line option.  **Please note that this should be for debugging'
            ' purpose only.**)'
        )
    else:
        _error(
            'Could not reach the orchestrator (%s).  Is the orchestrator running?',
            str(err),
        )
    _error('(Attempting to reach %s.)', target)
    sys.exit(2)
