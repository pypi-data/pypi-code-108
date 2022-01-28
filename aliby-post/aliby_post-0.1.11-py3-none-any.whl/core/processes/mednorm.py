#!/usr/bin/env python3


import pandas as pd

from agora.abc import ParametersABC, ProcessABC


class signalParameters(ParametersABC):
    """
    :window: Number of timepoints to consider for signal.
    """

    def __init__(self, window: int):
        self.window = window

    @classmethod
    def default(cls):
        return cls.from_dict({"window": 3})


class mednorm(ProcessABC):
    """
    Normalise a channel by the median
    """

    def __init__(self, parameters: mednormParameters):
        super().__init__(parameters)

    def run(self, signal: pd.DataFrame):
        return signal.rolling(window=self.parameters.window, axis=1).mean().diff(axis=1)
