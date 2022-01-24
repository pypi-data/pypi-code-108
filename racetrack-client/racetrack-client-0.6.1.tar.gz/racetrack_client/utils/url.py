from urllib.parse import urlsplit


def trim_url(url: str) -> str:
    """Trim trailing slash from the end of URL address"""
    split = urlsplit(url)
    path = split.path
    while path.endswith('/'):
        path = path[:-1]
    split = split._replace(path=path)
    return split.geturl()
