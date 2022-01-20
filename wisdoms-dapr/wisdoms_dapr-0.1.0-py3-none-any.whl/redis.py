import typing
from pydantic import BaseModel


class RedisConnectionConfig(BaseModel):
    """Redis Connection Configuration"""

    host: str = '127.0.0.1'
    port: int = 6379
    db: int = 0
    password: typing.Optional[str] = None
    decode_responses: bool = False

    # No Common Options
    socket_timeout: typing.Optional[int] = None
    socket_connect_timeout: typing.Optional[int] = None
    encoding = "utf-8"
    encoding_errors = "strict"
    retry_on_timeout: bool = False
    retry_on_error: list[str] = []
    ssl: bool = False
    ssl_ca_certs: typing.Optional[str] = None
    max_connections: typing.Optional[int] = None
    single_connection_client = False
    health_check_interval = 0
