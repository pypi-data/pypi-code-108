import os
from typing import Union


def read_verify_cert(value: str) -> Union[bool, str]:
    return True if value is None or value == '' or value.lower() == 'true' \
        else False if value.lower() == 'false' \
        else value


tornado_config = dict(
    cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    debug=True,
    port=8999
)

keycloak_config = dict(
    oidc_server_url='{}/realms/{}'.format(os.environ.get('KEYCLOAK_SERVER_URL'), os.environ.get('KEYCLOAK_REALM')),
    client_id=os.environ.get('KEYCLOAK_CLIENT_ID', 'transmart-client'),
    offline_token=os.environ.get('KEYCLOAK_OFFLINE_TOKEN')
)

transmart_config = dict(
    host=os.environ.get('TRANSMART_URL')
)

http_config = dict(
    verify_cert=read_verify_cert(os.environ.get('VERIFY_CERT'))
)

app_config = dict(
    host=os.environ.get('CLIENT_ORIGIN_URL', '*')
)

redis_config = dict(
    url=os.environ.get('REDIS_URL', 'redis://localhost:6379'),
)

task_config = dict(
    data_dir=os.environ.get('DATA_DIR', '/tmp/packer/')
)

celery_config = dict(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Europe/Amsterdam',
    enable_utc=True,
)

logging_config = dict(
    path=os.environ.get('LOG_CFG', 'packer/logging.yaml')
)
