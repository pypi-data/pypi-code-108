from localstack_ext import __version__

# version of localstack-ext
# TODO deprecated - use localstack-ext.__version__ instead
VERSION = __version__

# default expiry seconds for Cognito access tokens
TOKEN_EXPIRY_SECONDS = 24 * 60 * 60

# name of Docker registry for Lambda images
DEFAULT_LAMBDA_DOCKER_REGISTRY = "localstack/lambda"

# Github repo with various code artifacts
# TODO: remove and use the upstream constant from install.py
ARTIFACTS_REPO = "https://github.com/localstack/localstack-artifacts"

# request path for local pod management API
API_PATH_PODS = "/_pods"
