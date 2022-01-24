import os
import re

from localstack import config as localstack_config
from localstack import constants as localstack_constants
from localstack.constants import LOCALHOST_HOSTNAME
from localstack.utils.docker_utils import DOCKER_CLIENT

FALSE_STRINGS = localstack_constants.FALSE_STRINGS

ROOT_FOLDER = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

PROTECTED_FOLDERS = ("services", "utils")

# api server config
API_URL = localstack_constants.API_ENDPOINT

# localhost IP address and hostname
LOCALHOST_IP = "127.0.0.1"

# base domain name used for endpoints of created resources (e.g., CloudFront distributions)
RESOURCES_BASE_DOMAIN_NAME = (
    os.environ.get("RESOURCES_BASE_DOMAIN_NAME", "").strip() or LOCALHOST_HOSTNAME
)

# bind address of local DNS server
DNS_ADDRESS = os.environ.get("DNS_ADDRESS") or "0.0.0.0"

# IP address that AWS endpoints should resolve to in our local DNS server. By default,
# hostnames resolve to 127.0.0.1, which allows to use the LocalStack APIs transparently
# from the host machine. If your code is running in Docker, this should be configured
# to resolve to the Docker bridge network address, e.g., DNS_RESOLVE_IP=172.17.0.1
DNS_RESOLVE_IP = os.environ.get("DNS_RESOLVE_IP") or LOCALHOST_IP

# fallback DNS server to send upstream requests to
DNS_SERVER = os.environ.get("DNS_SERVER")
DNS_VERIFICATION_DOMAIN = os.environ.get("DNS_VERIFICATION_DOMAIN") or "localstack.cloud"

# SMTP settings (required, e.g., for Cognito)
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "")

# whether to automatically start up utility containers (e.g., Spark/Hadoop for EMR, Presto for Athena)
AUTOSTART_UTIL_CONTAINERS = localstack_config.is_env_true("AUTOSTART_UTIL_CONTAINERS")

# optional flags to pass when starting the bigdata Docker container
BIGDATA_DOCKER_FLAGS = (os.environ.get("BIGDATA_DOCKER_FLAGS") or "").strip()

# optional predefined hostname to use to connect from main container to localstack_bigdata container
BIGDATA_HOST_FROM_MAIN = (os.environ.get("BIGDATA_HOST_FROM_MAIN") or "").strip()

# Comma-separated list of regex patterns for DNS names to resolve locally.
# Any DNS name not matched against any of the patterns on this whitelist
# will resolve to the real DNS entry, rather than the local one.
DNS_LOCAL_NAME_PATTERNS = (os.environ.get("DNS_LOCAL_NAME_PATTERNS") or "").strip()

# whether to transparently set the target endpoint (by passing $AWS_ENDPOINT_URL) in
#  AWS SDK clients used in user code (e.g., Lambdas). default: true
TRANSPARENT_LOCAL_ENDPOINTS = localstack_config.is_env_not_false("TRANSPARENT_LOCAL_ENDPOINTS")

# whether to use static ports and IDs (e.g., cf-<port>) for CloudFormation distributions
CLOUDFRONT_STATIC_PORTS = localstack_config.is_env_true("CLOUDFRONT_STATIC_PORTS")

# whether to start the EC2 daemon on the host (which requires sudo privileges)
EC2_AUTOSTART_DAEMON = localstack_config.is_env_true("EC2_AUTOSTART_DAEMON")

# whether to enforce IAM policies when processing requests
ENFORCE_IAM = localstack_config.is_env_true("ENFORCE_IAM")

# whether to fully initialize XRay daemon for Lambda (increases Lambda startup times, hence disabled by default)
LAMBDA_XRAY_INIT = localstack_config.is_env_true("LAMBDA_XRAY_INIT")

# folder with persistent API backend states
BACKEND_STATES_DIR = os.path.join(localstack_config.dirs.data, "api_states")

# whether to enable extended persistence, storing "all" state like Lambda function code, etc
PERSIST_ALL = localstack_config.is_env_not_false("PERSIST_ALL")

# whether to require Pro features and exit with a fault if the API key cannot be activated
REQUIRE_PRO = localstack_config.is_env_true("REQUIRE_PRO")

# endpoint URL for kube cluster (defaults to https://<docker_bridge_ip>:6443)
KUBE_ENDPOINT = os.environ.get("KUBE_ENDPOINT", "")


def use_custom_dns():
    return str(DNS_ADDRESS) not in FALSE_STRINGS


# backend service ports
DEFAULT_PORT_LOCAL_DAEMON = 4600
DEFAULT_PORT_LOCAL_DAEMON_ROOT = 4601

# port for Azure APIs
PORT_AZURE = 12121

# add default service ports (TODO needed?)
localstack_constants.DEFAULT_SERVICE_PORTS["azure"] = PORT_AZURE

# name of CI project to sync usage events and state with
CI_PROJECT = os.environ.get("CI_PROJECT") or ""

# Controls the snapshot granularity of the run. The lower the interval, the more snapshot metamodels are created
COMMIT_INTERVAL_SECS = os.environ.get("COMMIT_INTERVAL_SECS", 10)

# Controls the synchronization rate of the run. The lower the rate, the more remote synchronization requests are performed.
#  Note: If the container shuts down gracefully a synchronization request is done at the very end of the run, otherwise
#   all results up until the last synchronization request are lost.
SYNCHRONIZATION_RATE = os.environ.get("SYNCHRONIZATION_RATE", 1)

# Docker host name resolvable from containers
DOCKER_HOST_NAME = "host.docker.internal"

# Port where Hive/metastore/Spark are available for EMR/Athena
PORT_HIVE_METASTORE = 9083
PORT_HIVE_SERVER = 10000
PORT_SPARK_MASTER = 7077
PORT_SPARK_UI = 4040

# Additional flags provided to the batch container
# only flags for volumes, ports, environment variables and add-hosts are allowed
BATCH_DOCKER_FLAGS = os.environ.get("BATCH_DOCKER_FLAGS", "")

if localstack_config.DOCKER_HOST_FROM_CONTAINER == DOCKER_HOST_NAME:
    # special case when we're running tests outside of Docker
    if not localstack_config.in_docker():
        image_name = localstack_constants.DOCKER_IMAGE_NAME
        try:
            out, _ = DOCKER_CLIENT.run_container(
                image_name,
                remove=True,
                entrypoint="",
                command=["bash", "-c", "ping -c 1 %s" % DOCKER_HOST_NAME],
            )
            out = out.decode(localstack_config.DEFAULT_ENCODING) if isinstance(out, bytes) else out
            ip = re.match(r"PING[^\(]+\(([^\)]+)\).*", out, re.MULTILINE | re.DOTALL)
            ip = ip and ip.group(1)
            if ip:
                localstack_config.DOCKER_HOST_FROM_CONTAINER = ip
        except Exception:
            # Swallow this error - Docker daemon potentially not running?
            pass

# update variable names that need to be passed as arguments to Docker
localstack_config.CONFIG_ENV_VARS += [
    "AUTOSTART_UTIL_CONTAINERS",
    "AZURE",
    "BIGDATA_DOCKER_FLAGS",
    "CI_PROJECT",
    "CLOUDFRONT_STATIC_PORTS",
    "DNS_ADDRESS",
    "DNS_LOCAL_NAME_PATTERNS",
    "DNS_RESOLVE_IP",
    "DNS_SERVER",
    "ENFORCE_IAM",
    "KUBE_ENDPOINT",
    "LAMBDA_XRAY_INIT",
    "LOG_LICENSE_ISSUES",
    "PERSIST_ALL",
    "REQUIRE_PRO",
    "SMTP_EMAIL",
    "SMTP_HOST",
    "SMTP_PASS",
    "SMTP_USER",
    "SYNC_POD_NAME",
    "TRANSPARENT_LOCAL_ENDPOINTS",
]

# re-initialize configs in localstack
localstack_config.populate_configs()
