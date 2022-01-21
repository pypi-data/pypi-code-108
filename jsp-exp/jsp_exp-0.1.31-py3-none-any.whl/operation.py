import dataclasses
from typing import Any, List, Optional, Union


@dataclasses.dataclass
class Operation(object):
    processed_by: Union[int, str] = 'Machine'
    name: str = 'Operation'
    r: Optional[int] = None
    p: Optional[int] = None
    q: Optional[int] = None
