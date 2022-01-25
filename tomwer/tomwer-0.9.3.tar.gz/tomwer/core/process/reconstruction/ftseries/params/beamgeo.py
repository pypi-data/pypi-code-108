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
from .base import _ReconsParam


@enum.unique
class BeamGeoType(enum.Enum):
    parallel = (0,)
    fan = (2,)
    conical = (3,)


class BeamGeoRP(_ReconsParam):
    """Beam geometry reconstruction parameters"""

    def __init__(self):
        _ReconsParam.__init__(self)
        self.__type = BeamGeoType.parallel
        self.__sx = 0.0
        self.__sy = 0.0
        self.__dist = 55.0

        self._managed_params = {
            "TYPE": self.__class__.type,
            "SX": self.__class__.sx,
            "SY": self.__class__.sy,
            "DIST": self.__class__.dist,
        }

    @property
    def type(self):
        """Beam geometry type"""
        return self.__type

    @type.setter
    def type(self, _type):
        assert isinstance(_type, (BeamGeoType, int, str))
        if type(_type) is str:
            __type = self._get_beam_geo_frm_letter(_type)
        else:
            __type = BeamGeoType(_type)
        if __type != self.__type:
            self.__type = __type
            self.changed()

    @property
    def sx(self):
        """Source position on vertical axis(X)"""
        return self.__sx

    @sx.setter
    def sx(self, value):
        assert isinstance(value, float)
        if self.__sx != value:
            self.__sx = value
            self.changed()

    @property
    def sy(self):
        """Source position on vertical axis(Y)"""
        return self.__sy

    @sy.setter
    def sy(self, value):
        assert isinstance(value, float)
        if value != self.__sy:
            self.__sy = value
            self.changed()

    @property
    def dist(self):
        """Source distance in meters"""
        return self.__dist

    @dist.setter
    def dist(self, dist):
        assert isinstance(dist, float)
        if self.__dist != dist:
            self.__dist = dist
            self.changed()

    def to_dict(self):
        _dict = {
            "TYPE": self.type.name[0],
            "SX": self.sx,
            "SY": self.sy,
            "DIST": self.dist,
        }
        _dict.update(self.unmanaged_params)
        return _dict

    @staticmethod
    def from_dict(_dict):
        params = BeamGeoRP()
        params.load_from_dict(_dict)
        return params

    def load_from_dict(self, _dict):
        self._load_unmanaged_params(_dict)
        self.type = self._get_beam_geo_frm_letter(_dict["TYPE"])
        self.sx = _dict["SX"]
        self.sy = _dict["SY"]
        self.dist = _dict["DIST"]

    @staticmethod
    def _get_beam_geo_frm_letter(letter):
        if letter.lower() == "p":
            return BeamGeoType.parallel
        elif letter.lower() == "f":
            return BeamGeoType.fan
        elif letter.lower() == "c":
            return BeamGeoType.conical
        else:
            raise ValueError("Invalid beam geometry type (%s)" % letter)
