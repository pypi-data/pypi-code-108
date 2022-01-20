"""
Abstraction layer for accessing fits data via class attributes
"""
from __future__ import annotations

from typing import Optional
from typing import Union

import numpy as np
from astropy.io import fits


class FitsAccessBase:
    def __init__(
        self,
        hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU],
        name: Optional[str] = None,
        auto_squeeze: bool = True,
    ):
        self._hdu = hdu
        self.name = name
        self.auto_squeeze = auto_squeeze

    @property
    def data(self) -> np.ndarray:
        """
        Return the data array from the associated FITS object, with axes of length 1 removed if the
        array has three dimensions and the unit axis is the zeroth one. This is intended solely to
        remove the dummy dimension that is in raw data from the summit.

        Setting `auto_squeeze = False` when initializing this object will never squeeze out any dimensions

        Returns
        -------
        data array
        """
        # This conditional is explicitly to catch summit data with a dummy first axis for WCS
        # purposes
        if self.auto_squeeze and len(self._hdu.data.shape) == 3 and self._hdu.data.shape[0] == 1:
            return np.squeeze(self._hdu.data)
        return self._hdu.data

    @data.setter
    def data(self, array: np.ndarray) -> None:
        # There is no shape magic stuff going on here right now because the tasks/services that care about
        # it will deal with it themselves (I think (tm)).
        self._hdu.data = array

    @property
    def header(self) -> fits.Header:
        return self._hdu.header

    @property
    def size(self) -> float:
        return self._hdu.size

    @classmethod
    def from_header(
        cls, header: Union[fits.Header, dict], name: Optional[str] = None
    ) -> FitsAccessBase:
        """
        Convert a header to a CommonFitsData (or child) object

        Parameters
        ----------
        header
            A single `astropy.io.fits.header.Header` HDU object.
        name
            A unique name for the fits access instance
        """
        if isinstance(header, dict):
            header = fits.Header(header)
        hdu = fits.PrimaryHDU(header=header)
        return cls(hdu=hdu, name=name)
