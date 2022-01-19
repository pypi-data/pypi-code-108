# https://aio-pika.readthedocs.io/en/latest/rabbitmq-tutorial/1-introduction.html
import aio_pika


def __init__(hub):
    hub.ingress.pika.ACCT = ["pika", "amqp", "rabbitmq"]


async def publish(hub, ctx, routing_key: str, body: str):
    """
    Any of the options for aio_pika.connect_robust are acceptable parameters for the profile:

    .. code-block:: sls

        pika:
          my_profile:
            connection:
              url:
              host: localhost
              port: 5672
              login: guest
              password: guest
              virtualhost: /
              ssl: False,
              ssl_options:
              client_properties:
            exchange: default
            timeout: None

    """
    if isinstance(body, str):
        body = body.encode()
    message = aio_pika.Message(body)

    exchange_type: str = ctx.acct.get("exchange", "default")

    connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
        loop=hub.pop.loop.CURRENT_LOOP, **ctx.acct.connection
    )

    channel: aio_pika.Channel
    async with await connection.channel() as channel:
        if exchange_type == "default":
            exchange = channel.default_exchange
        else:
            exchange = await channel.get_exchange(exchange_type, ensure=True)
        await exchange.publish(
            message, routing_key=routing_key, timeout=ctx.acct.get("timeout")
        )
