import aiokafka


def __init__(hub):
    hub.ingress.kafka.ACCT = ["kafka"]


__virtualname__ = "kafka"


async def publish(hub, ctx, routing_key: str, body: str):
    """
    Profile Example:

    .. code-block:: yaml

        kafka:
          profile_name:
            partition:
            key:
            connection:
              bootstrap_servers:
                - 'localhost:9092'
              client_id:
              acks: 1
              compression_type:
              max_batch_size: 16384
              linger_ms: 0
              connections_max_idle_ms: 9 * 60 * 1000
              max_request_size: 1048576
              retry_backoff_ms: 100
              request_timeout_ms: 30000
              security_protocol: PLAINTEXT
              ssl_context:
              api_version: auto
              sasl_mechanism: PLAIN
              sasl_plain_username:
              sasl_plain_password:
    """
    async with aiokafka.AIOKafkaProducer(
        **ctx.acct.connection, loop=hub.pop.loop.CURRENT_LOOP
    ) as connection:
        return await connection.send_and_wait(
            topic=routing_key,
            value=body.encode(),
            partition=ctx.acct.get("partition", None),
            key=ctx.acct.get("key", None),
        )
