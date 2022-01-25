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
__date__ = "30/05/2018"


import logging
import fabio

_logger = logging.getLogger(__name__)


def flatFieldCorrection(imgs, dark, flat):
    """
    Simple normalization of a list of images.
    Normalization is made for X-Ray imaging:
    (img - dark) / (flat - dark)

    :param dict imgs: list of imgs to correct. key: index of the image,
                      value: the image path or numpy.ndarray
    :param numpy.ndarray dark: dark image
    :param numpy.ndarray flat: flat image
    :return: list of corrected images
    """
    res = {}
    conditionOK = True
    if dark.ndim != 2:
        _logger.error(
            "cannot make flat field correction, dark should be of " "dimension 2"
        )
        conditionOK = False

    if flat.ndim != 2:
        _logger.error(
            "cannot make flat field correction, flat should be of " "dimension 2"
        )
        conditionOK = False

    if dark.shape != flat.shape:
        _logger.error("Given dark and flat have incoherent dimension")
        conditionOK = False

    if conditionOK is False:
        return res

    for index, img in imgs.items():
        imgData = img
        if type(img) is str:
            assert img.endswith(".edf")
            imgData = fabio.open(img).data

        if imgData.shape != dark.shape:
            _logger.error("Image has invalid. Cannot apply flat field" "correction it")
            corrrectedImage = imgData
        else:
            corrrectedImage = (imgData - dark) / (flat - dark)

        res[index] = corrrectedImage

    return res
