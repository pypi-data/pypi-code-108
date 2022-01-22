from enum import Enum


class ParamType(str, Enum):
    """Resulting status of some action."""

    body = "body"
    query = "query"
    params = "params"
    cookies = "cookies"
    headers = "headers"

    def __str__(self) -> str:
        return self.value
