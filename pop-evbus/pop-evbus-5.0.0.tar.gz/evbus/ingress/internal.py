import asyncio

"""
To use the internal queues, specify profile names for which queues should be created

.. code-block:: sls

    internal:
      default:
      my_profile:
      my_other_profile:
"""


def __init__(hub):
    hub.ingress.internal.QUEUE = {}
    hub.ingress.internal.ACCT = ["internal"]


async def get(hub, routing_key: str):
    if routing_key not in hub.ingress.internal.QUEUE:
        hub.ingress.internal.QUEUE[routing_key] = asyncio.Queue()
    return hub.ingress.internal.QUEUE[routing_key]


async def publish(hub, ctx, routing_key: str, body: str):
    # initialize the queue with the current loop
    channel = await hub.ingress.internal.get(routing_key)
    await channel.put(body)
