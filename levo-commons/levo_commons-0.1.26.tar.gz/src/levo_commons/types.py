from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Tuple, Union

PathLike = Union[Path, str]

Query = Dict[str, Any]
# Body can be of any Python type that corresponds to JSON Schema types + `bytes`
Body = Union[List, Dict[str, Any], str, int, float, bool, bytes]
PathParameters = Dict[str, Any]
Headers = Dict[str, Any]
Cookies = Dict[str, Any]
FormData = Dict[str, Any]


class NotSet:
    pass


# A filter for path / method
Filter = Union[str, List[str], Tuple[str], Set[str], NotSet]

RawAuth = Tuple[str, str]
# Generic test with any arguments and no return
GenericTest = Callable[..., None]
