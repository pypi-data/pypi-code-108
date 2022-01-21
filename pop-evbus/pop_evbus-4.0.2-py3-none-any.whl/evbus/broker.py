import asyncio
import dataclasses
import queue
from typing import Any
from typing import Dict

import dict_tools.data as data


def __init__(hub):
    # Start off with a synchronous queue
    hub.evbus.BUS = queue.Queue()


@dataclasses.dataclass
class Event:
    profile: str
    routing_key: str
    body: str


async def get(hub):
    bus = await hub.evbus.broker.init()
    return await bus.get()


async def init(hub):
    """
    Initialize the event bus queue in the current loop
    """
    # Once we are running in the context of asyncio, replace the synchronous queue with an async queue
    if isinstance(hub.evbus.BUS, queue.Queue):
        new_bus = asyncio.Queue()
        while not hub.evbus.BUS.empty():
            event = hub.evbus.BUS.get()
            new_bus.put_nowait(event)

        hub.evbus.BUS = new_bus
    return hub.evbus.BUS


async def put(hub, routing_key: str, body: str, profile: str = "default"):
    """
    Put an event on the bus as a single data class
    :param hub:
    :param routing_key: The channel to forward the message body to
    :param body: The message body that will be serialized and put on the bus
    :param profile: The ctx profile name that should be used for this message
    """
    bus: asyncio.Queue = await hub.evbus.broker.init()
    serialized = hub.serialize[hub.serialize.PLUGIN].apply(body)
    await bus.put(Event(routing_key=routing_key, body=serialized, profile=profile))


def put_nowait(hub, routing_key: str, body: str, profile: str = "default"):
    """
    Put an event on the bus as a single data class
    """
    serialized = hub.serialize[hub.serialize.PLUGIN].apply(body)
    hub.evbus.BUS.put_nowait(
        Event(routing_key=routing_key, body=serialized, profile=profile)
    )


async def propagate(
    hub,
    contexts: Dict[str, Any],
    event: Event,
):
    """
    Publish an event to all the ingress queues
    """
    coros = []
    for plugin in hub.ingress:
        # get a list of allowed acct plugins for this publisher
        acct_plugins = getattr(plugin, "ACCT", [])
        if not acct_plugins:
            hub.log.error(
                f"No acct providers specified for ingress.{plugin.name}, specify ACCT providers.  I.E.\n"
                f"def __init__(hub):\n"
                f"    hub.ingress.{plugin.name}.ACCT = ['acceptable_acct_providers']\n"
            )

            continue

        for acct_plugin in acct_plugins:
            provider = contexts.get(acct_plugin, {})
            if event.profile in provider:
                ctx = data.NamespaceDict(acct=provider[event.profile])
                coros.append(
                    plugin.publish(
                        ctx=ctx, routing_key=event.routing_key, body=event.body
                    )
                )

    await asyncio.gather(*coros)
