# Copyright 2020 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import requests
import subprocess
from retry import retry

from ebi_eva_common_pyutils.logger import logging_config as log_cfg

logger = log_cfg.get_logger(__name__)


def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def get_available_local_port(try_starting_with_port):
    for i in range(0, 20):
        port_to_try = try_starting_with_port + i
        logger.info("Attempting to forward remote mongo port to local port {0}...".format(port_to_try))
        if is_port_in_use(port_to_try):
            logger.info("Port {0} already in use...".format(port_to_try))
        else:
            return port_to_try
    logger.error("Could not forward to any local port!")


def forward_remote_port_to_local_port(remote_host: str, remote_port: int, local_port: int) -> int:
    port_forward_command = 'ssh -N -L{0}:localhost:{1} {2}'.format(local_port, remote_port, remote_host)
    logger.info("Forwarding port to local port using command: " + port_forward_command)
    proc = subprocess.Popen(port_forward_command.split(" "))
    return proc.pid


@retry(exceptions=(ConnectionError, requests.RequestException), logger=logger,
       tries=4, delay=2, backoff=1.2, jitter=(1, 3))
def json_request(url: str, payload: dict = None, method=requests.get) -> dict:
    """Makes a request of a specified type (by default GET) with the specified URL and payload, attempts to parse the
    result as a JSON string and return it as a dictionary, on failure raises an exception."""
    result = method(url, data=payload)
    result.raise_for_status()
    return result.json()

