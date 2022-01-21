# -*- coding: utf-8 -*-
r"""
Base class for spin lattices
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import List, Tuple, Union
from pathlib import Path
import pandas as pd
from spinterface.inputs.lattice.topology.ITopology import ITopology


class ILattice(ABC):
    r"""
    Abstract base class for spin lattices
    """

    def __init__(self, a1: Union[None, np.ndarray], a2: Union[None, np.ndarray], a3: Union[None, np.ndarray],
                 r_motif: Union[None, List[np.ndarray]], N1: Union[None, int], N2: Union[int, None],
                 N3: Union[None, int], magdir: np.ndarray) -> None:
        r"""
        Initializer. ILattice cannot be initialized but the initializer can be called from sub class.

        Args:
            a1(array): lattice vector 1
            a2(array): lattice vector 2
            a3(array): lattice vector 3
            rmotif(List[arrays]): position of the atoms in the unit cell in units of a1, a2, a3
            N1(int): number of unit cells in a1 dir.
            N2(int): number of unit cells in a2 dir.
            N3(int): number of unit cells in a2 dir.
            magdir(array): initial direction of the magnetization
        """
        self.N1 = N1
        self.N2 = N2
        self.N3 = N3
        if r_motif is not None:
            self.NUC = len(r_motif)
        else:
            self.NUC = None
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self._rmotif = r_motif
        if not any([True if element is None else False for element in [N1, N2, N3, r_motif, a1, a2, a3]]):
            self._points, self._magmoms = self._createlattice()
            magdir = magdir / np.linalg.norm(magdir)
            self._spins = np.array([magdir for NN in range(N1 * N2 * N3 * self.NUC)])

    def _createlattice(self) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Creates the lattice similar to the creation in the spindynamic code.

        Returns:
            the positions of the spins of the lattice in the same order as they appear in some STMi file. Also the mag.
            moments in the same order
        """
        ps, ms = [], []
        for i in range(self.N1):
            for j in range(self.N2):
                for k in range(self.N3):
                    for l in range(self.NUC):
                        p = (i + self._rmotif[l][0]) * self.a1 + (j + self._rmotif[l][1]) * self.a2 + (
                                k + self._rmotif[l][2]) * self.a3
                        ps.append(p)
                        ms.append(self._rmotif[l][3])
        return np.array(ps), np.array(ms)

    def write(self, path: Path = Path.cwd() / 'SpinSTMi.dat') -> None:
        r"""
        Writes the spin lattice to a file
        """
        df = pd.DataFrame(
            {'x': self.X, 'y': self.Y, 'z': self.Z, 'sx': self.SX, 'sy': self.SY, 'sz': self.SZ, 'm': self._magmoms})
        df.to_csv(path, sep=r' ', header=False, index=False)

    @property
    @abstractmethod
    def source(self) -> str:
        r"""
        Returns:
            the type of the lattice (e.g. spin configuration or eigenvector)
        """

    @property
    def spins(self) -> np.ndarray:
        r"""
        Returns:
             the spins in the lattice
        """
        return self._spins

    @spins.setter
    def spins(self, spins: np.ndarray) -> None:
        r"""
        Setter for the magnetisation of the lattice

        Args:
            spins(array): [[sx0, sy0, sz0],...]
        """
        self._spins = spins

    @property
    def points(self) -> np.ndarray:
        r"""
        Returns:
            the points of the lattice.
        """
        return self._points

    @property
    def magstructure(self) -> np.ndarray:
        r"""
        Returns:
            the magnetic structure as used in the spindynamic program
        """
        return np.column_stack((self._points, self._spins, self._magmoms))

    @property
    def X(self) -> np.ndarray:
        r"""
        Returns:
            the X-component of all spins
        """
        return self._points[:, 0]

    @property
    def Y(self) -> np.ndarray:
        r"""
        Returns:
            the Y-component of all spins
        """
        return self._points[:, 1]

    @property
    def Z(self) -> np.ndarray:
        r"""
        Returns:
            the Z-component of all spins
        """
        return self._points[:, 2]

    @property
    def SX(self) -> np.ndarray:
        r"""
        Returns:
            the SX-component of all spins
        """
        return self._spins[:, 0]

    @property
    def SY(self) -> np.ndarray:
        r"""
        Returns:
            the SY-component of all spins
        """
        return self._spins[:, 1]

    @property
    def SZ(self) -> np.ndarray:
        r"""
        Returns:
            the SZ-component of all spins
        """
        return self._spins[:, 2]

    @property
    def nlayer(self) -> int:
        r"""
        Returns:
            the number of layers
        """
        return len(set(self._points[:, 2]))

    @property
    def zlayer(self) -> np.ndarray:
        r"""
        Returns:
            the z coordinates of the occuring layers
        """
        return np.unique(self._points[:, 2])

    @property
    def midpoint(self) -> np.ndarray:
        r"""
        Returns:
            the midpoint of the lattice calculated by the mean
        """
        return np.round(np.mean(self._points, axis=0), 12)

    @property
    def layermidpoints(self) -> np.ndarray:
        r"""
        Returns the midpoints of the layers
        """
        return np.round(np.array([np.mean(self.getlayer_by_idx(l)[:, :3], axis=0) for l in range(self.nlayer)]), 12)

    @property
    def xmagcenter(self) -> np.ndarray:
        r"""
        Returns:
            the center of "mass" (magnetization in x-direction) of the spin lattice
        """
        return 1/self.SX.size * np.sum(self.SX.reshape((np.abs(self.SX.size),1))*self._points, axis=0)

    @property
    def ymagcenter(self) -> np.ndarray:
        r"""
        Returns:
            the center of "mass" (magnetization in x-direction) of the spin lattice
        """
        return 1 / self.SY.size * np.sum(self.SY.reshape((self.SY.size, 1)) * self._points, axis=0)

    @property
    def zmagcenter(self) -> np.ndarray:
        r"""
        Returns:
            the center of "mass" (magnetization in x-direction) of the spin lattice
        """
        return 1 / self.SZ.size * np.sum(self.SZ.reshape((self.SZ.size, 1)) * self._points, axis=0)

    @property
    def total_magnetization(self) -> np.ndarray:
        r"""
        Returns:
            the sum of all spins in the lattice
        """
        return np.sum(self.spins, axis=0)

    def getlayer_by_z(self, z: float) -> np.ndarray:
        r"""
        Args:
            z: z coordinate

        Returns:
            magstructure of the layer with the coordinate z
        """
        return self.magstructure[self.magstructure[:, 2] == z]

    def getlayer_by_idx(self, idx: int) -> np.ndarray:
        r"""
        Args:
            idx: index of the layer
        Returns:
            magstructure of the layer addressed by that index
        """
        if idx > self.nlayer - 1:
            raise ValueError('idx higher than number of layers')
        return self.magstructure[self.magstructure[:, 2] == self.zlayer[idx]]

    def setlayer_by_idx(self, idx: int, magstructure: np.ndarray) -> None:
        r"""
        Sets the magnetisation of a layer

        Args:
            idx(int): index of the layer to set
            magstructure(array): [[x0 y0 z0 sx0 sy0 sz0 mu0],...]
        """
        self._points[self._points[:, 2] == self.zlayer[idx]] = magstructure[:, :3]
        self._spins[self._points[:, 2] == self.zlayer[idx]] = magstructure[:, 3:6]
        self._magmoms[self._points[:, 2] == self.zlayer[idx]] = magstructure[:, 6]

    def setlayer_by_z(self, z: float, magstructure: np.ndarray) -> None:
        r"""
        Sets the magnetisation of a layer

        Args:
            z(foat): z coordinate of the layer to set
            magstructure(array): [[x0 y0 z0 sx0 sy0 sz0 mu0],...]
        """
        self._points[self._points[:, 2] == z] = magstructure[:, :3]
        self._spins[self._points[:, 2] == z] = magstructure[:, 3:6]
        self._magmoms[self._points[:, 2] == z] = magstructure[:, 6]

    @property
    @abstractmethod
    def topologies(self) -> List[ITopology]:
        r"""
        Returns:
            topology information about the lattice
        """


