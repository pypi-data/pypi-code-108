import json

__virtualname__ = "json"


def _default(data):
    if isinstance(data, set):
        return sorted(data)
    elif hasattr(data, "__iter__"):
        return list(data)
    else:
        return repr(data)


def apply(hub, data) -> str:
    return json.dumps(data, default=_default)
