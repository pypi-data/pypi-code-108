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
__date__ = "05/03/2019"


from .base import _ReconsParam
from ....utils import _assert_param_instance, _assert_cast_to_boolean
from silx.utils.enum import Enum as _Enum
from collections.abc import Iterable


class PaganinMode(_Enum):
    off = 0
    on = 1
    both = 2
    multi = 3


class PaganinRP(_ReconsParam):
    """
    Paganin parameters to use during ftseries process
    """

    def __init__(self):
        _ReconsParam.__init__(self)
        self.__mode = PaganinMode.off
        self.__db = 500.0
        self.__db2 = 100.0
        self.__unsharp_sigma = 0.8
        self.__unsharp_coeff = 3.0
        self.__threshold = 500
        self.__dilate = 2
        self.__median_r = 4
        self.__keep_bone = False
        self.__keep_soft = False
        self.__keep_abs = False
        self.__keep_corr = False
        self.__keep_mask = False

        self._managed_params = {
            "MODE": self.__class__.mode,
            "DB": self.__class__.db,
            "DB2": self.__class__.db2,
            "UNSHARP_SIGMA": self.__class__.unsharp_sigma,
            "UNSHARP_COEFF": self.__class__.unsharp_coeff,
            "THRESHOLD": self.__class__.threshold,
            "DILATE": self.__class__.dilate,
            "MEDIANR": self.__class__.median_r,
            "MKEEP_BONE": self.__class__.mkeep_bone,
            "MKEEP_SOFT": self.__class__.mkeep_soft,
            "MKEEP_ABS": self.__class__.mkeep_abs,
            "MKEEP_CORR": self.__class__.mkeep_corr,
            "MKEEP_MASK": self.__class__.mkeep_mask,
        }

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, mode):
        _assert_param_instance(mode, (PaganinMode, int))
        _mode = mode
        if isinstance(_mode, int):
            _mode = PaganinMode(_mode)
        self.__mode = _mode
        self.changed()

    @property
    def db(self):
        """value of delta/beta"""
        return self.__db

    @staticmethod
    def _get_db_fromstr(vals):
        vals = vals.replace(" ", "")
        vals = vals.replace("(", "")
        vals = vals.replace(")", "")
        vals = vals.replace("]", "")
        vals = vals.replace("[", "")
        vals = vals.replace(";", ",").split(",")
        if vals[-1] == "":
            del vals[-1]

        res = []
        [res.append(float(val)) for val in vals]
        if len(res) == 1:
            return res[0]
        else:
            return tuple(res)

    @db.setter
    def db(self, value):
        _assert_param_instance(value, (int, float, str))
        if isinstance(value, str):
            _db = self._get_db_fromstr(vals=value)
        else:
            _db = value
        if _db != self.__db:
            self.__db = _db
            self.changed()

    @property
    def db2(self):
        return self.__db2

    @db2.setter
    def db2(self, value):
        _assert_param_instance(value, (int, float, str))
        if isinstance(value, str):
            _db2 = self._get_db_fromstr(vals=value)
        else:
            _db2 = value
        if _db2 != self.__db2:
            self.__db2 = _db2
            self.changed()

    @property
    def unsharp_sigma(self):
        """size of the mask of unsharp masking"""
        return self.__unsharp_sigma

    @unsharp_sigma.setter
    def unsharp_sigma(self, value):
        """coeff for unsharp masking"""
        _assert_param_instance(value, float)
        if self.__unsharp_sigma != value:
            self.__unsharp_sigma = value
            self.changed()

    @property
    def unsharp_coeff(self):
        return self.__unsharp_coeff

    @unsharp_coeff.setter
    def unsharp_coeff(self, value):
        _assert_param_instance(value, float)
        if self.__unsharp_coeff != value:
            self.__unsharp_coeff = value
            self.changed()

    @property
    def threshold(self):
        return self.__threshold

    @threshold.setter
    def threshold(self, value):
        _assert_param_instance(value, (int, float))
        if self.__threshold != float(value):
            self.__threshold = float(value)
            self.changed()

    @property
    def dilate(self):
        return self.__dilate

    @dilate.setter
    def dilate(self, value):
        if self.__dilate != value:
            self.__dilate = value
            self.changed()

    @property
    def median_r(self):
        return self.__median_r

    @median_r.setter
    def median_r(self, value):
        if self.__median_r != value:
            self.__median_r = value
            self.changed()

    @property
    def mkeep_bone(self):
        return self.__keep_bone

    @mkeep_bone.setter
    def mkeep_bone(self, keep):
        # TODO: float should be removed, but this is a legacy from fastomo3
        _assert_param_instance(keep, (int, bool, float))
        _assert_cast_to_boolean(keep)
        if self.__keep_bone != bool(keep):
            self.__keep_bone = bool(keep)
            self.changed()

    @property
    def mkeep_soft(self):
        return self.__keep_soft

    @mkeep_soft.setter
    def mkeep_soft(self, keep):
        # TODO: float should be removed, but this is a legacy from fastomo3
        _assert_param_instance(keep, (int, bool, float))
        _assert_cast_to_boolean(keep)
        if self.__keep_soft != bool(keep):
            self.__keep_soft = bool(keep)
            self.changed()

    @property
    def mkeep_abs(self):
        return self.__keep_abs

    @mkeep_abs.setter
    def mkeep_abs(self, keep):
        # TODO: float should be removed, but this is a legacy from fastomo3
        _assert_param_instance(keep, (int, bool, float))
        _assert_cast_to_boolean(keep)
        if self.__keep_abs != bool(keep):
            self.__keep_abs = bool(keep)
            self.changed()

    @property
    def mkeep_corr(self):
        return self.__keep_corr

    @mkeep_corr.setter
    def mkeep_corr(self, keep):
        _assert_param_instance(keep, (int, bool, float))
        _assert_cast_to_boolean(keep)
        if self.__keep_corr != bool(keep):
            self.__keep_corr = bool(keep)
            self.changed()

    @property
    def mkeep_mask(self):
        return self.__keep_mask

    @mkeep_mask.setter
    def mkeep_mask(self, keep):
        _assert_param_instance(keep, (int, bool, float))
        _assert_cast_to_boolean(keep)
        if self.__keep_mask != bool(keep):
            self.__keep_mask = bool(keep)
            self.changed()

    def to_dict(self):
        _dict = {
            "MODE": self.mode.value,
            "DB": str(self.db),
            "DB2": str(self.db2),
            "UNSHARP_SIGMA": self.unsharp_sigma,
            "UNSHARP_COEFF": self.unsharp_coeff,
            "THRESHOLD": self.threshold,
            "DILATE": self.dilate,
            "MEDIANR": self.median_r,
            "MKEEP_BONE": self.mkeep_bone,
            "MKEEP_SOFT": self.mkeep_soft,
            "MKEEP_ABS": self.mkeep_abs,
            "MKEEP_CORR": self.mkeep_corr,
            "MKEEP_MASK": self.mkeep_mask,
        }
        _dict.update(self.unmanaged_params)
        return _dict

    @staticmethod
    def from_dict(_dict: dict):
        recons_param = PaganinRP()
        recons_param.load_from_dict(_dict)
        return recons_param

    def load_from_dict(self, _dict: dict) -> None:
        self._load_unmanaged_params(_dict)
        self.mode = PaganinMode(_dict["MODE"])
        self.db = _dict["DB"]
        self.db2 = _dict["DB2"]
        self.unsharp_sigma = _dict["UNSHARP_SIGMA"]
        self.unsharp_coeff = _dict["UNSHARP_COEFF"]
        self.threshold = _dict["THRESHOLD"]
        self.dilate = _dict["DILATE"]
        self.median_r = _dict["MEDIANR"]
        self.mkeep_bone = _dict["MKEEP_BONE"]
        self.mkeep_soft = _dict["MKEEP_SOFT"]
        self.mkeep_abs = _dict["MKEEP_ABS"]
        self.mkeep_corr = _dict["MKEEP_CORR"]
        self.mkeep_mask = _dict["MKEEP_MASK"]

    def has_several_db_param(self) -> bool:
        """

        :return: True if the reconstruction contains several delta/beta values.
                 If the paganin mode is off will return False by default,
                 No matter the values of db and db2
        """
        if self.mode is PaganinMode.off:
            return False
        if isinstance(self.db, Iterable) and len(self.db) > 1:
            return True
        if isinstance(self.db2, Iterable) and len(self.db2) > 1:
            return True
        return False
