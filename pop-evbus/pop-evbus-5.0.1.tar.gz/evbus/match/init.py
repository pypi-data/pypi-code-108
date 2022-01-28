def __init__(hub):
    hub.match.PLUGIN = "glob"


def find(hub, name: str, pattern: str) -> bool:
    return hub.match[hub.match.PLUGIN].find(name, pattern)
