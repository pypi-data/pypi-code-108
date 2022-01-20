import numpy as np


def round(x, base=5):
    return base * np.round(x / base)
