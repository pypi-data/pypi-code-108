def __init__(hub):
    hub.serialize.PLUGIN = "init"


def apply(hub, data) -> str:
    return str(data)
