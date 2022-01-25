# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "25/02/2019"


import numpy
import logging
import enum
from numpy.linalg import inv

_logger = logging.getLogger(__file__)
try:
    from scipy.ndimage import shift as shift_scipy

    has_scipy_shift = True
except ImportError:
    has_scipy_shift = False
    _logger.info("no scipy.ndimage.shift detected, will use numpy.fft instead")


def shift_img(
    data: numpy.ndarray, dx: float, dy: float, cval: float = 0.0
) -> numpy.ndarray:
    """
    Apply simple 2d image shift in 'constant mode'.

    :param data:
    :type data: numpy.ndarray
    :param dx: x translation to be applied
    :type dx: float
    :param dy: y translation to be applied
    :type dy: float
    :param float cval: value to replace the shifted values

    :return: shifted image
    :rtype: numpy.ndarray
    """
    assert data.ndim == 2
    assert dx is not None
    assert dy is not None
    _logger.debug("apply shift dx=%s, dy=%s " % (dx, dy))

    if has_scipy_shift:
        return shift_scipy(
            input=data, shift=(dy, dx), order=1, mode="constant", cval=cval
        )
    else:
        ynum, xnum = data.shape
        xmin = int(-numpy.fix(xnum / 2))
        xmax = int(numpy.ceil(xnum / 2) - 1)
        ymin = int(-numpy.fix(ynum / 2))
        ymax = int(numpy.ceil(ynum / 2) - 1)

        nx, ny = numpy.meshgrid(
            numpy.linspace(xmin, xmax, xnum), numpy.linspace(ymin, ymax, ynum)
        )
        # cast variables to float
        ny = numpy.asarray(ny, numpy.float32)
        nx = numpy.asarray(nx, numpy.float32)
        res = abs(
            numpy.fft.ifft2(
                numpy.fft.fft2(data)
                * numpy.exp(1.0j * 2.0 * numpy.pi * (-dy * ny / ynum + -dx * nx / xnum))
            )
        )

        # apply constant filter
        if dx > 0:
            res[:, 0 : int(numpy.ceil(dx))] = cval
        elif dx < 0:
            res[:, xnum + int(numpy.ceil(dx)) :] = cval
        return res


class ImageScaleMethod(enum.Enum):
    RAW = "raw"
    MEAN = "mean"
    MEDIAN = "median"


def scale_img2_to_img1(img_1, img_2, method=ImageScaleMethod.MEAN):
    """
    scale image2 relative to image 1 in such a way they have same min and
    max. Scale will be apply from and to 'data' / raw data

    :param img_1: reference image
    :type: numpy.array
    :param numpy.array img_2: image to scale
    :type: numpy.array
    :param method: method to apply scaling
    :type: ImageScaleMethod
    :return:
    """
    assert method in ImageScaleMethod
    assert img_1.ndim == 2
    assert img_2.shape == img_1.shape
    min1 = img_2.min()
    max1 = img_2.max()
    min0 = img_1.min()
    max0 = img_1.max()

    if method is ImageScaleMethod.RAW:
        a = (min0 - max0) / (min1 - max1)
        b = (min1 * max0 - min0 * max1) / (min1 - max1)
        return a * img_2 + b
    else:
        if method is ImageScaleMethod.MEAN:
            me0 = img_1.mean()
            me1 = img_2.mean()
        elif method is ImageScaleMethod.MEDIAN:
            me0 = img_1.median()
            me1 = img_2.median()
        else:
            raise ValueError("method not managed", method)

        vec0 = numpy.mat([[min0], [me0], [max0]])
        matr = numpy.mat(
            [[min1 * min1, min1, 1.0], [me1 * me1, me1, 1.0], [max1 * max1, max1, 1.0]]
        )
        vec1 = inv(matr) * vec0
        return (
            float(vec1[0]) * (img_2 * img_2) + float(vec1[1]) * img_2 + float(vec1[2])
        )
