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
__date__ = "07/03/2019"


import enum
from silx.utils.enum import Enum as _Enum
from tomwer.core.process.reconstruction.darkref.settings import (
    DARKHST_PREFIX,
    REFHST_PREFIX,
)
from tomwer.core.process.reconstruction.ftseries.params.base import _ReconsParam
from tomwer.core.utils.deprecation import deprecated


# TODO: those classes (when, method) should be linked / embedded in the DarkRef
# method
@enum.unique
class When(_Enum):
    never = (0,)
    before = (1,)
    after = (2,)


@enum.unique
class Method(_Enum):
    none = (0,)
    average = (1,)
    median = 2
    first = 10
    last = 11

    @classmethod
    def from_value(cls, value):
        if isinstance(value, str):
            for m in Method:
                if value.lower() == m.name.lower():
                    return m
        return super().from_value(value)


class DKRFRP(_ReconsParam):
    """Settings for the calculation of dark and flat fields mean or median"""

    def __init__(self):
        _ReconsParam.__init__(self)
        self.__do_when = When.before
        self.__dark_calc = Method.average
        self.__overwrite_dark = False
        self.__remove_dark = False
        self.__dark_pattern = "darkend[0-9]{3,4}"
        self.__ref_calc = Method.median
        self.__overwrite_flat = False
        self.__remove_ref = False
        self.__ref_pattern = "ref*.*[0-9]{3,4}_[0-9]{3,4}"
        self.__dark_prefix = DARKHST_PREFIX
        self.__ref_prefix = REFHST_PREFIX

        self._managed_params = {
            "DOWHEN": self.__class__.do_when,
            "DARKCAL": self.__class__.dark_calc_method,
            "DARKOVE": self.__class__.overwrite_dark,
            "DARKRMV": self.__class__.remove_dark,
            "DKFILE": self.__class__.dark_pattern,
            "REFSCAL": self.__class__.ref_calc_method,
            "REFSOVE": self.__class__.overwrite_flat,
            "REFSRMV": self.__class__.remove_ref,
            "RFFILE": self.__class__.ref_pattern,
        }

    @property
    def do_when(self):
        """When should we process calculation. Should be removed now that DKRF
        process exists. Was needed for fastomo3"""
        return self.__do_when

    @do_when.setter
    def do_when(self, when):
        assert isinstance(when, (int, When))
        when = When(when)
        if when != self.__do_when:
            self.__do_when = when
            self.changed()

    @property
    def dark_calc_method(self):
        """Dark calculation Method"""
        return self.__dark_calc

    @dark_calc_method.setter
    def dark_calc_method(self, method):
        assert isinstance(method, (int, Method, str))
        if isinstance(method, str):
            _dark_calc = getattr(Method, method.lower())
        else:
            _dark_calc = Method(method)

        if self.__dark_calc != _dark_calc:
            self.__dark_calc = _dark_calc
            self.changed()

    @property
    def overwrite_dark(self):
        """Overwrite Dark results if already exists"""
        return self.__overwrite_dark

    @overwrite_dark.setter
    def overwrite_dark(self, overwrite):
        assert isinstance(overwrite, (int, bool, float))
        _overwrite_dark = bool(overwrite)
        if self.__overwrite_dark != _overwrite_dark:
            self.__overwrite_dark = _overwrite_dark
            self.changed()

    @property
    def remove_dark(self):
        """Remove original Darks files when done"""
        return self.__remove_dark

    @remove_dark.setter
    def remove_dark(self, remove):
        assert isinstance(remove, (int, bool, float))
        _remove_dark = bool(remove)
        if _remove_dark != self.__remove_dark:
            self.__remove_dark = _remove_dark
            self.changed()

    @property
    def dark_pattern(self):
        """File pattern to detect edf Dark field"""
        return self.__dark_pattern

    @dark_pattern.setter
    def dark_pattern(self, pattern):
        _dark_pattern = pattern
        if self.__dark_pattern != _dark_pattern:
            self.__dark_pattern = _dark_pattern
            self.changed()

    @property
    def ref_calc_method(self):
        """Dark calculation method (None, Average, Median)"""
        return self.__ref_calc

    @ref_calc_method.setter
    def ref_calc_method(self, method):
        assert isinstance(method, (int, Method, str))
        if isinstance(method, str):
            _ref_calc = getattr(Method, method.lower())
        else:
            _ref_calc = Method(method)
        if self.__ref_calc != _ref_calc:
            self.__ref_calc = _ref_calc
            self.changed()

    @property
    @deprecated(replacement="overwrite_flat", since_version="0.9")
    def overwrite_ref(self):
        return self.overwrite_flat

    @overwrite_ref.setter
    @deprecated(replacement="overwrite_flat", since_version="0.9")
    def overwrite_ref(self, overwrite):
        self.overwrite_flat = overwrite

    @property
    def overwrite_flat(self):
        """Overwrite Dark results if already exists"""
        return self.__overwrite_flat

    @overwrite_flat.setter
    def overwrite_flat(self, overwrite):
        assert isinstance(overwrite, (int, bool, float))
        _overwrite_flat = bool(overwrite)
        if self.__overwrite_flat != _overwrite_flat:
            self.__overwrite_flat = _overwrite_flat
            self.changed()

    @property
    def remove_ref(self):
        """Remove original ref files when done"""
        return self.__remove_ref

    @remove_ref.setter
    def remove_ref(self, remove):
        # TODO: float should be removed, but this is a legacy from fastomo3
        assert isinstance(remove, (int, bool, float))
        _remove_ref = remove
        if self.__remove_ref != _remove_ref:
            self.__remove_ref = _remove_ref
            self.changed()

    @property
    def ref_pattern(self):
        """File pattern to detect references"""
        return self.__ref_pattern

    @ref_pattern.setter
    def ref_pattern(self, pattern):
        if pattern != self.__ref_pattern:
            self.__ref_pattern = pattern
            self.changed()

    @property
    def ref_prefix(self):
        return self.__ref_prefix

    @ref_prefix.setter
    def ref_prefix(self, prefix):
        if prefix != self.__ref_prefix:
            self.__ref_prefix = prefix
            self.changed()

    @property
    def dark_prefix(self):
        return self.__dark_prefix

    @dark_prefix.setter
    def dark_prefix(self, prefix):
        if prefix != self.__dark_prefix:
            self.__dark_prefix = prefix
            self.changed()

    def _set_remove_opt(self, rm):
        self.remove_ref = rm
        self.remove_dark = rm

    def _set_skip_if_exist(self, skip):
        self.overwrite_flat = not skip
        self.overwrite_dark = not skip

    def to_dict(self):
        _dict = {
            "DOWHEN": self.do_when.name,
            "DARKCAL": self.dark_calc_method.name.split(".")[-1].title(),
            "DARKOVE": int(self.overwrite_dark),
            "DARKRMV": int(self.remove_dark),
            "DKFILE": self.dark_pattern,
            "REFSCAL": self.ref_calc_method.name.split(".")[-1].title(),
            "REFSOVE": int(self.overwrite_flat),
            "REFSRMV": int(self.remove_ref),
            "RFFILE": self.ref_pattern,
        }
        _dict.update(self.unmanaged_params)
        return _dict

    @staticmethod
    def from_dict(_dict):
        params = DKRFRP()
        params.load_from_dict(_dict)
        return params

    def load_from_dict(self, _dict):
        self._load_unmanaged_params(_dict=_dict)
        self.do_when = getattr(When, _dict["DOWHEN"])
        self.dark_calc_method = getattr(Method, _dict["DARKCAL"].lower())
        self.overwrite_dark = _dict["DARKOVE"]
        self.remove_dark = _dict["DARKRMV"]
        self.dark_pattern = _dict["DKFILE"]
        self.ref_calc_method = getattr(Method, _dict["REFSCAL"].lower())
        self.overwrite_flat = _dict["REFSOVE"]
        self.remove_ref = _dict["REFSRMV"]
        self.ref_pattern = _dict["RFFILE"]
