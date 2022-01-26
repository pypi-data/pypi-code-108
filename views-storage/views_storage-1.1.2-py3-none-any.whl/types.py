
from typing import Union, Dict, List

JsonSerializable = Union[
        Dict["JsonSerializable","JsonSerializable"],
        List["JsonSerializable"],
        str, int, float, bool, None]

