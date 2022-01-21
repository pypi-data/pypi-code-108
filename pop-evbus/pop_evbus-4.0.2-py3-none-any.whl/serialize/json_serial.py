import json

__virtualname__ = "json"


def apply(hub, data) -> str:
    return json.dumps(data)
