#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Geometry class for detector."""
import logging
import typing as t
from enum import Enum
from pathlib import Path

import numpy as np

from pyxel.util.memory import get_size


class MaterialType(Enum):
    """TBW."""

    Silicon = "silicon"
    HXRG = "hxrg"


# Universal global constants
M_ELECTRON = 9.10938356e-31  # kg     # TODO put these global constants to a data file


def load_array(filename: Path) -> np.ndarray:
    """Load an array from a filename."""
    if filename.suffix == ".npy":
        logging.debug("Load numpy array from filename '%s'", filename)
        result = np.load(filename)  # type: np.ndarray
    else:
        raise NotImplementedError

    return result


class Material:
    """Material attributes of the detector."""

    def __init__(
        self,
        trapped_charge: t.Optional[Path] = None,
        n_acceptor: float = 0.0,
        n_donor: float = 0.0,
        material: MaterialType = MaterialType.Silicon,
        material_density: float = 2.328,
        ionization_energy: float = 3.6,
        band_gap: float = 1.12,
        e_effective_mass: float = 0.5 * M_ELECTRON,
    ):
        """Create an instance of `Material`.

        Parameters
        ----------
        trapped_charge: str
            Numpy array storing the trap density temporarily.
        n_acceptor: float
            Density of acceptors in the lattice. Unit: cm^-3
        n_donor: float
            Density of donors in the lattice. Unit: cm^-3
        material: MaterialType
            Semiconductor material of the detector
        material_density: float
            Material density. Unit: g/cm^3
        ionization_energy: float
            Mean ionization energy of the semiconductor lattice. Unit: eV
        band_gap: float
            Band gap of the semiconductor lattice. Unit: eV
        e_effective_mass: float
            Electron effective mass in the semiconductor lattice. Unit: kg
        """
        if not (0.0 <= n_acceptor <= 1000.0):
            raise ValueError("'n_acceptor' must be between 0.0 and 1000.0.")

        if not (0.0 <= n_donor <= 1000.0):
            raise ValueError("'n_donor' must be between 0.0 and 1000.0.")

        if not (0.0 <= material_density <= 10000.0):
            raise ValueError("'material_density' must be between 0.0 and 10000.0.")

        if not (0.0 <= ionization_energy <= 100.0):
            raise ValueError("'ionization_energy' must be between 0.0 and 100.0.")

        if not (0.0 <= band_gap <= 10.0):
            raise ValueError("'band_gap' must be between 0.0 and 10.0.")

        if not (0.0 <= e_effective_mass <= 1.0e-10):
            raise ValueError("'e_effective_mass' must be between 0.0 and 1.e-10.")

        data = (
            load_array(trapped_charge) if trapped_charge else None
        )  # type: t.Optional[np.ndarray]

        self._trapped_charge = data  # type: t.Optional[np.ndarray]
        self._n_acceptor = n_acceptor
        self._n_donor = n_donor

        # TODO: The following parameters could be extracted into a new dedicated class
        self._material = material  # TODO: create func for compound materials
        self._material_density = (
            material_density  # TODO: set automatically depending on the material
        )
        self._ionization_energy = (
            ionization_energy  # TODO: set automatically depending on the material
        )
        self._band_gap = band_gap  # TODO: set automatically depending on the material
        self._e_effective_mass = (
            e_effective_mass  # TODO: set automatically depending on the material
        )
        self._numbytes = 0

    @property
    def trapped_charge(self) -> t.Optional[np.ndarray]:
        """Get Numpy array storing the trap density temporarily."""
        return self._trapped_charge

    @trapped_charge.setter
    def trapped_charge(self, value: Path) -> None:
        """Set Numpy array storing the trap density temporarily."""
        self._trapped_charge = load_array(value)

    @property
    def n_acceptor(self) -> float:
        """Get Density of acceptors in the lattice."""
        return self._n_acceptor

    @n_acceptor.setter
    def n_acceptor(self, value: float) -> None:
        """Set Density of acceptors in the lattice."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'n_acceptor' must be between 0.0 and 1000.0.")

        self._n_acceptor = value

    @property
    def n_donor(self) -> float:
        """Get Density of donors in the lattice."""
        return self._n_donor

    @n_donor.setter
    def n_donor(self, value: float) -> None:
        """Set Density of donors in the lattice."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'n_donor' must be between 0.0 and 1000.0.")

        self._n_donor = value

    @property
    def material(self) -> MaterialType:
        """Get Semiconductor material of the detector."""
        return self._material

    @material.setter
    def material(self, value: MaterialType) -> None:
        """Set Semiconductor material of the detector."""
        self._material = value

    @property
    def material_density(self) -> float:
        """Get Material density."""
        return self._n_donor

    @material_density.setter
    def material_density(self, value: float) -> None:
        """Set Material density."""
        if not (0.0 <= value <= 10000.0):
            raise ValueError("'material_density' must be between 0.0 and 10000.0.")

        self._material_density = value

    @property
    def ionization_energy(self) -> float:
        """Get Mean ionization energy of the semiconductor lattice."""
        return self._ionization_energy

    @ionization_energy.setter
    def ionization_energy(self, value: float) -> None:
        """Set Mean ionization energy of the semiconductor lattice."""
        if not (0.0 <= value <= 100.0):
            raise ValueError("'ionization_energy' must be between 0.0 and 100.0.")

        self._ionization_energy = value

    @property
    def band_gap(self) -> float:
        """Get Band gap of the semiconductor lattice."""
        return self._band_gap

    @band_gap.setter
    def band_gap(self, value: float) -> None:
        """Set Band gap of the semiconductor lattice."""
        if not (0.0 <= value <= 10.0):
            raise ValueError("'band_gap' must be between 0.0 and 10.0.")

        self._band_gap = value

    @property
    def e_effective_mass(self) -> float:
        """Get Electron effective mass in the semiconductor lattice."""
        return self._e_effective_mass

    @e_effective_mass.setter
    def e_effective_mass(self, value: float) -> None:
        """Set Electron effective mass in the semiconductor lattice."""
        if not (0.0 <= value <= 1.0e-10):
            raise ValueError("'e_effective_mass' must be between 0.0 and 1.e-10.")

        self._e_effective_mass = value

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes

    # TODO create func for compound materials
    # def set_material(self, material):
    #     """Set material properties.
    #
    #     :param material:
    #     """
    #     # TODO put these constants to a data file
    #     if material == 'silicon' or 'Si' or 'si':
    #         self.material_density = 2.328                 # (g/cm3)
    #         self.ionization_energy = 3.6                  # (eV)
    #         self.band_gap = 1.12                          # (eV)
    #         self.e_effective_mass = 0.5 * M_ELECTRON      # (kg)
    #
    #     else:
    #         raise NotImplementedError('Given material has not implemented yet')
