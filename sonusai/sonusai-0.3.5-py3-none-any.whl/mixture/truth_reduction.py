import numpy as np

from sonusai import logger


def truth_reduction(x: np.ndarray, func: str) -> np.ndarray:
    if func == 'max':
        return np.max(x, axis=1)

    if func == 'mean':
        return np.mean(x, axis=1)

    logger.error('Invalid truth reduction function: {}'.format(func))
    exit()
