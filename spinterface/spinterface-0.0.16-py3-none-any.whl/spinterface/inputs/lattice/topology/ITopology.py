r"""
Abstract base class for topology classes
"""
from abc import ABC, abstractmethod
import numpy as np


class ITopology(ABC):
    r"""
    abstract base class for inheriting topology classes for spin lattices
    """

    @property
    @abstractmethod
    def dual_lattice_points(self) -> np.ndarray:
        r"""
        Returns the points of the dual lattice
        """

    @property
    @abstractmethod
    def areas1(self) -> np.ndarray:
        r"""
        Returns the area of the upper triangles
        """

    @property
    @abstractmethod
    def areas2(self) -> np.ndarray:
        r"""
        Returns the area of the upper triangles
        """

    @property
    @abstractmethod
    def topo_dens(self) -> np.ndarray:
        r"""
        Returns the topological density for each dual lattice point
        """

    @property
    @abstractmethod
    def polygons1(self) -> np.ndarray:
        r"""
        Returns the upper triangles
        """

    @property
    @abstractmethod
    def polygons2(self) -> np.ndarray:
        r"""
        Returns the lower triangles
        """

    @property
    @abstractmethod
    def topological_center(self) -> np.ndarray:
        r"""
        Returns the center of mass with respect to the topological density
        """