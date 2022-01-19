import sys
from typing import Union


def crash(reason: Union[str, int] = 1) -> None:
    sys.exit(reason)
