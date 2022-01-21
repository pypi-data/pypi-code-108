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
import base64
import hashlib
import json
import logging
import sys
import tarfile
import threading
from time import sleep

import requests

########################################################################

INIT_FILE_PATH = "app/init_services.json"
EXIT_CODE = 1
SLEEP_DELAY = 1

TIMEOUT = HOST = PORT = CONTAINER_ID = SERVICES = TOKEN = None


########################################################################


def get_container(container_id):
    """Return targeted container.

    # Required parameters

    - container_id: a string

    # Returned value

    A _container_ object or None.
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_id)
        return container
    except docker.errors.NotFound:
        logging.error("Container %s not found.", container_id)
        return None


def is_container_ready(container_id):
    """Verify if container is running.

    # Required parameters

    - container_id: a string

    # Returned value

    A boolean.
    """
    try:
        container = get_container(container_id)
        return container.status == "running"
    except Exception:
        logging.debug('Could not get container %s, retrying.', container_id)
        return False


def get_checked_json_file(container_id):
    """Get services json file and validate it.

    # Required parameters:

    - container_id: a string

    # Returned value

    A dictionary or None.
    """
    try:
        init_services_json = get_init_services_json(container_id)
        if validate_checksum(
            init_services_json["services"], init_services_json["checksum"]
        ):
            logging.debug('Valid service list received from container.')
            return init_services_json
        logging.debug(
            'Invalid or incomplete service list received from container, retrying.'
        )
    except Exception as err:
        logging.debug('Started services list not yet available: %s.', str(err))
    return None


def get_init_services_json(container_id):
    """Get services json file from the docker container.

    # Required parameters

    - container_id: a string

    # Returned value

    A dictionary.
    """
    container = get_container(container_id)
    logging.debug('Reading started services lists from container...')
    bits = container.get_archive(INIT_FILE_PATH)[0]

    logging.debug('Writing to current directory...')
    with open("./init_services.tar", "wb") as f:
        for chunk in bits:
            f.write(chunk)

    logging.debug('Extracting...')
    with tarfile.open("init_services.tar", "r:tar") as tar:
        tar.extractall()

    logging.debug('Importing...')
    with open("init_services.json", encoding='utf-8') as json_file:
        init_services_json = json.load(json_file)

    return init_services_json


def validate_checksum(init_services, init_checksum):
    """Validate integrity of services json file."""
    services = "".join(init_services)
    services_bytes = base64.b64encode(services.encode("utf-8"))
    checksum = hashlib.sha256(services_bytes).hexdigest()
    return init_checksum == checksum


def _find(key, dictionary):
    """Find all values for a key in a json file."""
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in _find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in _find(key, d):
                    yield result


def get_checked_subscribers_list():
    """Get list of subscibers services from docker container."""
    headers = {"Authorization": (f"Bearer {TOKEN}")}
    response = requests.get(f"{HOST}:{PORT}/subscriptions", headers=headers)
    data = response.json()
    subscribers_set = set(_find("name", data))
    subscribers_list = list(subscribers_set)
    return subscribers_list


def are_ready_subscribers(init_services_list):
    """Check if declared services are ready to work."""
    try:
        init_services_list = list(init_services_list)
        init_services_list = {svc.lower() for svc in init_services_list}
        if 'receptionist' in init_services_list:
            init_services_list.remove("receptionist")
        if 'killswitch' in init_services_list:
            init_services_list.remove("killswitch")

        subscribers_list = list(get_checked_subscribers_list())
        subscribers_list = {svc.lower() for svc in subscribers_list}

        # tm.generator.premium tm.generator.community
        junk = ['tm.generator.premium', 'tm.generator.community']
        for item in junk:
            if item in init_services_list:
                init_services_list.remove(item)
                init_services_list.add('tm.generator')
            if item in subscribers_list:
                subscribers_list.remove(item)
                subscribers_list.add('tm.generator')

        # result aggregator work around
        junk = [
            'result.aggregator.execution-command',
            'result.aggregator.execution-result',
            'result.aggregator.workflow-completed',
            'result.aggregator.workflow-canceled',
        ]
        for item in junk:
            if item in init_services_list:
                init_services_list.remove(item)
                init_services_list.add('result.aggregator')
            if item in subscribers_list:
                subscribers_list.remove(item)
                subscribers_list.add('result.aggregator')

        logging.debug("Expected services: %s", sorted(init_services_list))
        logging.debug("Subscribed services: %s", sorted(subscribers_list))
        return init_services_list <= subscribers_list
    except Exception:
        logging.debug('Subscriber list not yet ready.')
        return False


def wait_till_ready():
    """Verify if orchestrator inside docker container is ready."""
    global EXIT_CODE
    if CONTAINER_ID:
        logging.debug("Waiting for container...")
        while not is_container_ready(CONTAINER_ID):
            sleep(SLEEP_DELAY)
        logging.debug("Checking started services...")
        while not (init_services_list := get_checked_json_file(CONTAINER_ID)):
            sleep(SLEEP_DELAY)
    else:
        init_services_list = {'services': SERVICES}

    logging.debug("Waiting for services availability...")
    while not are_ready_subscribers(init_services_list["services"]):
        sleep(SLEEP_DELAY)

    EXIT_CODE = 0


def main():
    """Manage the script"""
    global TIMEOUT, HOST, PORT, CONTAINER_ID, SERVICES, TOKEN
    parser = argparse.ArgumentParser(
        description="OpenTestFactory Orchestrator availability checker"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--container_id", help="docker id of the container to check")

    group.add_argument("--services", help="comma-separated list of expected services")

    parser.add_argument(
        "--timeout",
        help="verification timeout in seconds (default to 3600)",
        default=3600,
        type=int,
    )

    parser.add_argument(
        "--host",
        help="target host with protocol (e.g. https://example.local)",
        required=True,
    )

    parser.add_argument(
        "--port",
        help="target port (eventbus, default to 38368)",
        default=38368,
        type=int,
    )

    parser.add_argument(
        "--token",
        help="token",
        required=True,
    )

    parser.add_argument(
        '--debug', help='whether to log debug information.', action='store_true'
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    CONTAINER_ID = args.container_id

    if CONTAINER_ID:
        try:
            import docker
        except ModuleNotFoundError:
            print(
                "Module 'docker' not found.  Please ensure it is installed (use 'pip install docker' to install it)."
            )
            sys.exit(2)
    else:
        SERVICES = args.services.split(',')

    TIMEOUT = args.timeout
    HOST = args.host
    PORT = args.port
    TOKEN = args.token

    thread = threading.Thread(target=wait_till_ready, daemon=True)
    thread.start()
    try:
        thread.join(timeout=TIMEOUT)
    except KeyboardInterrupt:
        sys.exit(1)
    if EXIT_CODE == 1:
        logging.error('Timeout exceeded.')
    logging.debug("exiting with code %d", EXIT_CODE)
    sys.exit(EXIT_CODE)


if __name__ == "__main__":
    main()
