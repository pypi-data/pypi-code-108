from typing import List, Union
from pathlib import Path
import numpy as np
from .buffered_array import BufferedArray

__all__ = ('EntropyProductionRate',)


class EntropyProductionRate:
    """
    Tracks entropy production rate (EPR) using a Gallavotti-Cohen functional.

    EPR = 1/N sum_{i=0}^N ln P(i -> j)/P(j -> i)

    N is the number of steps of a path and P(i -> j) is the probability of
    going from state i to state j. The expression is exact in the limit
    N -> infty. However, this class tracks the terms inside the sum and write
    them to file. To calculate the time evolution of EPR one can use a windowed
    average of the resulting data.

    References:

    [1] Gourgoulias, Konstantinos, Markos A. Katsoulakis, and Luc Rey-Bellet.
        "Information criteria for quantifying loss of reversibility in parallelized KMC."
        Journal of Computational Physics 328 (2017): 438-454.

    :param buffer_length: Length of buffer used to temporarily store the terms
        in the sum in memory. When the buffer is full, it is flushed to a text
        file.
    :param logfile: Filename of the file used when the buffer is flushed
    """

    def __init__(self, buffer_length: int = 10000, logfile: Union[str, Path] = "epr.txt"):
        self._buffer = BufferedArray(size=buffer_length, fname=logfile)
        self.prev_swap = -1
        self.prob_forw = 0.0

    def reset(self):
        """
        Clear all information stored
        """
        self.prev_swap = -1
        self.prob_forw = 0.0
        self._buffer.clear()

    @staticmethod
    def _probabilty(choice: int, cumulative_rates: np.ndarray):
        """
        Calculate the probability of going from the current state to the
        chosen state.
        """
        if choice == 0:
            return cumulative_rates[0]
        return cumulative_rates[choice] - cumulative_rates[choice - 1]

    def update(self, current: int, choice: int, cumulative_rates: np.ndarray, swaps: List[int]):
        """
        Update the buffer

        :param current: Current position of the vacancy
        :param choice: Index into cumulative_rates that is chosen
        :param cumulative_rates: Cumulative sum of the rates
        :param swaps: Possible swaps
        """
        if self.prev_swap == -1:
            # First, time we can't calculate the backward rate.
            # Track the swap and return
            self.prev_swap = current
            self.prob_forw = self._probabilty(choice, cumulative_rates)
            return

        backward = swaps.index(self.prev_swap)
        prob_back = self._probabilty(backward, cumulative_rates)
        self.prev_swap = current
        self._buffer.push(np.log(self.prob_forw / prob_back))

    def flush_buffer(self):
        self._buffer.flush()
