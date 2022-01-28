from typing import List


def join_url_path(__a: str, *paths: List[str]) -> str:
    """Join url paths, insert '/' if needed."""
    r = __a
    for p in paths:
        if r[-1:] == "/" and p[:1] == "/":
            r += p[1:]
        elif r[-1:] != "/" and p[:1] != "/":
            r += "/" + p
        else:
            r += p
    return r
