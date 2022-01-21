# Copyright 2021 Henix, henix.fr
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


"""OpenTestFactory Orchestrator availability checker"""

import argparse
import logging
import sys

from time import sleep, time
from urllib.parse import urlparse

import requests


########################################################################

DEFAULT_POLLING_DELAY = 5
DEFAULT_TIMEOUT_DELAY = 3600
DEFAULT_PORT = 7775

ENDPOINT_TEMPLATE = '{server}/workflows/status'


########################################################################


def wait_until_idle(endpoint, headers, polling, timeout):
    """Wait until orchestrator is in IDLE state."""
    start = time()
    try:
        while (
            requests.get(endpoint, headers=headers).json()['details']['status']
            != 'IDLE'
        ):
            sleep(int(polling))
            if (time() - start) > int(timeout):
                return False
        return True
    except Exception as err:
        logging.error(
            'Something went wront while checking orchestrator status: %s', err
        )
        sys.exit(2)
    return False


def main():
    """Manage the script"""
    parser = argparse.ArgumentParser(
        description="OpenTestFactory Orchestrator availability checker"
    )
    parser.add_argument(
        "--timeout",
        help=f"verification timeout in seconds (default to {DEFAULT_TIMEOUT_DELAY})",
        default=DEFAULT_TIMEOUT_DELAY,
    )
    parser.add_argument(
        "--polling_delay",
        help=f"polling delay in seconds (default to {DEFAULT_POLLING_DELAY})",
        default=DEFAULT_POLLING_DELAY,
    )
    parser.add_argument(
        "--host",
        help="target host with protocol (e.g. https://example.local)",
        required=True,
    )
    parser.add_argument(
        "--port",
        help=f"target port (default to {DEFAULT_PORT})",
        default=DEFAULT_PORT,
    )
    parser.add_argument(
        "--token",
        help="token",
        required=True,
    )

    args = parser.parse_args()

    logging.info('Waiting for orchestratoy completion...')
    if args.token:
        headers = {'Authorization': f'Bearer {args.token}'}
    else:
        headers = None

    url = urlparse(args.host)
    new = url._replace(netloc=url.netloc.split(':')[0] + ':' + str(args.port))
    server = new.geturl()
    endpoint = ENDPOINT_TEMPLATE.format(server=server.strip('/'))

    if wait_until_idle(endpoint, headers, args.polling_delay, args.timeout):
        logging.info('Done.')
        sys.exit(0)
    else:
        logging.error('Timeout exceeded.  Could not confirm orchestrator IDLE status')
        sys.exit(1)


if __name__ == "__main__":
    main()
