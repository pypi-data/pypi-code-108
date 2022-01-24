"""
This module provides global definitions and methods to compute COR in extrem
Half Acquisition mode
"""

__authors__ = ["C. Nemoz", "H.Payno"]
__license__ = "MIT"
__date__ = "13/04/2021"

import numpy as np
from scipy.signal import convolve2d
from ..resources.logger import LoggerOrPrint

def schift(mat, val):
    ker = np.zeros((3, 3))
    s = 1.0
    if val < 0:
        s = -1.0
    val = s * val
    ker[1, 1] = 1 - val
    if s > 0:
        ker[1, 2] = val
    else:
        ker[1, 0] = val
    mat = convolve2d(mat, ker, mode="same")
    return mat


class SinoCor(object):
    """
    This class has 2 methods:
        - overlap. Find a rough estimate of COR
        - accurate. Try to refine COR to 1/10 pixel
    """

    def __init__(self, sinogram, logger=None):
        """
        """
        self.logger = LoggerOrPrint(logger)
        self.sx = sinogram.shape[1]
        self.sy = sinogram.shape[0]

        # algorithm cannot accept odd number of projs
        nproj2 = int((self.sy - (self.sy % 2)) / 2)

        # extract upper and lower part of sinogram, flipping H the upper part
        self.data1 = sinogram[0:nproj2, :]
        self.data2 = np.fliplr(sinogram[nproj2:, :].copy())

        self.rcor_abs = round(self.sx / 2.0)
        self.cor_acc = round(self.sx / 2.0)

        # parameters for overlap sino - rough estimation

        # default sliding ROI is 20% of the width of the detector
        # the maximum size of ROI in the "right" case is 2*(self.sx - COR)
        # ex: 2048 pixels, COR= 2000, window_width should not exceed 96!

        self.window_width = round(self.sx / 5)


    def overlap(self, side="right", window_width=None):
        """
        Compute COR by minimizing difference of circulating ROI

         - side:         preliminary knowledge if the COR is on right or left
         - window_width: width of ROI that will slide on the other part of the sinogram
                         by default, 20% of the width of the detector.
        """

        if window_width is None:
            window_width = self.window_width

        if not (window_width & 1):
            window_width -= 1

        # number of pixels where the window will "slide".
        n = self.sx - int(window_width)
        nr = range(n)

        dmax = 1000000000.0
        imax = 0

        # Should we do both right and left and take the minimum "diff" of the 2 ?
        # windows self.data2 moves over self.data1, measure the width of the histogram and retains the smaller one.
        if side == "right":
            for i in nr:
                imout = self.data1[:, n - i : n - i + window_width] - self.data2[:, 0:window_width]
                diff = imout.max() - imout.min()
                if diff < dmax:
                    dmax = diff
                    imax = i
            self.cor_abs = self.sx - (imax + window_width + 1.0) / 2.0
            self.cor_rel = self.sx / 2 - (imax + window_width + 1.0) / 2.0
        else:
            for i in nr:
                imout = self.data1[:, i : i + window_width] - self.data2[:, self.sx - window_width : self.sx]
                diff = imout.max() - imout.min()
                if diff < dmax:
                    dmax = diff
                    imax = i
            self.cor_abs = (imax + window_width - 1.0) / 2
            self.cor_rel = self.cor_abs - self.sx / 2.0 - 1
        if imax < 1:
            self.logger.warning("sliding width %d seems too large!" % window_width)
        self.rcor_abs = round(self.cor_abs)
        return self.rcor_abs


    def accurate(self, neighborhood=7, shift_value=0.1):
        """
        refine the calculation around COR integer pre-calculated value
        The search will be executed in the defined neighborhood

        Parameters
        -----------
        neighborhood: int
            Parameter for accurate calculation in the vicinity of the rough estimate.
            It must be an odd number.
            0.1 pixels float shifts will be performed over this number of pixel
        """
        # define the H-size (odd) of the window one can use to find the best overlap moving finely over ng pixels
        if not (neighborhood & 1):
            neighborhood += 1
        ng2 = int(neighborhood / 2)

        # pleft and pright are the number of pixels available on the left and the right of the cor position
        # to slide a window
        pleft = self.rcor_abs - ng2
        pright = self.sx - self.rcor_abs - ng2 - 1

        # the maximum window to slide is restricted by the smaller side
        if pleft > pright:
            p_sign = 1
            xwin = 2 * (self.sx - self.rcor_abs - ng2) - 1
        else:
            p_sign = -1
            xwin = 2 * (self.rcor_abs - ng2) + 1

        # Note that xwin is odd
        xc1 = self.rcor_abs - int(xwin / 2)
        xc2 = self.sx - self.rcor_abs - int(xwin / 2) - 1

        im1 = self.data1[:, xc1 : xc1 + xwin]
        im2 = self.data2[:, xc2 : xc2 + xwin]

        pixs = p_sign * (np.arange(neighborhood) - ng2)
        diff0 = 1000000000.0

        isfr = shift_value * np.arange(10)
        self.cor_acc = self.rcor_abs

        for pix in pixs:
            x0 = xc1 + pix
            for isf in isfr:
                if isf != 0:
                    ims = schift(self.data1[:, x0 : x0 + xwin].copy(), -p_sign * isf)
                else:
                    ims = self.data1[:, x0 : x0 + xwin]

                imout = ims - self.data2[:, xc2 : xc2 + xwin]
                diff = imout.max() - imout.min()
                if diff < diff0:
                    self.cor_acc = self.rcor_abs + (pix + p_sign * isf) / 2.0
                    diff0 = diff
        return self.cor_acc


    # Aliases
    estimate_cor_coarse = overlap
    estimate_cor_fine = accurate
