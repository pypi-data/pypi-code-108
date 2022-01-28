import msgpack

__virtualname__ = "msgpack"


def apply(hub, data) -> str:
    return msgpack.dumps(data)
