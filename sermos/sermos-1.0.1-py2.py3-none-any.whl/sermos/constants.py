""" Sermos Constants
"""
import os
from urllib.parse import urljoin

API_PATH_V1 = '/api/v1'

DEFAULT_RESULT_TTL = 86400  # seconds (1 day)
DEFAULT_TASK_TTL = 60  # seconds (1 minute)
DEFAULT_RETRY_TASK_MAX_TTL = 300
DEFAULT_MAX_RETRY = 10
DEFAULT_REGULATOR_TASK = 'sermos.celery.task_chain_regulator'
DEFAULT_SUCCESS_TASK = 'sermos.celery.pipeline_success'
DEFAULT_RETRY_TASK = 'sermos.celery.pipeline_retry'

CHAIN_SUCCESS_MSG = 'Chain built successfully ...'
CHAIN_FAILURE_MSG = 'Chain failed to build ...'

PIPELINE_RUN_WRAPPER_CACHE_KEY = 'sermos_{}_{}'  # pipeline_id + execution_id
PIPELINE_RESULT_CACHE_KEY = 'sermos_result_{}'  # execution_id

# Pipeline configurations and scheduled task configuration are cached in Redis
# temporarily (default to CONFIG_REFRESH_RATE (in seconds)).
# Each pipeline config/schedule config is specific to an individual deployment,
# however, we cache only with the pipeline_id here because the usage of this
# cache key is restricted to the redis instance associated with the deployment.
PIPELINE_CONFIG_CACHE_KEY = 'sermos_pipeline_config_{}'  # pipeline_id
SCHEDULE_CONFIG_CACHE_KEY = 'sermos_schedule_config'
CONFIG_REFRESH_RATE = int(os.environ.get('CONFIG_REFRESH_RATE', 30))  # seconds

# TODO where on earth is this crazy time format coming from?
SCHEDULE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

AUTH_LOCK_KEY = os.environ.get('AUTH_LOCK_KEY', 'sermos-auth-lock')
AUTH_LOCK_DURATION = int(os.environ.get('AUTH_LOCK_DURATION', 30))

STORED_MODEL_KEY = '{}_{}{}'

# Yaml path is relative to package
SERMOS_YAML_PATH = os.environ.get('SERMOS_YAML_PATH', 'sermos.yaml')
SERMOS_ACCESS_KEY = os.environ.get('SERMOS_ACCESS_KEY', None)
SERMOS_CLIENT_PKG_NAME = os.environ.get('SERMOS_CLIENT_PKG_NAME', None)
SERMOS_DEPLOYMENT_ID = os.environ.get('SERMOS_DEPLOYMENT_ID', 'local')
LOCAL_DEPLOYMENT_VALUE = os.environ.get('LOCAL_DEPLOYMENT_VALUE', 'local')
DEFAULT_BASE_URL = os.environ.get('SERMOS_BASE_URL', 'https://console.sermos.ai')
if DEFAULT_BASE_URL != 'local':
    DEFAULT_BASE_URL += '/api/v1/'
DEPLOYMENTS_URL = "{}deployments/{}"
DEPLOYMENTS_DEPLOY_URL = "{}deployments/{}/deploy"
DEPLOYMENTS_SERVICES_URL = "{}deployments/{}/services"
DEPLOYMENTS_SERVICE_URL = "{}deployments/{}/services/{}"
PROXY_SERVICE_URL = "{}deployments/{}/proxy-token/{}"
DEFAULT_AUTH_URL = urljoin(DEFAULT_BASE_URL, 'auth')
USING_SERMOS_CLOUD = DEFAULT_BASE_URL != LOCAL_DEPLOYMENT_VALUE
DEFAULT_CONFIG_RETRIEVAL_PAGE_SIZE = 25
# Default 'responses' dictionary when decorating endpoints with @api.doc()
# Extend as necessary.
API_DOC_RESPONSES = {
    200: {
        'code': 200,
        'description': 'Successful response.'
    },
    400: {
        'code': 400,
        'description': 'Malformed request. Verify payload is correct.'
    },
    401: {
        'code': 401,
        'description':
        'Unauthorized. Verify your API Key (`accesskey`) header.'
    }
}

# Default 'params' dictionary when decorating endpoints with @api.doc()
# Extend as necessary.
API_DOC_PARAMS = {
    'accesskey': {
        'in': 'header',
        'name': 'accesskey',
        'description': 'Your API Consumer\'s `accesskey`',
        'type': 'string',
        'required': True
    }
}

DEFAULT_OPENAPI_CONFIG = (
    ('SWAGGER_UI_DOC_EXPANSION',
     'list'), ('API_DOCUMENTATION_TITLE',
               'Sermos API Specs'), ('API_DOCUMENTATION_DESCRIPTION',
                                     'Available API Endpoints'),
    ('OPENAPI_VERSION', '3.0.2'), ('OPENAPI_URL_PREFIX',
                                   '/api/v1'), ('OPENAPI_SWAGGER_APP_NAME',
                                                'Sermos - API Reference'),
    ('OPENAPI_SWAGGER_UI_PATH',
     '/docs'), ('OPENAPI_SWAGGER_BASE_TEMPLATE',
                'swagger/swagger_ui.html'), ('OPENAPI_SWAGGER_URL', '/docs'),
    ('OPENAPI_SWAGGER_UI_URL',
     'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/'),
    ('EXPLAIN_TEMPLATE_LOADING', False))

# Rho Auth settings
DEFAULT_RHOAUTH_CONFIG = (
    ('RHOAUTH_OIDC_CLIENT_ID',
     os.environ.get('RHOAUTH_OIDC_CLIENT_ID',
                    os.environ.get('CLIENT_PKG_NAME', '').replace('_', '-'))),
    ('RHOAUTH_OIDC_ISSUER',
     os.environ.get('RHOAUTH_OIDC_ISSUER',
                    'https://auth.rho.ai/auth/realms/sermos')),
    ('RHOAUTH_OIDC_AUTH_ENDPOINT',
     os.environ.get(
         'RHOAUTH_OIDC_AUTH_ENDPOINT',
         'https://auth.rho.ai/auth/realms/sermos/protocol/openid-connect/auth')
     ),
    ('RHOAUTH_OIDC_TOKEN_ENDPOINT',
     os.environ.get(
         'RHOAUTH_OIDC_TOKEN_ENDPOINT',
         'https://auth.rho.ai/auth/realms/sermos/protocol/openid-connect/token'
     )),
    ('RHOAUTH_OIDC_JWKS_URI_ENDPOINT',
     os.environ.get(
         'RHOAUTH_OIDC_JWKS_URI_ENDPOINT',
         'https://auth.rho.ai/auth/realms/sermos/protocol/openid-connect/certs'
     )),
    ('RHOAUTH_OIDC_END_SESSION_ENDPOINT',
     os.environ.get(
         'RHOAUTH_OIDC_END_SESSION_ENDPOINT',
         'https://auth.rho.ai/auth/realms/sermos/protocol/openid-connect/logout'
     )), ('RHOAUTH_OIDC_END_SESSION_REDIRECT_URI',
          os.environ.get('RHOAUTH_OIDC_END_SESSION_REDIRECT_URI',
                         '/')), ('OAUTHLIB_INSECURE_TRANSPORT',
                                 os.environ.get('OAUTHLIB_INSECURE_TRANSPORT',
                                                1)))


def create_model_key(model_prefix: str,
                     model_version: str,
                     model_postfix: str = ''):
    """ Ensures we're consistently creating the keys for storing/retrieving.
    """
    return STORED_MODEL_KEY.format(model_prefix, model_version, model_postfix)
