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
__date__ = "04/05/2021"


from tomwer.core.process.reconstruction.scores.params import SABaseParams
from tomwer.core.process.reconstruction.nabu.utils import retrieve_lst_of_value_from_str
import typing


class SADeltaBetaParams(SABaseParams):
    """Parameters for the semi-automatic axis calculation"""

    def __init__(self):
        super().__init__()
        self._delta_beta_values = (100,)
        self._selected_db = None

    @property
    def delta_beta_values(self):
        return self._delta_beta_values

    @delta_beta_values.setter
    def delta_beta_values(self, delta_beta_values):
        if isinstance(delta_beta_values, str):
            self._delta_beta_values = retrieve_lst_of_value_from_str(
                delta_beta_values, type_=float
            )
        else:
            self._delta_beta_values = delta_beta_values

    def set_db_selected_value(self, value):
        self._selected_db = value

    @property
    def selected_delta_beta_value(self) -> typing.Union[None, float]:
        return self._selected_db

    def to_dict(self) -> dict:
        dict = super().to_dict()
        dict.update(
            {
                "delta_beta_values": self.delta_beta_values,
                "selected_db_value": self.selected_delta_beta_value,
            }
        )
        return dict

    def load_from_dict(self, dict_: dict):
        if not isinstance(dict_, dict):
            raise TypeError(
                "dict_ should be an instance of dict not {}".format(type(dict_))
            )
        super().load_from_dict(dict_)
        if "delta_beta_values" in dict_:
            self.delta_beta_values = dict_["delta_beta_values"]
        if "selected_db_value" in dict_:
            self.set_db_selected_value(value=dict["selected_db_value"])

    @staticmethod
    def from_dict(dict_):
        params = SADeltaBetaParams()
        params.load_from_dict(dict_=dict_)
        return params

    def check_configuration(self):
        """
        Insure all requested information for processing the SAAXis are here.
        :raises: ValueError if some information are missing
        """
        missing_information = []
        if self.delta_beta_values is None or len(self.delta_beta_values) == 0:
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

    def __str__(self):
        return str(self.to_dict())
