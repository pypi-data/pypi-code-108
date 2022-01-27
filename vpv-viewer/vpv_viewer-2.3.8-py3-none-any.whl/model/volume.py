import numpy as np
import os
import tempfile
from PyQt5 import QtCore, Qt
from scipy import ndimage
# from scipy.misc import imresize
from ..common import Orientation, ImageReader
from vpv.utils.read_minc import minc_to_numpy


class Volume(Qt.QObject):
    """
    Basically a wrapper around a numpy 3D array
    The classes that inherit from this add functionality specific to those volume type
    """
    axial_slice_signal = QtCore.pyqtSignal(str, name='axial_signal')

    def __init__(self, vol_path: str, model: "vpv_viewer.model.model", datatype: str,  memory_map: bool=False):
        """

        Parameters
        ----------
        vol_path:
        model
        datatype
        memory_map
        """
        super(Volume, self).__init__()
        self.space = None
        self.data_type = datatype
        self.name = None
        self.model = model
        self.vol_path = vol_path
        self._arr_data = self._load_data(vol_path, memory_map)
        self.voxel_size = 28  # Temp hard coding
        self.interpolate = False
        # Set to False if Volume to be destroyed. We can't just delete this object as there are reference to
        # it in Slices.Layers and possibly others
        self.active = True
        self.int_order = 3
        self.min = float(self._arr_data.min())
        self.max = float(self._arr_data.max())
        # The coordinate spacing of the input volume


    def shape_xyz(self):
        return tuple(reversed(self._arr_data.shape))

    def shape(self):
        return self._arr_data.shape

    def get_axial_slot(self):
        print('get_axial_slot')

    # def pixel_axial(self, z, y, x, flipx, flipz):
    #     """
    #     get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the z axis
    #     """
    #     try:
    #         vox = self.get_data(Orientation.axial, z, flipx, flipz, xy=(x, y))
    #     except TypeError as e:
    #         print(e.message)
    #     return vox
    #
    # def pixel_sagittal(self, z, y, x, flipx, flipz):
    #     """
    #     get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the y axis
    #     """
    #     vox = self.get_data(Orientation.sagittal, x, flipx, flipz, xy=(y, z))
    #     return vox
    #
    # def pixel_coronal(self, z, y, x, flipx, flipz):
    #     """
    #     get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the y axis
    #     """
    #     vox = self.get_data(Orientation.coronal, y, flipx, flipz, xy=(x, z))
    #     return vox

    def intensity_range(self):
        return self.min, self.max

    def _load_data(self, path, memmap=False):
        """
        Open data and convert
        todo: error handling
        :param path:
        :return:
        """
        ext = os.path.splitext(path)[1].lower()
        if ext == '.mnc':
            return minc_to_numpy(path)

        ir = ImageReader(path, memmap=memmap)
        vol = ir.vol
        self.space = ir.dir_cos
        #
        # vol = convert_volume(vol, ir.space)
        return vol

    def get_data(self, orientation, index=0, flipx=False, flipz=False, flipy=False, xy=None):
        """
        Get a 2D slice given the index and orthogonal orientation. Optionally return the slice flipped in x
        if xy specified, return just a single pixel value

        Parameters
        ----------
        orientation: Orientation
        index: int
            the slice to returb
        flipx: bool
            Whether to flip in x or not. X in this case is the x dimension of the resulting 2D slice that will be
            returned for display
        flipz: bool
            Whether to flip in z or not. Z in this case is the order of the slices as they come of the array for
            the given dimension. if flipz == True then  -> index = dimension_len - index

        Returns
        -------
        np.ndarry 2D


        Notes
        -----
        get_sagittal, get_axial and get_coronal apply a flip in in x on the 2D slice.

        """
        if orientation == Orientation.sagittal:
            return self._get_sagittal(index, flipx, flipz, flipy, xy=xy)
        if orientation == Orientation.coronal:
            return self._get_coronal(index, flipx, flipz, flipy, xy=xy)
        if orientation == Orientation.axial:
            return self._get_axial(index, flipx, flipz, flipy, xy=xy)

    def dimension_length(self, orientation):
        """
        Temp bodge. return the number of slices in this dimension
        :param orientation:
        :return:
        """
        if orientation == Orientation.sagittal:
            return self._arr_data.shape[2]
        if orientation == Orientation.coronal:
            return self._arr_data.shape[1]
        if orientation == Orientation.axial:
            return self._arr_data.shape[0]

    def set_voxel_size(self, size):
        """
        Set the voxel size in real world dimensions
        :param size:
        :return:
        """
        self.voxel_size = size

    def _get_coronal(self, index, flipx, flipz, flipy, xy=None):
        if flipz:
            index = self.shape_xyz()[1] - index
        slice_ = self._arr_data[:, index, :]
        if flipy:
            slice_ = np.flipud(slice_)
        if not flipx:
            slice_ = np.fliplr(slice_)
        if xy:
            x, y = xy
            slice_ = slice_[y, x]
        return slice_.T

    def _get_sagittal(self, index, flipx, flipz, flipy, xy=None):
        if flipz:
            index = self.shape_xyz()[0] - index
        slice_ = self._arr_data[:, :, index]
        if flipy:
            slice_ = np.flipud(slice_)
        if not flipx:
            slice_ = np.fliplr(slice_)
        if xy:
            x, y = xy
            slice_ = slice_[y, x]
        return slice_.T

    def _get_axial(self, index, flipx, flipz, flipy, xy=None):
        if flipz:
            index = self.shape_xyz()[2] - index
        slice_ = self._arr_data[index, :, :]
        if flipy:
            slice_ = np.flipud(slice_)
        if not flipx:
            slice_ = np.fliplr(slice_)
        if xy:
            x, y = xy
            slice_ = slice_[y, x]
        return slice_.T

    def set_lower_level(self, level):
        self.levels[0] = level

    def set_upper_level(self, level):
        #print 'u', level
        self.levels[1] = level

    def destroy(self):
        self._arr_data = None
        self.active = False

    def set_interpolation(self, state):
        self.interpolate = state

    # def _interpolate(self, slice_):
    #     return imresize(ndimage.zoom(slice_, 2, order=4), 0.5, interp='bicubic')
    #     #return ndimage.gaussian_filter(slice_, sigma=0.7, order=0)
