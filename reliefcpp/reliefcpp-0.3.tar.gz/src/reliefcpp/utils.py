from enum import Enum

from numpy import isin


class Metric(Enum):
    EUCLIDEAN = 0
    MANHATTAN = 1
    HAMMING = 2
    L2 = 3
    L1 = 4


metric_names = [
    "euclidean",
    "manhattan",
    "hamming",
    "l2",
    "l1"
]


def _validate_metric(metric_name):
    if isinstance(metric_name, Metric):
        return metric_name.value
    elif isinstance(metric_name, str):
        metric_name = metric_name.lower()
        return metric_names.index(metric_name)
    elif isinstance(metric_name, int):
        return metric_name
    else:
        raise ValueError("Could not identify metric.")
