__func_alias__ = {"ctx_": "ctx"}
__contracts__ = ["returns", "soft_fail"]


def __init__(hub):
    hub.exec.test.ITEMS = {}
    hub.exec.test.ACCT = ["test"]


def ping(hub):
    return {"result": True, "ret": True}


async def aping(hub):
    return {"result": True, "ret": True}


def ctx_(hub, ctx):
    return {"result": True, "comment": None, "ret": ctx}


def fail(hub):
    raise Exception("Expected failure")


async def afail(hub):
    raise Exception("Expected failure")


def echo(hub, value):
    """
    Return the parameter passed in without changing it at all
    """
    return value


async def aecho(hub, value):
    """
    Return the parameter passed in without changing it at all
    """
    return value


async def event(hub, routing_key: str, body: str, ingress_profile: str = "default"):
    """
    :param routing_key: The ingress channel to publish to
    :param body: The event body
    :param ingress_profile: The ingress profile to allowlist for this event

    .. code-block:: bash

        $ idem exec test.event routing_key body ingress_profile="default" --serialize-plugin="json"
        $ idem exec test.event routing_key="key" body="my_event" ingress_profile="default" --serialize-plugin="json"
    """
    event_kwargs = dict(routing_key=routing_key, body=body, profile=ingress_profile)
    await hub.evbus.broker.put(**event_kwargs)
    return {"result": True, "ret": event_kwargs}
