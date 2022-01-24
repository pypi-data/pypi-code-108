from __future__ import annotations

from typing import Any, List, Union

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]
Number = Union[
    float,
    List[float],
    Array,
]

Axes = NDArray[Any]
