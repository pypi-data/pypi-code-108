import numpy as np


def int16_to_float(x: np.ndarray) -> np.ndarray:
    return np.single(x) / 32768
