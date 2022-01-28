r"""
Abstract class for functions which meet the requirements of the visualizer of the energy landscape. Inheriting from
this class for your own defined functions ensures this fulfillment.
"""
from abc import ABC, abstractmethod
import numpy as np


class I2DFunction(ABC):
    r"""
    Abstract base class for functions for visualizing energy landscapes on 2D spaces.
    """

    @abstractmethod
    def __call__(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        r"""
        Abstract method which prescribes the functions to implement for the use in the visualization interface.
        """


    #===============utility function which can be used to define a combination in the call-method when inheriting=======


    @staticmethod
    def gauss(x: np.ndarray, y: np.ndarray, x0: float, y0: float, a: float, sigmax: float, sigmay: float) -> np.ndarray:
        r"""
        Gaussian function
        Args:
            x: x-array
            y: y-array
            x0: x offset zero point
            y0: y offset zero point
            a: amplitude
            sigmax: x width
            sigmay: y width

        Returns:
            a * e^{-(x - x0)^2 / sigmax} * e^{-(y - y0)^2 / sigmay}

        """
        return a * np.exp(-(((x - x0) ** 2 / sigmax) + ((y - y0) ** 2 / sigmay ** 2)))

    @staticmethod
    def spherical_sin(x: np.ndarray, y: np.ndarray, omega: float, a: float):
        r"""
        Spherical sine
        Args:
            x: x-array
            y: y-array
            omega: frequency
            a: amplitude

        Returns:
            a * sin(w * sqrt(w * (x^2 + y^2))

        """
        return a * np.sin(omega * np.sqrt(omega * (x ** 2 + y ** 2)))
