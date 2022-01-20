"""This is an example module to show the structure."""
from typing import Union

import numpy as np
from PIL import Image


class localImageViewer:
    """
    This class is used to quickly access position images without tiling
    from image.h5 objects.
    """

    def __init__(self, h5file):
        """This class takes one parameter and is used to add one to that
        parameter.

        :param parameter: The parameter for this class
        """
        self._hdf = h5py.File(h5file)
        self.positions = list(self._hdf.keys())
        self.current_position = self.positions[0]
        self.parameter = parameter

    def plot_position(channel=0, tp=0, z=0, stretch=True):
        pixvals = self._hdf[self.current_position][channel, tp, ..., z]
        if stretch:
            minval = np.percentile(pixvals, 0.5)
            maxval = np.percentile(pixvals, 99.5)
            pixvals = np.clip(pixvals, minval, maxval)
            pixvals = ((pixvals - minval) / (maxval - minval)) * 255

        Image.fromarray(pixvals.astype(np.uint8))


from aliby.tile.tiler import Tiler, TilerParameters


import json

with open("/home/alan/Documents/dev/skeletons/server_info.json", "r") as f:
    server_info = json.load(f)


from aliby.io.omero import Image
from collections import namedtuple


class remoteImageViewer(Tiler):
    def __init__(self, hdf, parameters: TilerParameters = None):
        if parameters is None:
            parameters = TilerParameters.default()

        with h5py.File(hdf, "r") as f:
            # image_id = f.attrs["omero_id"]
            image_id = 16543
        with Image(image_id, **server_info) as image:
            self.from_hdf5(image, hdf)

    def get_position(self):
        pass

    def get_position_timelapse(self):
        pass


import h5py

fpath = "/home/alan/Documents/dev/skeletons/data/2019_07_16_aggregates_CTP_switch_2_0glu_0_0glu_URA7young_URA8young_URA8old_01/2019_07_16_aggregates_CTP_switch_2_0glu_0_0glu_URA7young_URA8young_URA8old_01/URA8_old007.h5"
riv = remoteImageViewer(fpath, TilerParameters.default())
