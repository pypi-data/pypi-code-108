from .volume import Volume
import numpy as np
import os
from collections import OrderedDict
import SimpleITK as sitk
from vpv.common import timing, ImageReader

from vpv.utils.lookup_tables import Lut
from vpv.utils.read_minc import mincstats_to_numpy


class HeatmapVolume(Volume):
    def __init__(self, *args):
        self.connected_components = OrderedDict()
        super(HeatmapVolume, self).__init__(*args)
        self.lt = Lut()
        self.negative_lut = None
        self.positive_lut = None
        initial_lut = self.lt.heatmap_lut_list()[0]

        self._fdr_thresholds = {}

        neg_lower = float(self._arr_data.min())

        # Fix problem when we have no negative values
        if float(self._arr_data.min()) >= 0:
            neg_upper = 0
        else:
            neg_upper = float(self._arr_data[self._arr_data < 0].max())
        self.neg_levels = [neg_lower, neg_upper]

        pos_upper = self._arr_data.max()
        # Fix problem when we have no positve values
        if self._arr_data.max() <= 0:
            pos_lower = 0
        else:
            pos_lower = self._arr_data[self._arr_data > 0].min()
        self.pos_levels = [float(pos_lower), float(pos_upper)]

        self.non_zero_mins = self._get_non_zero_mins()

        self.set_lut(initial_lut)

        self.max = self._arr_data.max()
        self.min = self._arr_data.min()

    @property
    def fdr_thresholds(self):
        return self._fdr_thresholds

    @fdr_thresholds.setter
    def fdr_thresholds(self, thresholds):
        self._fdr_thresholds = thresholds
        if thresholds is None:  # Set the lower t-statistic slider to max as there's no hits at any FDR cutoff
            self.set_lower_positive_lut(self._arr_data.max() - 0.1)
            self.set_upper_negative_lut(self._arr_data.min() + 0.2)  # Had to add extra as it would go nuts

    def _get_non_zero_mins(self):
        """
        return the minimum non-zero positive value an dthe maximum non-zero negative value
        used to set the minimum T-statistic values in the view manager sliders
        :return:
        """

        if self._arr_data.min() >= 0:
            neg = 0
        else:
            neg = self._arr_data[self._arr_data < 0].max()
        if self._arr_data.max() <= 0:
            pos = 0
        else:
            pos = self._arr_data[self._arr_data > 0].min()
        self.mins = (neg, pos)
        return self.mins

    def positive_min(self):
        return self._arr_data[self._arr_data > 0].min()

    def negative_min(self):
        return self._arr_data[self._arr_data < 0].max()

    def _load_data(self, path, memmap=False):
        """
        override Volume method to cast to 16bit float to speed things up
        """
        if os.path.splitext(path)[1].lower() == '.mnc':

            arr = mincstats_to_numpy(path)  # Need to fix headers for mncs
            return arr
        else:
            ir = ImageReader(path)
            arr = ir.vol.astype(np.float16)

        return arr

    @timing
    def find_largest_connected_components(self):
        """
        Look for the top n conencted comonets for easy finding
        :return:
        """
        self.connected_components = OrderedDict()
        img = sitk.GetImageFromArray(self._arr_data.astype(np.float32)) # Create this on the fly as it would take up lots of space
        lower_threshold = self.neg_levels[1]
        upper_threshold = self.pos_levels[0]
        binary_img = sitk.BinaryThreshold(img, lower_threshold, upper_threshold, 0, 1)
        conn = sitk.RelabelComponent(sitk.ConnectedComponent(binary_img))
        ls = sitk.LabelStatisticsImageFilter()
        ls.Execute(img, conn)
        number_of_labels = ls.GetNumberOfLabels()
        # Now get the top 50  coordinates of the connected components
        n = 50
        if n > number_of_labels:
            n = number_of_labels
        for i in range(1, n):
            bbox = ls.GetBoundingBox(i)  # x,x,y,y, z,z
            size = ls.GetCount(i)
            if size < 4:
                break
            mean = ls.GetMean(i)

            bbox_xyz = [bbox[0], bbox[1], bbox[2], bbox[3], bbox[4], bbox[5]]
            self.connected_components[size, mean] = bbox_xyz

    def set_lut(self, lut_name):
        self.positive_lut, self.negative_lut = self.lt.get_lut(lut_name)
        # If there are no positive or negative values, se the LUT to full transparancy
        if self.neg_levels[0] == self.neg_levels[1]:
            self.negative_lut[:] = 0
        if self.pos_levels[0] == self.pos_levels[1]:
            self.positive_lut[:] = 0

    def get_lut(self):
        return self.negative_lut, self.positive_lut

    def get_data(self, orientation, index=1, flipx=False, flipz=False, flipy=False, xy=None):
        """
        Override the base method. return two arrays instead of one. One with negative values and the other with positives
        The Heatmap layer takes negative and positive slices and applies individual LUTs to each

        If xy given, just return a single pixel value at that position

        Parameters
        ----------
        orientation: Orientation
        index: slice to take
        flipx:
        xy

        Returns
        -------
        tuple: (ndarray, ndarray)
            orthogonal slices at given slice index and orientation if xy is None
        float:
            single voxel value if xy is tuple (xy)

        """
        array = super(HeatmapVolume, self).get_data(orientation, index, flipx, flipz, flipy, xy)

        if xy:
           return array

        neg_array = np.copy(array)
        neg_array[neg_array > 0] = 0
        pos_array = np.copy(array)
        pos_array[pos_array < 0] = 0

        return neg_array, pos_array

    def set_lower_positive_lut(self, value):
        if value > self.max:
            value = self.max - 0.1
        self.pos_levels[0] = value

    def set_upper_positive_lut(self, value):
        self.pos_levels[1] = value

    def set_lower_negative_lut(self, value):
        self.neg_levels[0] = value

    def set_upper_negative_lut(self, value):
        if value < self.min:
            value = self.min + 0.1
        self.neg_levels[1] = value

    def set_t_threshold(self, t):
        self.set_lower_positive_lut(t)
        self.set_upper_negative_lut(-t)