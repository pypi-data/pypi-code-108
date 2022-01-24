import pydantic


class PubSubConfig(pydantic.BaseModel):
    """
    Configuration for ``CacheDatabase`` instances.

    type : str
        The database type.
    host : str
        The database host address.
    port : int
        The database port.
    schema_registry : bool
        Confluentinc schema registry url.
    topic_filter : list
        List of topic filters separated by comma.
    """

    type: str = "kafka"
    bootstrap_servers: str = "localhost:9092"
    security_protocol: str = "PLAINTEXT"
    schema_registry: str = "http://localhost:8081"
    topic_filter: str = "*"
