# -*- coding: utf-8 -*-
r"""
Abstract interface class for visualizing energy landscapes of functions defined on a two dimensional configuration
space. These visualizations can be used to explain the methods performed by the Spin Dynamics Code on high dimensional
configuration space. E.G. the GNEB or ci-GNEB method, the saddle point search, the mode following or even minimization
procedures. In that context the package spineapple included in this package here can be used (It includes low dim.
implementations of the algorithms of the spindynamic code).
"""
from abc import ABC, abstractmethod
from typing import Callable, Union
from spinterface.visualizations.energylandscapes.i2dfunction import I2DFunction
import numpy as np


class IVisualizer(ABC):
    r"""
    Abstract base class for visualizing functions on two dimensional configuration spaces.
    """

    def __init__(self, x: np.ndarray, y: np.ndarray, function: I2DFunction) -> None:
        r"""
        Initializer for the Visualizer.

        Args:
            x(np.array): x array - can be created with linspace (together with y a meshgrid will be created.
            y(np.array): y array - can be created with linspace (together with x a meshgrid will be created.
            function(I2DFunction): function defined on a two dimensional configuration space.
        """
        self.func = function
        self.x = x
        self.y = y
        self.xgrid, self.ygrid = np.meshgrid(self.x, self.y)
        # evaluate the
        self.zgrid = function(self.xgrid, self.ygrid)
