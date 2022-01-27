from vpv.common import Orientation, read_image
import numpy as np


class VectorVolume(object):
    """
    Holds deformation vector field volume.
    Does not inherit from Volume as it's so different
    """
    def __init__(self,  vol, model, datatype):
        self.model = model
        self.datatype = datatype
        self._arr_data = self._load_data(vol)
        self.shape = self._arr_data.shape
        self.scale = 1
        self.subsampling = 5

    def _load_data(self, vol, memap=False):
        return read_image(vol)

    def get_coronal(self, index):
        #slice_ = np.rot90(self._arr_data[:, index, :], 1)
        slice_ = np.fliplr(self._arr_data[:, index, :])
        return slice_

    def get_sagittal(self, index):
        slice_ = self._arr_data[:, :, index]
        #slice_ = np.rot90(self._arr_data[:, :, index], 1)
        return slice_

    def get_axial(self, index):
        slice_ = np.flipud(self._arr_data[index, :, :])
        return slice_

    def dimension_length(self, orientation):
        """
        Temp bodge. return the number of slices in this dimension
        :param orientation:
        :return:
        """
        if orientation == Orientation.sagittal:
            return self._arr_data[0, 0, :, 0].size
        if orientation == Orientation.coronal:
            return self._arr_data[0, :, 0, 0].size
        if orientation == Orientation.axial:
            return self._arr_data[:, 0, 0, 0].size