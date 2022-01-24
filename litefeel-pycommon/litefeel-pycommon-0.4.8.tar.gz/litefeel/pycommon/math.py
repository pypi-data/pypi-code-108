"some function for math"

import math
from typing import SupportsFloat


def round(n: SupportsFloat) -> int:
    return math.floor(float(n).__float__() + 0.5)
