from typing import Union, Tuple

import numpy as np
from torch import Tensor


TensorType = Union[np.ndarray, Tensor]
TensorTuple = Union[TensorType, Tuple[TensorType, ...]]
