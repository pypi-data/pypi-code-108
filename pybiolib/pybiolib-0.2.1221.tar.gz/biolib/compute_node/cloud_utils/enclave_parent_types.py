from biolib.typing_utils import TypedDict


class VsockProxyResponse(TypedDict):
    hostname: str
    id: str
    port: int
