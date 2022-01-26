import logging

import h5py
import numpy as np

logger = logging.getLogger('CCD')


def read_ccd_from_hdf(path):
    with h5py.File(path, "r") as h5f:
        # read in CCD information
        Nx = h5f[f"CCD"].attrs['Nx']
        Ny = h5f[f"CCD"].attrs['Ny']
        ps = h5f[f"CCD"].attrs['pixelsize']
        return CCD(xmin=0, xmax=Nx, ymax=Ny, pixelsize=ps)


class CCD:
    def __init__(self, name='detector', xmin=0, xmax=4096, ymin=0, ymax=4096, maxval=65536, pixelsize=9):
        self.data = np.zeros(((ymax - ymin), (xmax - xmin)), dtype=np.uint32)
        self.name = name
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.maxval = maxval
        self.pixelsize = pixelsize

    def add_readnoise(self, std=3.):
        self.data = self.data + np.asarray(np.random.normal(0., std, self.data.shape).round(0), dtype=np.int32)

    def add_bias(self, value: int = 1000):
        """Adds a bias value to the detector counts

        Args:
            value: bias value to be added. If float will get rounded to next integer

        Returns:
            None
        """
        self.data += value

    def clip(self):
        if np.any(self.data < 0):
            logger.warning('There is data <0 which will be clipped. Make sure you e.g. apply the bias before the '
                           'readnoise.')
            self.data[self.data < 0] = 0
        if np.any(self.data > self.maxval):
            self.data[self.data > self.maxval] = self.maxval
