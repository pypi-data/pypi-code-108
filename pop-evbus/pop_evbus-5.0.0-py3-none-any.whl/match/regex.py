import re


def find(hub, name: str, pattern: str) -> bool:
    return bool(re.fullmatch(pattern, name))
