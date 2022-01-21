import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.absolute()
CONFIG_FILE = str(Path.home()) + "/.config/configstore/levo.json"
DAF_CLIENT_ID = os.getenv("LEVO_DAF_CLIENT_ID", "aa9hJp2bddyhZeEXjAsura6bWIdSEr5s")
BASE_URL = os.getenv("LEVO_BASE_URL", "https://api.levo.ai")
LEVO_IAM_BASE_URL = os.getenv("LEVO_IAM_BASE_URL", BASE_URL)
TEST_PLANS_GRPC_URL = os.getenv("TEST_PLANS_GRPC_URL", BASE_URL)
TEST_RUNS_SERVICE_URL = os.getenv("TEST_RUNS_SERVICE_URL", BASE_URL) + "/test-runs"
SIGNADOT_BAGGAGE = (
    ("sd-workspace=" + os.getenv("SIGNADOT_WORKSPACE_ID", ""))
    if os.getenv("SIGNADOT_WORKSPACE_ID") is not None
    else None
)
DAF_DOMAIN = os.getenv("LEVO_DAF_DOMAIN", "https://levoai.us.auth0.com")
DAF_GRANT_TYPE = os.getenv(
    "LEVO_DAF_GREANT_TYPE", "urn:ietf:params:oauth:grant-type:device_code"
)
DAF_AUDIENCE = os.getenv("LEVO_DAF_AUDIENCE", "https://api.levo.ai")
DAF_SCOPES = os.getenv("LEVO_DAF_SCOPES", "email offline_access openid")

######################################################################################
# Docker related items
LOCAL_WORK_DIR = "/home/levo/work"
LEVO_CONFIG_DIR = "/home/levo/.config/configstore"
######################################################################################

# Logging related
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()
LOG_HANDLER = os.environ.get("LOG_HANDLER", "stdout").upper()
LOG_BASE_PATH = os.environ.get("LOG_BASE_PATH", Path.home())
LOG_DEFAULT_NAME = os.environ.get("LOG_BASE_NAME", "levocli.log")

# Comma separated list of headers that need to be passed in all API calls to Levo's SaaS.
# Example: "feat: myfeature,workspace_id: workspace1"
LEVO_EXTRA_HEADERS = os.getenv("LEVO_EXTRA_HEADERS", "")


def get_feature_testing_headers():
    """
    Returns a dictionary of feature testing headers.
    """
    headers = {}
    if SIGNADOT_BAGGAGE:
        headers["baggage"] = SIGNADOT_BAGGAGE
    if not LEVO_EXTRA_HEADERS:
        return headers

    for header in LEVO_EXTRA_HEADERS.split(","):
        key, value = header.split(":")
        headers[key] = value

    return headers
