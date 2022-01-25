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
__date__ = "23/10/2019"


from .base import _ReconsParam
import logging

_logger = logging.getLogger(__name__)


class AxisRP(_ReconsParam):
    """
    Define axis parameters for ftserie reconstruction
    """

    AXIS_POSITION_PAR_KEY = "ROTATION_AXIS_POSITION"
    """Key used for the axis position in par files"""

    def __init__(self):
        super().__init__()
        self.__do_axis_correction = True
        self.__use_tomwer_axis = True
        self.__use_old_tomwer_axis = True

        # binding
        self._managed_params = {
            "DO_AXIS_CORRECTION": self.__class__.do_axis_correction,
            "USE_TOMWER_AXIS": self.__class__.use_tomwer_axis,
            "TRY_USE_OLD_TOMWER_AXIS": self.__class__.use_old_tomwer_axis,
        }

    @property
    def do_axis_correction(self):
        """Activate pyhst axis translation correction"""
        return self.__do_axis_correction

    @do_axis_correction.setter
    def do_axis_correction(self, do_axis_correction):
        do_axis_correction = bool(do_axis_correction)
        if do_axis_correction != self.__do_axis_correction:
            self.__do_axis_correction = do_axis_correction
            self.changed()

    @property
    def use_tomwer_axis(self):
        """If the scan contains a valid axis_params.value then use it."""
        return self.__use_tomwer_axis

    @use_tomwer_axis.setter
    def use_tomwer_axis(self, use_tomwer_axis):
        use_tomwer_axis = bool(use_tomwer_axis)
        if self.__use_tomwer_axis != use_tomwer_axis:
            self.__use_tomwer_axis = use_tomwer_axis
            self.changed()

    @property
    def use_old_tomwer_axis(self):
        """If the scan does not contains an axis_params but contains a
        [XXX]tomwer_processes.h5 file from a previous computation, try to
        get the center of rotation from it"""
        return self.__use_old_tomwer_axis

    @use_old_tomwer_axis.setter
    def use_old_tomwer_axis(self, use_old_tomwer_axis):
        use_old_tomwer_axis = bool(use_old_tomwer_axis)
        if self.__use_old_tomwer_axis != use_old_tomwer_axis:
            self.__use_old_tomwer_axis = bool(use_old_tomwer_axis)
            self.changed()

    def to_dict(self):
        return {
            "DO_AXIS_CORRECTION": str(int(self.do_axis_correction)),
            "USE_TOMWER_AXIS": str(int(self.use_tomwer_axis)),
            "TRY_USE_OLD_TOMWER_AXIS": str(int(self.use_tomwer_axis)),
        }

    @staticmethod
    def from_dict(_dict):
        axis = AxisRP()
        axis.load_from_dict(_dict=_dict)
        return axis

    def load_from_dict(self, _dict):
        try:
            self.do_axis_correction = int(_dict["DO_AXIS_CORRECTION"])
        except KeyError:
            _logger.info('no "DO_AXIS_CORRECTION" key')
        try:
            self.use_tomwer_axis = int(_dict["USE_TOMWER_AXIS"])
        except KeyError:
            _logger.info('no "USE_TOMWER_AXIS" key')
        try:
            self.use_old_tomwer_axis = int(_dict["TRY_USE_OLD_TOMWER_AXIS"])
        except KeyError:
            _logger.info('no "TRY_USE_OLD_TOMWER_AXIS" key')
