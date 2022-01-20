import numpy as np
from overrides import overrides
from .metric import Metric

class Loss(Metric):
    def __call__(self, results:np.ndarray, labels:np.ndarray, **kwargs):
        return kwargs["loss"]
