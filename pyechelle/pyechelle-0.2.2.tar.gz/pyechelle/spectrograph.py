import logging

import h5py
import numpy as np

from pyechelle.CCD import CCD
from pyechelle.transformation import AffineTransformation


class Spectrograph:
    pass


class PSFs:
    def __init__(self):
        self.wl = []
        self.psfs = []
        self.idx = None
        self.sampling = []

    def add_psf(self, wl, data, sampling):
        self.wl.append(wl)
        self.psfs.append(data)
        self.sampling.append(sampling)
        self.idx = None

    def prepare_lookup(self):
        self.idx = np.argsort(self.wl)
        self.wl = np.array(self.wl)[self.idx]
        self.psfs = np.array(self.psfs)[self.idx]
        self.sampling = np.array(self.sampling)[self.idx]


class ZEMAX(Spectrograph):
    def __init__(self, path, fiber: int = 1):
        """
        Load spectrograph model from ZEMAX based .hdf model.

        Args:
            path: file path
            fiber: which fiber
        """
        super().__init__()
        self.transformations = {}
        self.order_keys = {}
        self.psfs = {}
        self.field_shape = "round"
        self.fibers = lambda: self.order_keys
        self.CCD = None
        self.efficiency = None

        self.blaze = None
        self.gpmm = None
        self.name = None
        self.modelpath = path

        with h5py.File(path, "r") as h5f:
            # read in grating information
            self.name = h5f[f"Spectrograph"].attrs['name']
            self.blaze = h5f[f"Spectrograph"].attrs['blaze']
            self.gpmm = h5f[f"Spectrograph"].attrs['gpmm']

            Nx = h5f[f"CCD"].attrs['Nx']
            Ny = h5f[f"CCD"].attrs['Ny']
            ps = h5f[f"CCD"].attrs['pixelsize']
            self.CCD = CCD(xmin=0, xmax=Nx, ymax=Ny, pixelsize=ps)
            self.field_shape = h5f[f"fiber_{fiber}"].attrs["field_shape"]
            try:
                self.efficiency = h5f[f"fiber_{fiber}"].attrs["efficiency"]
            except KeyError:
                logging.warning(f'No spectrograph efficiency data found for fiber {fiber}.')
                self.efficiency = None
            for g in h5f[f"fiber_{fiber}"]:
                if not "psf" in g:
                    data = h5f[f"fiber_{fiber}/{g}"][()]
                    data = np.sort(data, order='wavelength')
                    self.transformations[g] = AffineTransformation(*data.view((data.dtype[0], len(data.dtype.names))).T)
                if "psf" in g:
                    self.psfs[g] = PSFs()
                    for wl in h5f[f"fiber_{fiber}/{g}"]:
                        self.psfs[g].add_psf(h5f[f"fiber_{fiber}/{g}/{wl}"].attrs['wavelength'],
                                             h5f[f"fiber_{fiber}/{g}/{wl}"][()],
                                             h5f[f"fiber_{fiber}/{g}/{wl}"].attrs['dataSpacing'])
                    self.psfs[g].prepare_lookup()
        self.order_keys = list(self.transformations.keys())
        self.orders = [int(o[5:]) for o in self.order_keys]
        print(f"Available orders: {self.orders}")

    def get_wavelength_range(self, order):
        return self.transformations[f"order{order}"].min_wavelength(), self.transformations[
            f"order{order}"].max_wavelength()

