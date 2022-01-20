import typing

from elasticsearch_dsl import connections
from redis import Redis
from wisdoms_dapr.elasticsearch import ElasticsearchConnectionConfig, create_elasticsearch_connection


def get_es(conf: typing.Union[dict[str, typing.Any], ElasticsearchConnectionConfig]) -> typing.Callable:
    """Get Elasticsearch Connection

    conf:
        hosts: http url[s]
        auth:
            username: str
            password: str
        timeout: int
        **kwargs: es kwargs

    raise: connection exceptions
    """

    def _get_es() -> connections.Elasticsearch:
        return create_elasticsearch_connection(config=conf)

    return _get_es


def get_redis(conf: dict[str, typing.Any]) -> typing.Callable[..., Redis]:
    """
    Get Redis Connection

    conf: package redis.Redis init kwargs
    raise: redis connection exception
    """
    db = None

    def _get_redis() -> Redis:
        nonlocal db
        if db is None:
            db = Redis(**conf)

        return db

    return _get_redis
