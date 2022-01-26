import base64
import time
import sys
import requests

from biolib.biolib_api_client.auth import BearerAuth
from biolib.biolib_api_client import BiolibApiClient, Job
from biolib.biolib_binary_format import AesEncryptedPackage
from biolib.biolib_binary_format.stdout_and_stderr import StdoutAndStderr
from biolib.biolib_errors import BioLibError
from biolib.compute_node.utils import SystemExceptionCodeMap
from biolib.biolib_logging import logger
from biolib.utils import BIOLIB_PACKAGE_VERSION
from biolib.typing_utils import List


class RetryException(Exception):
    pass


class BiolibJobApi:

    @staticmethod
    def create(app_version_id, caller_job=None):
        data = {
            'app_version_id': app_version_id,
            'client_type': 'biolib-python',
            'client_version': BIOLIB_PACKAGE_VERSION,
        }
        if caller_job:
            data['caller_job'] = caller_job

        response = requests.post(
            f'{BiolibApiClient.get().base_url}/api/jobs/',
            auth=BearerAuth(BiolibApiClient.get().access_token),
            json=data,
        )

        # TODO: Error handling with response object
        if not response.ok:
            raise BioLibError(response.content)

        return response.json()

    @staticmethod
    def update_state(job_id, state):
        response = requests.patch(
            f'{BiolibApiClient.get().base_url}/api/jobs/{job_id}/',
            json={'state': state},
            auth=BearerAuth(BiolibApiClient.get().access_token)
        )

        # TODO: Error handling with response object
        if not response.ok:
            raise BioLibError(response.content)

        return response.json()

    @staticmethod
    def create_cloud_job(module_name, job_id):
        response = None
        for retry in range(4):
            try:
                response = requests.post(
                    f'{BiolibApiClient.get().base_url}/api/jobs/cloud/',
                    json={'module_name': module_name, 'job_id': job_id},
                    auth=BearerAuth(BiolibApiClient.get().access_token)
                )

                if response.status_code == 503:
                    raise RetryException(response.content)
                # Handle possible validation errors from backend
                elif not response.ok:
                    raise BioLibError(response.text)

                break

            except RetryException as retry_exception:  # pylint: disable=broad-except
                if retry > 3:
                    raise BioLibError('Reached retry limit for cloud job creation') from retry_exception
                time.sleep(1)

        if not response:
            raise BioLibError('Could not create new cloud job')

        cloud_job = response.json()
        if cloud_job.get('is_compute_node_ready', False):
            return cloud_job

        max_retry_attempts = 25
        retry_interval_seconds = 10

        for _ in range(max_retry_attempts):
            response = requests.get(
                f'{BiolibApiClient.get().base_url}/api/jobs/cloud/{cloud_job["public_id"]}/status/',
                auth=BearerAuth(BiolibApiClient.get().access_token)
            )
            cloud_job = response.json()
            if cloud_job.get('is_compute_node_ready', False):
                return cloud_job

            logger.info('Cloud: Reserved compute node not ready, retrying...')
            time.sleep(retry_interval_seconds)

        raise BioLibError('Cloud: The reserved compute node was not ready in time')

    @staticmethod
    def save_compute_node_job(job, module_name, access_token, node_url):
        response = requests.post(
            f'{node_url}/v1/job/',
            json={'module_name': module_name, 'job': job, 'access_token': access_token}
        )

        if not response.ok:
            raise BioLibError(response.content)

        return response.json

    @staticmethod
    def start_cloud_job(job_id, module_input_serialized, node_url):
        response = requests.post(
            f'{node_url}/v1/job/{job_id}/start/',
            data=module_input_serialized
        )

        if not response.ok:
            raise BioLibError(response.content)

    @staticmethod
    def await_compute_node_status(
            retry_interval_seconds: float,
            retry_limit_minutes: float,
            status_to_await: str,
            compute_type: str,
            node_url: str,
            job: Job,
            aes_key_buffer=None,
    ):
        status_max_retry_attempts = int(retry_limit_minutes * 60 / retry_interval_seconds)
        status_is_reached = False
        final_status_messages: List[str] = []

        for _ in range(status_max_retry_attempts):
            response = requests.get(f'{node_url}/v1/job/{job["public_id"]}/status/')
            if not response.ok:
                raise Exception(response.content)

            status_json = response.json()

            for status_update in status_json['status_updates']:
                if status_update.get('log_message') == status_to_await:
                    status_is_reached = True

                # If the status is reached print the log messages after all stdout and stderr has been written
                if status_is_reached:
                    final_status_messages.append(status_update['log_message'])
                else:
                    # Print the status before writing stdout and stderr
                    logger.info(f'{compute_type}: {status_update["log_message"]}')

            app_version =  job['app_version']
            if 'stdout_and_stderr_packages_b64' in status_json and \
                    (app_version.get('main_output_file') or app_version.get('stdout_render_type') == 'text'):
                for stdout_and_stderr_package_b64 in status_json['stdout_and_stderr_packages_b64']:
                    stdout_and_stderr_package = base64.b64decode(stdout_and_stderr_package_b64)
                    if aes_key_buffer:
                        stdout_and_stderr_package = AesEncryptedPackage(stdout_and_stderr_package).decrypt(
                            aes_key_buffer
                        )

                    stdout_and_stderr = StdoutAndStderr(stdout_and_stderr_package).deserialize()

                    sys.stdout.write(stdout_and_stderr.decode())
                    sys.stdout.flush()

            if 'error_code' in status_json:
                error_code = status_json['error_code']
                error_message = SystemExceptionCodeMap.get(error_code, f'Unknown error code {error_code}')

                raise BioLibError(f'{compute_type}: {error_message}')

            if status_is_reached:
                # Print the final log message after stdout and stderr has been written
                for message in final_status_messages:
                    logger.info(f'{compute_type}: {message}')

                return

            time.sleep(retry_interval_seconds)

        raise BioLibError(f'{compute_type}: Failed to get results: Retry limit exceeded')

    @staticmethod
    def get_cloud_result(job_id, node_url):
        response = requests.get(
            f'{node_url}/v1/job/{job_id}/result/',
        )

        if not response.ok:
            raise Exception(response.content)

        return response.content

    @staticmethod
    def get_enclave_json(biolib_base_url):
        response = requests.get(
            f'{biolib_base_url}/info-files/biolib-enclave.json',
        )
        return response.json()
