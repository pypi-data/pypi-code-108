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
__date__ = "22/06/2018"


import fabio
import os
import logging

logger = logging.getLogger(__name__)


def getMotorInformationFromEDfFile(_file):
    """

    :param _file: file to the edf file containing header with information
    :return: dictionary with motor name as key and motor position as value
    :rtype: dict
    """
    assert type(_file) is str
    assert _file.endswith(".edf")
    if not os.path.isfile(_file):
        warn = "%s is not a valid file. Cannot retrieve motor information" % _file
        logger.warning(warn)
        return None
    else:
        with fabio.open(_file) as dsc:
            header = dsc.header

        if "motor_mne" not in header:
            logger.warning(
                'key "motor_mne" not found in the file header.'
                "Cannot retrieve motor information"
            )
            return None

        if "motor_pos" not in header:
            logger.warning(
                'key "motor_pos" not found in the file header.'
                "Cannot retrieve motor information"
            )
            return None

        motor_mne_lst = header["motor_mne"].split(" ")
        motor_pos_lst = header["motor_pos"].split(" ")
        if len(motor_mne_lst) != len(motor_pos_lst):
            logger.warning(
                "Incoherent number of motor_mne and motor_pos."
                "Cannot retrieve motor information"
            )
            return None
        res = {}
        for mne, pos in zip(motor_mne_lst, motor_pos_lst):
            res[mne] = pos
        return res
