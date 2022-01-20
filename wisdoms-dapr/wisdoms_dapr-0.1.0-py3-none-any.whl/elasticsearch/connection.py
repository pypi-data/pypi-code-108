import typing

from elasticsearch_dsl.connections import Elasticsearch, create_connection, get_connection
from pydantic import BaseModel, Field


class ElasticsearchConnectionConfig(BaseModel):
    class AuthConfig(BaseModel):
        username: str
        password: str

    hosts: typing.Union[str, list[str]]
    auth: typing.Optional[AuthConfig]
    timeout: float = Field(12, ge=3)


def create_elasticsearch_connection(
    config: typing.Union[dict[str, typing.Any], ElasticsearchConnectionConfig], *, alias: str = 'default'
) -> Elasticsearch:
    """Create Elasticsearch Connection"""

    if isinstance(config, ElasticsearchConnectionConfig):
        config = config.dict()

    try:
        return get_connection(alias=alias)
    except KeyError:
        auth = None
        if isinstance(config.get('auth'), dict) and config['auth'].get('username') and config['auth'].get('password'):
            auth = config.pop('auth')
            auth = (auth['username'], auth['password'])

        return create_connection(http_auth=auth, **config)
