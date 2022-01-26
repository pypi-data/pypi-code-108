# pylint: disable=unsubscriptable-object

import os
import subprocess
import time
import signal
from multiprocessing import Process
from datetime import datetime
from socket import gethostbyname, gethostname
import requests

from biolib import utils
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger
from biolib.typing_utils import Optional
from biolib.biolib_api_client import BiolibApiClient
from biolib.compute_node.cloud_utils.enclave_parent_types import VsockProxyResponse
from biolib.compute_node.webserver.webserver_types import WebserverConfig, ComputeNodeInfo, ShutdownTimes


class CloudAutoShutdownTimer(Process):
    def __init__(self, seconds_to_wait: int) -> None:
        super().__init__()
        self._seconds_to_wait = seconds_to_wait

    def run(self) -> None:
        time.sleep(self._seconds_to_wait)
        CloudUtils.deregister_and_shutdown()


class _EnclaveUtils:
    _BASE_URL = 'http://127.0.0.1:5005'

    @staticmethod
    def get_webserver_config():
        response = requests.get(f'{_EnclaveUtils._BASE_URL}/config/', timeout=5)
        return response.json()

    @staticmethod
    def deregister_and_shutdown() -> None:
        requests.post(url=f'{_EnclaveUtils._BASE_URL}/deregister_and_shutdown/', timeout=5)

    @staticmethod
    def start_vsock_proxy(hostname: str, port: int) -> VsockProxyResponse:
        remote_host = {'hostname': hostname, 'port': str(port)}
        response = requests.post(url=f'{_EnclaveUtils._BASE_URL}/vsock_proxy/', json=remote_host, timeout=5)
        vsock_proxy: VsockProxyResponse = response.json()
        return vsock_proxy

    @staticmethod
    def stop_vsock_proxy(vsock_proxy_id: str) -> None:
        requests.delete(url=f'{_EnclaveUtils._BASE_URL}/vsock_proxy/{vsock_proxy_id}/', timeout=5)

    @staticmethod
    def log_message_to_log_file(log_message: str, level: int) -> None:
        requests.post(
            url=f'{_EnclaveUtils._BASE_URL}/log/',
            json={
                'log_message': log_message,
                'level': level,
            },
            timeout=5,
        )


class CloudUtils:
    _webserver_config: Optional[WebserverConfig] = None
    enclave = _EnclaveUtils
    _auto_shutdown_timer_pid_file_name: str = '/tmp/biolib_auto_shutdown_timer.pid'

    @staticmethod
    def initialize() -> None:
        logger.debug('Reporting availability...')
        CloudUtils._report_availability()
        CloudUtils.start_auto_shutdown_timer()

    @staticmethod
    def get_webserver_config() -> WebserverConfig:
        if CloudUtils._webserver_config:
            return CloudUtils._webserver_config

        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            CloudUtils._webserver_config = CloudUtils.enclave.get_webserver_config()

        else:
            CloudUtils._webserver_config = WebserverConfig(
                compute_node_info=ComputeNodeInfo(
                    auth_token=CloudUtils._get_environment_variable('BIOLIB_COMPUTE_NODE_AUTH_TOKEN'),
                    public_id=CloudUtils._get_environment_variable('BIOLIB_COMPUTE_NODE_PUBLIC_ID'),
                    ip_address=gethostbyname(gethostname())
                ),
                base_url=CloudUtils._get_environment_variable('BIOLIB_BASE_URL'),
                ecr_region_name=CloudUtils._get_environment_variable('BIOLIB_ECR_REGION_NAME'),
                s3_general_storage_bucket_name=CloudUtils._get_environment_variable(
                    'BIOLIB_S3_GENERAL_STORAGE_BUCKET_NAME'
                ),
                s3_lfs_bucket_name=CloudUtils._get_environment_variable('BIOLIB_S3_LFS_BUCKET_NAME'),
                max_docker_image_cache_size_bytes=CloudUtils._get_environment_variable_as_int(
                    'BIOLIB_MAX_DOCKER_IMAGE_CACHE_SIZE_BYTES'
                ),
                is_dev=CloudUtils._get_environment_variable('BIOLIB_DEV').upper() == 'TRUE',
                shutdown_times=ShutdownTimes(
                    job_max_runtime_shutdown_time_in_seconds=CloudUtils._get_environment_variable_as_int(
                        'BIOLIB_CLOUD_JOB_MAX_RUNTIME_IN_SECONDS'
                    ),
                    auto_shutdown_time_in_seconds=CloudUtils._get_environment_variable_as_int(
                        'BIOLIB_CLOUD_AUTO_SHUTDOWN_TIME_IN_SECONDS'
                    ),
                )
            )

        return CloudUtils._webserver_config

    @staticmethod
    def log(log_message: str, level: int) -> None:
        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            CloudUtils.enclave.log_message_to_log_file(log_message, level)
        else:
            logger.log(level=level, msg=log_message)

    @staticmethod
    def deregister_and_shutdown() -> None:
        logger.debug('Waiting 10 seconds, deregistering and shutting down...')

        # Sleep for 10 seconds to ensure logs are written
        time.sleep(10)

        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            CloudUtils.enclave.deregister_and_shutdown()
        else:
            config = CloudUtils.get_webserver_config()
            try:
                requests.post(url=f'{config["base_url"]}/api/jobs/deregister/', json={
                    'auth_token': config["compute_node_info"]["auth_token"],
                    'public_id': config["compute_node_info"]["public_id"],
                })
            except Exception as error:  # pylint: disable=broad-except
                logger.error(error)

            logger.debug('Shutting down...')
            try:
                subprocess.run(['sudo', 'shutdown', 'now'], check=True)
            except Exception as error:  # pylint: disable=broad-except
                logger.error(error)

    @staticmethod
    def finish_cloud_job(cloud_job_id: str, system_exception_code: Optional[int]) -> None:
        config = CloudUtils.get_webserver_config()
        try:
            requests.post(
                url=f'{config["base_url"]}/api/jobs/cloud/finish/',
                json={
                    'auth_token': config["compute_node_info"]["auth_token"],
                    'cloud_job_id': cloud_job_id,
                    'system_exception_code': system_exception_code,
                },
                timeout=5
            )

        except Exception as error:  # pylint: disable=broad-except
            logger.error(f"Could not finish cloud job with id: {cloud_job_id}")
            logger.error(error)

    @staticmethod
    def start_auto_shutdown_timer() -> None:
        if not utils.IS_RUNNING_IN_CLOUD:
            raise BioLibError('Can not start shutdown timer when not running in cloud.')

        if os.path.exists(CloudUtils._auto_shutdown_timer_pid_file_name):
            logger.debug("Re-starting the auto shutdown timer")
            try:
                pid = int(open(CloudUtils._auto_shutdown_timer_pid_file_name, 'r').read())
                os.kill(pid, signal.SIGTERM)

            except Exception as error:  # pylint: disable=broad-except
                logger.warning(error)
                logger.warning('Could not kill old auto shutdown timer')

        config = CloudUtils.get_webserver_config()
        timer_process = CloudAutoShutdownTimer(
            seconds_to_wait=config['shutdown_times']['auto_shutdown_time_in_seconds']
        )

        timer_process.start()

        with open(CloudUtils._auto_shutdown_timer_pid_file_name, 'w') as pid_file:
            pid_file.write(str(timer_process.pid))

    @staticmethod
    def _report_availability() -> None:
        try:
            config = CloudUtils.get_webserver_config()
            compute_node_info = config['compute_node_info']
            api_client = BiolibApiClient.get()
            logger.debug(f'Registering with {compute_node_info} to host {api_client.base_url} at {datetime.now()}')

            response: Optional[requests.Response] = None
            max_retries = 5
            for retry_count in range(max_retries):
                try:
                    response = requests.post(f'{api_client.base_url}/api/jobs/report_available/',
                                             json=compute_node_info)
                    break
                except Exception as error:  # pylint: disable=broad-except
                    logger.error(f'Self-registering failed with error: {error}')
                    if retry_count < max_retries - 1:
                        seconds_to_sleep = 1
                        logger.info(f'Retrying self-registering in {seconds_to_sleep} seconds')
                        time.sleep(seconds_to_sleep)

            if not response:
                raise BioLibError('Failed to register. Max retry limit reached')

            if response.status_code != 201:
                raise Exception("Non 201 error code")

        except Exception as exception:  # pylint: disable=broad-except
            logger.error(f'Shutting down as self register failed due to: {exception}')
            if not utils.IS_DEV:
                CloudUtils.deregister_and_shutdown()

    @staticmethod
    def _get_environment_variable(key: str) -> str:
        value = os.environ.get(key)
        # Purposely loose falsy check (instead of `is not None`) as empty string should fail
        if not value:
            raise Exception(f'CloudUtils: Missing environment variable "{key}"')

        return value

    @staticmethod
    def _get_environment_variable_as_int(key: str) -> int:
        return int(CloudUtils._get_environment_variable(key))
