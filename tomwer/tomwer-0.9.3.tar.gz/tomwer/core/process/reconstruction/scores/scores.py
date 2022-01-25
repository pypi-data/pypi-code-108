# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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
__date__ = "18/02/2021"


from silx.utils.enum import Enum as _Enum
import numpy
import sys
import logging
from typing import Union

_logger = logging.getLogger(__name__)


class ScoreMethod(_Enum):
    STD = "standard deviation"
    TV = "total variation"
    TV_INVERSE = "1 / (total variation)"
    STD_INVERSE = "1 / std"
    TOMO_CONSISTENCY = "tomo consistency"


class ComputedScore:
    def __init__(self, tv, std, tomo_consistency=None):
        self._tv = tv
        self._std = std
        self._tomo_consistency = tomo_consistency

    @property
    def total_variation(self):
        return self._tv

    @property
    def std(self):
        return self._std

    @property
    def tomo_consistency(self):
        return self._tomo_consistency

    def get(self, method: ScoreMethod):
        method = ScoreMethod.from_value(method)
        if method is ScoreMethod.TV:
            return self.total_variation / float(10e5)
        elif method is ScoreMethod.TV_INVERSE:
            return (1.0 / self.total_variation) * float(10e5)
        elif method is ScoreMethod.STD:
            return self.std
        elif method is ScoreMethod.STD_INVERSE:
            return 1.0 / self.std
        elif method is ScoreMethod.TOMO_CONSISTENCY:
            return self.tomo_consistency
        else:
            raise ValueError("{} is an unrecognized method".format(method))


def compute_tomo_consistency(
    data: numpy.ndarray,
    original_sinogram,
    angles,
    original_axis_position,
    detector_width,
):
    from silx.opencl.projection import Projection

    projector = Projection(
        slice_shape=data.shape,
        angles=angles,
        detector_width=detector_width,
        axis_position=original_axis_position,
    )
    sinogram = projector.projection(data)
    sinogram_n = (sinogram - sinogram.min()) / (sinogram.max() - sinogram.min())
    original_sinogram_n = (original_sinogram - original_sinogram.min()) / (
        original_sinogram.max() - original_sinogram.min()
    )
    return 1.0 / (numpy.sum(numpy.abs(sinogram_n - original_sinogram_n)) + 1)


def compute_score_contrast_std(data: numpy.ndarray):
    """
    Compute a contrast score by simply computing the standard deviation of
    the frame
    :param numpy.ndarray data: frame for which we should compute the score
    :return: score of the frame
    :rtype: float
    """
    if data is None:
        return None
    else:
        return data.std() * 100


def compute_tv_score(data: numpy.ndarray):
    """
    Compute the data score as image total variation

    :param numpy.ndarray data: frame for which we should compute the score
    :return: score of the frame
    :rtype: float
    """
    tv = numpy.sum(
        numpy.sqrt(
            numpy.gradient(data, axis=0) ** 2 + numpy.gradient(data, axis=1) ** 2
        )
    )
    return tv


_METHOD_TO_FCT = {
    ScoreMethod.STD: compute_score_contrast_std,
    ScoreMethod.TV: compute_tv_score,
}


def compute_score(
    data: numpy.ndarray,
    method: ScoreMethod,
    angles: Union[None, list] = None,
    original_sinogram: Union[None, numpy.array] = None,
    original_axis_position: Union[float, None] = None,
    detector_width: Union[float, None] = None,
) -> Union[float, None]:
    """

    :param numpy.ndarray data: frame for which we should compute the score
    :param str method:
    :return: score of the frame
    :rtype: float
    """
    method = ScoreMethod.from_value(method)
    if data.ndim == 3:
        if data.shape[0] == 1:
            data = data.reshape(data.shape[1], data.shape[2])
        elif data.shape[2] == 1:
            data = data.reshape(data.shape[0], data.shape[1])
        else:
            raise ValueError("Data is expected to be 2D. Not {}".format(data.ndim))
    elif data.ndim == 2:
        pass
    else:
        raise ValueError("Data is expected to be 2D. Not {}".format(data.ndim))
    if method is ScoreMethod.TOMO_CONSISTENCY:
        try:
            return compute_tomo_consistency(
                data=data,
                angles=angles,
                original_sinogram=original_sinogram,
                original_axis_position=original_axis_position,
                detector_width=detector_width,
            )
        except ImportError:
            return None
        except Exception as e:
            _logger.warning(
                "Fail to compute 'tomo consistency' score. " "Reason is {}".format(e)
            )
            return None
    else:
        fct = _METHOD_TO_FCT.get(method, None)

    if fct is not None:
        return fct(data)
    else:
        raise ValueError("{} is not handled".format(method))


def get_disk_mask_radius(datasets_) -> int:
    """compute the radius to use for the mask"""
    radius = sys.maxsize
    # get min radius
    for cor, (url, data) in datasets_.items():
        assert data.ndim == 2, "data is expected to be 2D"
        min_ = numpy.array(data.shape).min()
        if radius >= min_:
            radius = min_
    return radius // 2


def apply_roi(data, radius, url) -> numpy.array:
    """compute the square included in the circle of radius and centered
    in the middle of the data"""
    half_width = int(radius / 2 ** 0.5)
    center = numpy.array(data.shape[:]) // 2
    min_x, max_x = center[0] - half_width, center[0] + half_width
    min_y, max_y = center[1] - half_width, center[1] + half_width
    try:
        return data[min_y:max_y, min_x:max_x]
    except Exception:
        _logger.error(
            "Fail to apply roi for {}. Take the entire dataset".format(url.path())
        )
        return data
