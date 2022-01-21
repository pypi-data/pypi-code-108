# -*- coding: utf-8 -*-
r"""
Classes responsible for rotations of spin configurations
"""
import numpy as np
from abc import abstractmethod, ABC
from pathlib import Path
import pandas as pd
from typing import Union


class IRotation(ABC):
    r"""
    Abstract base class for rotations of spin configurations
    """

    def __init__(self, spins: np.ndarray, scale: float = 1.0, rodriguez_threshold: float = 1.0e-5) -> None:
        r"""
        Initializes the superclass for rotations

        Args:
            spins: spin array of all spins in the lattice: [[s1x,s1y,s1z],...,[sNx,sNy,sNz]]
            scale: scales the rotations angle for all spins
            rodriguez_threshold: defines how small an angle for a certain threshold has to be in order to switch the
            description of rodriguez formula to the corresponding taylor expansion
        """
        self._spins = spins
        self._scale = scale
        self._rodriguez_threshold = rodriguez_threshold

    @abstractmethod
    def applyrotation(self) -> np.ndarray:
        r"""
        Applies rotations
            returns:
                the rotated spin configuration: [[s1x',s1y',s1z'],...,[sNx',sNy',sNz']]
        """


class CRotationAlongEvec(IRotation):
    r"""
    Class for rotation of a spin lattice along an eigenvector.
    """

    def __init__(self, spins: np.ndarray, scale: float = 1.0, evec_source: str = 'file',
                 evec_path: Path = Path.cwd() / 'evec.dat', evec_data: Union[None, np.ndarray] = None) -> None:
        r"""
        Initializes the rotation of a spin lattice along an eigenvector.

        Args:
            spins: spin array of all spins in the lattice: [[s1x,s1y,s1z],...,[sNx,sNy,sNz]]
            scale: scales the rotations angle for all spins
            evec_source: decider string from which source the data for the eigenvector shall be read. Can be file
            (data is read from the file provided in 'evec_path') or data (the data is used provided in 'evec_data').
            evec_path: path to the eigenvector file
            evec_data: numpy array for the eigenvector information. Default is None here.
        """
        super().__init__(spins, scale=scale, rodriguez_threshold=1e-5)
        if evec_source == 'data':
            if evec_data is None:
                raise ValueError(
                    'If you choose data as as source please provide the eigenvector array in the evec_data keyword!')
            else:
                self._displacement = evec_data
        elif evec_source == 'file':
            try:
                self._df_evec = pd.read_csv(evec_path, sep=r'\s+', usecols=[3, 4, 5, 6],
                                            names=['vx', 'vy', 'vz', 'v'])
                self._displacement = np.zeros(shape=(len(self._df_evec['v']), 3))
                self._displacement[:, 0] = self._df_evec['vx'].to_numpy()
                self._displacement[:, 1] = self._df_evec['vy'].to_numpy()
                self._displacement[:, 2] = self._df_evec['vz'].to_numpy()
            except FileNotFoundError:
                raise FileNotFoundError(
                    'Corresponding eigenvector file not found. Please provide correct path under keyword: evec_path')
        else:
            raise ValueError('Keyword for eigenvector data source not supported!')
        # apply scaling:
        self._displacement = self._displacement * self._scale

    def applyrotation(self) -> np.ndarray:
        r"""
        Applies rotations
            returns:
             the rotated spin configuration: [[s1x',s1y',s1z'],...,[sNx',sNy',sNz']]
        """
        rotated_spins = np.zeros(shape=(len(self._df_evec['v']), 3))
        for (index, spin) in enumerate(self._spins):
            theta_i = np.linalg.norm(self._displacement[index, :])
            if theta_i >= self._rodriguez_threshold:
                rotated_spins[index, :] = spin * np.cos(theta_i) + self._displacement[index, :] * np.sin(
                    theta_i) / theta_i
            else:
                rotated_spins[index, :] = spin * np.cos(theta_i) + self._displacement[index, :] * (
                            1.0 - 1.0 / 6.0 * theta_i ** 2 + 1.0 / 120.0 * theta_i ** 4)
        return rotated_spins
