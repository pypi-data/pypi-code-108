import fnmatch


def find(hub, name: str, pattern: str) -> bool:
    return fnmatch.fnmatch(name=name, pat=pattern)
