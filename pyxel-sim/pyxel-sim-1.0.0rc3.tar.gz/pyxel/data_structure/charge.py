#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Charge class to generate electrons or holes inside detector."""

import typing as t

import numba
import numpy as np
import pandas as pd
from typing_extensions import Literal

from pyxel.detectors.geometry import (
    get_horizontal_pixel_center_pos,
    get_vertical_pixel_center_pos,
)

if t.TYPE_CHECKING:
    from pyxel.detectors import Geometry


@numba.jit(nopython=True)
def df_to_array(
    array: np.ndarray,
    charge_per_pixel: list,
    pixel_index_ver: list,
    pixel_index_hor: list,
) -> np.ndarray:
    """Assign charge in dataframe to nearest pixel.

    Parameters
    ----------
    array: ndarray
    charge_per_pixel: list
    pixel_index_ver: list
    pixel_index_hor:list

    Returns
    -------
    ndarray
    """
    for i, charge_value in enumerate(charge_per_pixel):
        array[pixel_index_ver[i], pixel_index_hor[i]] += charge_value
    return array


class Charge:
    """TBW."""

    EXP_TYPE = float
    TYPE_LIST = (
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )

    def __init__(self, geo: "Geometry"):

        self._array = np.zeros(
            (geo.row, geo.col), dtype=self.EXP_TYPE
        )  # type: np.ndarray
        self._geo = geo
        self.nextid = 0  # type: int

        self.columns = (
            "charge",
            "number",
            "init_energy",
            "energy",
            "init_pos_ver",
            "init_pos_hor",
            "init_pos_z",
            "position_ver",
            "position_hor",
            "position_z",
            "velocity_ver",
            "velocity_hor",
            "velocity_z",
        )  # type: t.Tuple[str, ...]

        self.EMPTY_FRAME = pd.DataFrame(
            columns=self.columns, dtype=float
        )  # type: pd.DataFrame
        self._frame = self.EMPTY_FRAME.copy()  # type: pd.DataFrame

    @staticmethod
    def create_charges(
        *,
        particle_type: Literal["e", "h"],
        particles_per_cluster: np.ndarray,
        init_energy: np.ndarray,
        init_ver_position: np.ndarray,
        init_hor_position: np.ndarray,
        init_z_position: np.ndarray,
        init_ver_velocity: np.ndarray,
        init_hor_velocity: np.ndarray,
        init_z_velocity: np.ndarray,
    ) -> pd.DataFrame:
        """Create new charge(s) or group of charge(s) as a `DataFrame`.

        Parameters
        ----------
        particle_type : str
            Type of particle. Valid values: 'e' for an electron or 'h' for a hole.
        particles_per_cluster : array-like
        init_energy : array
        init_ver_position : array
        init_hor_position : array
        init_z_position : array
        init_ver_velocity : array
        init_hor_velocity : array
        init_z_velocity : array

        Returns
        -------
        DataFrame
            Charge(s) stored in a ``DataFrame``.
        """
        if not (
            len(particles_per_cluster)
            == len(init_energy)
            == len(init_ver_position)
            == len(init_hor_position)
            == len(init_z_position)
            == len(init_ver_velocity)
            == len(init_hor_velocity)
            == len(init_z_velocity)
        ):
            raise ValueError("List arguments have different lengths.")

        if not (
            particles_per_cluster.ndim
            == init_energy.ndim
            == init_ver_position.ndim
            == init_hor_position.ndim
            == init_z_position.ndim
            == init_ver_velocity.ndim
            == init_hor_velocity.ndim
            == init_z_velocity.ndim
            == 1
        ):
            raise ValueError("List arguments must have only one dimension.")

        elements = len(init_energy)

        # check_position(self.detector, init_ver_position, init_hor_position, init_z_position)      # TODO
        # check_energy(init_energy)             # TODO
        # Check if particle number is integer:
        # check_type(particles_per_cluster)      # TODO

        if particle_type == "e":
            charge = [-1] * elements  # * cds.e
        elif particle_type == "h":
            charge = [+1] * elements  # * cds.e
        else:
            raise ValueError("Given charged particle type can not be simulated")

        # if all(init_ver_velocity) == 0 and all(init_hor_velocity) == 0 and all(init_z_velocity) == 0:
        #     random_direction(1.0)

        # Create new charges as a `dict`
        new_charges = {
            "charge": charge,
            "number": particles_per_cluster,
            "init_energy": init_energy,
            "energy": init_energy,
            "init_pos_ver": init_ver_position,
            "init_pos_hor": init_hor_position,
            "init_pos_z": init_z_position,
            "position_ver": init_ver_position,
            "position_hor": init_hor_position,
            "position_z": init_z_position,
            "velocity_ver": init_ver_velocity,
            "velocity_hor": init_hor_velocity,
            "velocity_z": init_z_velocity,
        }  # type: t.Mapping[str, t.Union[t.Sequence, np.ndarray]]

        return pd.DataFrame(new_charges)

    def convert_df_to_array(self):
        """Convert charge dataframe to an array.

        Charge in the detector volume is collected and assigned to the nearest pixel.
        """
        array = np.zeros((self._geo.row, self._geo.col))

        charge_per_pixel = self.get_frame_values(quantity="number")
        charge_pos_ver = self.get_frame_values(quantity="position_ver")
        charge_pos_hor = self.get_frame_values(quantity="position_hor")

        pixel_index_ver = np.floor_divide(
            charge_pos_ver, self._geo.pixel_vert_size
        ).astype(int)
        pixel_index_hor = np.floor_divide(
            charge_pos_hor, self._geo.pixel_horz_size
        ).astype(int)

        # Changing = to += since charge dataframe is reset, the pixel array need to be
        # incremented, we can't do the whole operation on each iteration
        return df_to_array(array, charge_per_pixel, pixel_index_ver, pixel_index_hor)

    @staticmethod
    def convert_array_to_df(
        array: np.ndarray,
        num_rows: int,
        num_cols: int,
        pixel_vertical_size: float,
        pixel_horizontal_size: float,
    ) -> pd.DataFrame:
        """Convert charge array to a dataframe placing charge packets in pixels to the center and on top of pixels.

        Parameters
        ----------
        array: ndarray
        num_rows: int
        num_cols: int
        pixel_vertical_size: float
        pixel_horizontal_size: float

        Returns
        -------
        DataFrame
        """
        charge_number = array.flatten()
        where_non_zero = np.where(charge_number > 0.0)
        charge_number = charge_number[where_non_zero]
        size = charge_number.size  # type: int

        vertical_pixel_center_pos_1d = get_vertical_pixel_center_pos(
            num_rows=num_rows,
            num_cols=num_cols,
            pixel_vertical_size=pixel_vertical_size,
        )

        horizontal_pixel_center_pos_1d = get_horizontal_pixel_center_pos(
            num_rows=num_rows,
            num_cols=num_cols,
            pixel_horizontal_size=pixel_horizontal_size,
        )

        init_ver_pix_position_1d = vertical_pixel_center_pos_1d[where_non_zero]
        init_hor_pix_position_1d = horizontal_pixel_center_pos_1d[where_non_zero]

        # Create new charges
        return Charge.create_charges(
            particle_type="e",
            particles_per_cluster=charge_number,
            init_energy=np.zeros(size),
            init_ver_position=init_ver_pix_position_1d,
            init_hor_position=init_hor_pix_position_1d,
            init_z_position=np.zeros(size),
            init_ver_velocity=np.zeros(size),
            init_hor_velocity=np.zeros(size),
            init_z_velocity=np.zeros(size),
        )

    def add_charge_dataframe(self, new_charges: pd.DataFrame) -> None:
        """Add new charge(s) or group of charge(s) to the charge dataframe.

        Parameters
        ----------
        new_charges : DataFrame
            Charges as a `DataFrame`
        """
        if set(new_charges.columns) != set(self.columns):
            expected_columns = ", ".join(map(repr, self.columns))  # type: str
            raise ValueError(f"Expected columns: {expected_columns}")

        if self._frame.empty:
            if not np.all(self.array == 0):
                df = Charge.convert_array_to_df(
                    array=self.array,
                    num_cols=self._geo.col,
                    num_rows=self._geo.row,
                    pixel_vertical_size=self._geo.pixel_vert_size,
                    pixel_horizontal_size=self._geo.pixel_horz_size,
                )
                new_frame = df.append(new_charges, ignore_index=True)
            else:
                new_frame = new_charges
        else:
            new_frame = self._frame.append(new_charges, ignore_index=True)

        self._frame = new_frame
        self.nextid = self.nextid + len(new_charges)

    def add_charge(
        self,
        *,
        particle_type: Literal["e", "h"],
        particles_per_cluster: np.ndarray,
        init_energy: np.ndarray,
        init_ver_position: np.ndarray,
        init_hor_position: np.ndarray,
        init_z_position: np.ndarray,
        init_ver_velocity: np.ndarray,
        init_hor_velocity: np.ndarray,
        init_z_velocity: np.ndarray,
    ) -> None:
        """Add new charge(s) or group of charge(s) inside the detector.

        Parameters
        ----------
        particle_type : str
            Type of particle. Valid values: 'e' for an electron or 'h' for a hole.
        particles_per_cluster : array
        init_energy : array
        init_ver_position : array
        init_hor_position : array
        init_z_position : array
        init_ver_velocity : array
        init_hor_velocity : array
        init_z_velocity : array
        """
        # Create charge(s)
        new_charges = Charge.create_charges(
            particle_type=particle_type,
            particles_per_cluster=particles_per_cluster,
            init_energy=init_energy,
            init_ver_position=init_ver_position,
            init_hor_position=init_hor_position,
            init_z_position=init_z_position,
            init_ver_velocity=init_ver_velocity,
            init_hor_velocity=init_hor_velocity,
            init_z_velocity=init_z_velocity,
        )  # type: pd.DataFrame

        # Add charge(s)
        self.add_charge_dataframe(new_charges=new_charges)

    def add_charge_array(self, array: np.ndarray) -> None:
        """Add charge to the charge array. Add to charge dataframe if not empty instead.

        Parameters
        ----------
        array: ndarray
        """
        self.validate_type(array)
        self.validate_shape(array)

        if self._frame.empty:
            self._array += array

        else:
            charge_df = Charge.convert_array_to_df(
                array=array,
                num_cols=self._geo.col,
                num_rows=self._geo.row,
                pixel_vertical_size=self._geo.pixel_vert_size,
                pixel_horizontal_size=self._geo.pixel_horz_size,
            )
            self.add_charge_dataframe(charge_df)

    @property
    def array(self) -> np.ndarray:
        """Get charge in a numpy array."""
        if not self._frame.empty:
            self._array = self.convert_df_to_array()
        return self._array

    def __array__(self, dtype: t.Optional[np.dtype] = None):
        if not isinstance(self._array, np.ndarray):
            raise TypeError("Array not initialized.")
        return np.asarray(self._array, dtype=dtype)

    @property
    def frame(self) -> pd.DataFrame:
        """Get charge in a pandas dataframe."""
        if not isinstance(self._frame, pd.DataFrame):
            raise TypeError("Charge data frame not initialized.")
        return self._frame

    def empty(self) -> None:
        """Empty all data stored in Charge class."""
        self.nextid = 0
        if not self._frame.empty:
            self._frame = self.EMPTY_FRAME.copy()
        self._array *= 0

    def validate_type(self, value: np.ndarray) -> None:
        """Validate a value.

        Parameters
        ----------
        value
        """
        cls_name = self.__class__.__name__  # type: str

        if not isinstance(value, np.ndarray):
            raise TypeError(f"{cls_name} array should be a numpy.ndarray")

        if value.dtype not in self.TYPE_LIST:
            exp_type_name = str(self.EXP_TYPE)  # type: str
            raise TypeError(f"Expected type of {cls_name} array is {exp_type_name}.")

    def validate_shape(self, value: np.ndarray) -> None:
        """TBW."""
        cls_name = self.__class__.__name__  # type: str

        if value.shape != self._array.shape:
            raise ValueError(f"Expected {cls_name} array is {self._array.shape}.")

    def get_frame_values(
        self, quantity: str, id_list: t.Optional[list] = None
    ) -> np.ndarray:
        """Get quantity values of particles defined with id_list. By default it returns values of all particles.

        Parameters
        ----------
        quantity : str
            Name of the quantity: ``number``, ``energy``, ``position_ver``, ``velocity_hor``, etc.
        id_list : Sequence of int
            List of particle ids: ``[0, 12, 321]``

        Returns
        -------
        array
        """
        if id_list:
            df = self._frame.query("index in %s" % id_list)  # type: pd.DataFrame
        else:
            df = self._frame

        array = df[quantity].values  # type: np.ndarray

        return array

    def set_frame_values(
        self, quantity: str, new_value_list: list, id_list: t.Optional[list] = None
    ) -> None:
        """Update quantity values of particles defined with id_list. By default it updates all.

        Parameters
        ----------
        quantity : str
            Name of the quantity: ``number``, ``energy``, ``position_ver``, ``velocity_hor``, etc.
        new_value_list : Sequence of int
            List of values ``[1.12, 2.23, 3.65]``
        id_list : Sequence of int
            List of particle ids: ``[0, 12, 321]``
        """
        new_df = pd.DataFrame({quantity: new_value_list}, index=id_list)
        self._frame.update(new_df)

    def remove_from_frame(self, id_list: t.Optional[list] = None) -> None:
        """Remove particles defined with id_list. By default it removes all particles from DataFrame.

        Parameters
        ----------
        id_list : Sequence of int
            List of particle ids: ``[0, 12, 321]``
        """
        if id_list:
            # TODO: Check carefully if 'inplace' is needed. This could break lot of things.
            self._frame.query("index not in %s" % id_list, inplace=True)
        else:
            self._frame = self.EMPTY_FRAME.copy()
