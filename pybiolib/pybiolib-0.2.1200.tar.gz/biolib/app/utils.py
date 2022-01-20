import logging
import os
import sys
import random
import subprocess
import time
import pathlib

import requests.exceptions

from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_api_client.biolib_job_api import BiolibJobApi
from biolib.biolib_binary_format import ModuleOutput
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger


# TODO: type return value as ModuleOutput class
def run_job(job, module_input_serialized: bytes):
    host = '127.0.0.1'
    port = str(random.choice(range(5000, 65000)))
    node_url = f'http://{host}:{port}'
    job_id = job['public_id']
    logger.debug(f'Starting local compute node at {node_url}')
    start_cli_path = pathlib.Path(__file__).parent.parent.resolve() / 'start_cli.py'
    python_executable_path = sys.executable
    compute_node_process = subprocess.Popen(
        args=[python_executable_path, start_cli_path, 'start', '--host', host, '--port', port],
        env=dict(os.environ, BIOLIB_LOG=logging.getLevelName(logger.level)),
    )
    try:
        for retry in range(20):
            time.sleep(1)
            try:
                BiolibJobApi.save_compute_node_job(
                    job=job,
                    module_name='main',
                    access_token=BiolibApiClient.get().access_token,
                    node_url=node_url
                )
                break

            except requests.exceptions.ConnectionError:
                if retry == 19:
                    raise BioLibError('Could not connect to local compute node') from None
                logger.debug('Could not connect to local compute node retrying...')

        BiolibJobApi.start_cloud_job(job_id, module_input_serialized, node_url)
        BiolibJobApi.await_compute_node_status(
            retry_interval_seconds=1.5,
            retry_limit_minutes=30,
            status_to_await='Result Ready',
            compute_type='Compute Node',
            node_url=node_url,
            job=job,
        )

        result = BiolibJobApi.get_cloud_result(job_id, node_url)
        return ModuleOutput(result).deserialize()

    finally:
        compute_node_process.terminate()
