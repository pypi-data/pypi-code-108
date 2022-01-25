import os
from urllib.parse import urlparse

from importlib_metadata import version, PackageNotFoundError

# try fetching version, if it fails (usually when in dev), add default
from biolib.biolib_logging import logger

try:
    BIOLIB_PACKAGE_VERSION = version('pybiolib')
except PackageNotFoundError:
    BIOLIB_PACKAGE_VERSION = '0.0.0'

IS_DEV = os.getenv('BIOLIB_DEV', '').upper() == 'TRUE'

BIOLIB_PACKAGE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

BIOLIB_CLOUD_ENVIRONMENT = os.getenv('BIOLIB_CLOUD_ENVIRONMENT', '').lower()

BIOLIB_IS_RUNNING_IN_ENCLAVE = BIOLIB_CLOUD_ENVIRONMENT == 'enclave'

IS_RUNNING_IN_CLOUD = BIOLIB_CLOUD_ENVIRONMENT in ('enclave', 'non-enclave')

if BIOLIB_CLOUD_ENVIRONMENT and not IS_RUNNING_IN_CLOUD:
    logger.warning((
        'BIOLIB_CLOUD_ENVIRONMENT defined but does not specify the cloud environment correctly. ',
        'The compute node will not act as a cloud compute node'
    ))

BIOLIB_CLOUD_SKIP_PCR_VERIFICATION = os.getenv('BIOLIB_CLOUD_SKIP_PCR_VERIFICATION', '').upper() == 'TRUE'

BIOLIB_ENABLE_DNS_PROXY = os.getenv('BIOLIB_ENABLE_DNS_PROXY', '').upper() == 'TRUE'

RUN_DEV_JOB_ID = 'run-dev-mocked-job-id'


def get_absolute_container_image_uri(base_url: str, relative_image_uri: str, job_is_federated: bool= False):
    if base_url == 'https://biolib.com' or job_is_federated:
        container_registry_hostname = 'containers.biolib.com'
    elif base_url in ('https://staging-elb.biolib.com', 'https://staging.biolib.com'):
        container_registry_hostname = 'containers.staging.biolib.com'
    else:
        # Expect registry to be accessible on the hostname of base_url if not running on biolib.com
        base_hostname = urlparse(base_url).hostname
        if not base_hostname:
            raise Exception("Could not get hostname from base_url. Tried to get ecr_proxy_uri for image pulling.")
        container_registry_hostname = base_hostname

    return f'{container_registry_hostname}/{relative_image_uri}'
