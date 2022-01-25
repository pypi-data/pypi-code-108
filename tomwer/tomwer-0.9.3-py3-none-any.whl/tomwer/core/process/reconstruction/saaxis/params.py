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


from collections.abc import Iterable
from typing import Union
from silx.utils.enum import Enum as _Enum
from tomwer.core.process.reconstruction.scores.params import SABaseParams
import numpy


class ReconstructionMode(_Enum):
    VERTICAL = "Vertical"
    TILT_CORRECTION = "Tilt correction"


class SAAxisParams(SABaseParams):
    """Parameters for the semi-automatic axis calculation"""

    def __init__(self):
        super().__init__()
        self._research_width = 10  # in pixel
        self._estimated_cor = None
        self._n_reconstruction = 20
        self._mode = ReconstructionMode.VERTICAL
        self._image_width = None
        self._cluster_config = None

    @property
    def research_width(self):
        return self._research_width

    @research_width.setter
    def research_width(self, research_width):
        self._research_width = research_width

    @property
    def estimated_cor(self):
        return self._estimated_cor

    @estimated_cor.setter
    def estimated_cor(self, estimated_cor):
        self._estimated_cor = estimated_cor

    @property
    def cors(self) -> Iterable:
        return self.compute_cors(
            estimated_cor=self.estimated_cor,
            research_width=self.research_width,
            n_reconstruction=self.n_reconstruction,
        )

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        mode = ReconstructionMode.from_value(mode)
        self._mode = mode

    @property
    def image_width(self) -> Union[None, float]:
        return self._image_width

    @image_width.setter
    def image_width(self, width):
        if not isinstance(width, (type(None), float, int)):
            raise TypeError("None, int or float expected. Not {}".format(type(width)))
        else:
            self._image_width = width

    def to_dict(self):
        ddict = super().to_dict()
        ddict.update(
            {
                "estimated_cor": self.estimated_cor,
                "research_width": self.research_width,
                "n_reconstruction": self.n_reconstruction,
                "mode": self.mode.value,
            }
        )
        return ddict

    def load_from_dict(self, dict_: dict):
        super().load_from_dict(dict_)
        if "research_width" in dict_:
            self.research_width = dict_["research_width"]
        if "estimated_cor" in dict_:
            self.estimated_cor = dict_["estimated_cor"]
        if "n_reconstruction" in dict_:
            self.n_reconstruction = dict_["n_reconstruction"]
        if "mode" in dict_:
            self.mode = ReconstructionMode.from_value(dict_["mode"])

    @staticmethod
    def from_dict(dict_):
        params = SAAxisParams()
        params.load_from_dict(dict_=dict_)
        return params

    def check_configuration(self):
        """
        Insure all requested information for processing the SAAXis are here.
        :raises: ValueError if some information are missing
        """
        missing_information = []
        if self.cors is None or len(self.cors) == 0:
            missing_information.append("no values for center of rotation provided")
        if self.slice_indexes is None:
            missing_information.append("slice index not provided")
        if len(missing_information) > 0:
            raise ValueError(
                str(
                    "Some informations are missing: {}".format(
                        " ; ".join(missing_information)
                    )
                )
            )

    @staticmethod
    def compute_cors(estimated_cor, research_width, n_reconstruction):
        if estimated_cor is None:
            raise ValueError("No estimated cor provided")
        if estimated_cor == "middle":
            estimated_cor = 0
        if n_reconstruction % 2 == 0:
            n_reconstruction = n_reconstruction + 1
            # insure we have an odd number of cor to insure the estimated
            # one is reconstructed
        if n_reconstruction == 1:
            return (estimated_cor,)
        return numpy.linspace(
            start=estimated_cor - research_width / 2.0,
            stop=estimated_cor + research_width / 2.0,
            num=n_reconstruction,
        )
