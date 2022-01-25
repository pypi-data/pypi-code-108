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
__date__ = "02/12/2021"


from typing import Union
from tomoscan.esrf.hdf5scan import ImageKey
import numpy


def get_n_series(image_key_values: Union[tuple, list], image_key_type: ImageKey) -> int:
    """
    Return the number of series of an inage_key. Image key can be dark, flat, or projection.
    A serie is defined as a contiguous elements in image_key_values

    :param image_key_values: list or tuple of image_keys to consider. Can be integers or tomoscan.esrf.hdf5scan.ImageKey
    """
    image_key_type = ImageKey.from_value(image_key_type)
    if image_key_type is ImageKey.INVALID:
        raise ValueError(
            "we can't count Invalid image keys serie because those are ignored from tomoscan"
        )
    image_key_values = [ImageKey.from_value(img_key) for img_key in image_key_values]

    # remove invalid frames
    image_key_values = numpy.array(
        image_key_values
    )  # for filtering invalid value a numpy aray is requested
    image_key_values = image_key_values[image_key_values != ImageKey.INVALID]

    n_serie = 0
    is_in_a_serie = False
    for frame in image_key_values:
        if frame == image_key_type and not is_in_a_serie:
            is_in_a_serie = True
            n_serie += 1
        elif frame != image_key_type:
            is_in_a_serie = False
    return n_serie
