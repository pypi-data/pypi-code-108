from biolib.typing_utils import TypedDict, Any


class Proxy(TypedDict):
    container: Any
    hostname: str
    ip: str
