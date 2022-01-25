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
from ....utils import _assert_cast_to_boolean, _assert_param_instance
from collections.abc import Iterable
import logging

_logger = logging.getLogger(__name__)


class PyhstRP(_ReconsParam):

    OFFV = "pyhst2"

    def __init__(self):
        _ReconsParam.__init__(self)
        self.__offv = PyhstRP.OFFV
        # textread([self.DIR self.OFFN], '%s'){1} # ne dois jamais changer On ne la presente pas
        self.__pyhst_exe = PyhstRP.OFFV
        self.__verbose_file = "pyhst_out.txt"
        self.__verbose = False
        self.__make_oar_file = False
        self._cuda_devices = None
        """Cuda gpu devices to use for the reconstruction. For now limited on
        local gpu device"""

        self._managed_params = {
            "OFFV": self.__class__._offv,
            "EXE": self.__class__.pyhst_exe,
            "VERBOSE_FILE": self.__class__.verbose_file,
            "VERBOSE": self.__class__.verbose,
            "MAKE_OAR_FILE": self.__class__.make_oar_file,
            "CUDA_DEVICES": self.__class__.cuda_devices,
        }

    @property
    def offv(self):
        return self.__offv

    @offv.setter
    def offv(self, offv):
        if self.__offv != offv:
            self.__offv = offv
            self.changed()

    @property
    def pyhst_exe(self):
        """name of the pyhste executable"""
        return self.__pyhst_exe

    @pyhst_exe.setter
    def pyhst_exe(self, exe_name):
        if self.__pyhst_exe != exe_name:
            self.__pyhst_exe = exe_name
            self.changed()

    @property
    def _offv(self):
        return self.__offv

    @_offv.setter
    def _offv(self, offv):
        if self.__offv != offv:
            self.__offv = offv
            self.changed()

    @property
    def verbose_file(self):
        """output file name if verbose is activated"""
        return self.__verbose_file

    @verbose_file.setter
    def verbose_file(self, file_name):
        if self.__verbose_file != file_name:
            self.__verbose_file = file_name
            self.changed()

    @property
    def verbose(self):
        return self.__verbose

    @verbose.setter
    def verbose(self, activate):
        assert isinstance(activate, (bool, int, float))
        if self.__verbose != bool(activate):
            self.__verbose = bool(activate)
            self.changed()

    @property
    def make_oar_file(self):
        return self.__make_oar_file

    @make_oar_file.setter
    def make_oar_file(self, make):
        _assert_param_instance(make, (bool, int, float))
        _assert_cast_to_boolean(make)
        if self.__make_oar_file != bool(make):
            self.__make_oar_file = bool(make)
            self.changed()

    @property
    def cuda_devices(self):
        """

        :return: list of cuda devices to use
        """
        return self._cuda_devices

    @cuda_devices.setter
    def cuda_devices(self, devices):
        """

        :param Union[list,None,str] devices: list of :class:`CudaDevice`
        :return: list of :class:`CudaDevice`
        """
        if isinstance(devices, Iterable):
            if len(devices) == 0:
                self._cuda_devices = None
            else:
                from tomwer.core.utils.device import CudaDevice

                self._cuda_devices = []
                for item in devices:
                    if isinstance(item, CudaDevice):
                        self._cuda_devices.append(item.id)
                    else:
                        self._cuda_devices.append(item)
        elif devices in ("", None):
            # string used to store 'no device' state
            self._cuda_devices = None
        else:
            raise TypeError(
                "devices is expected to be None or an Iterable containing instances of CudaDevice"
            )

    def to_dict(self):
        if self._cuda_devices is not None:
            cuda_devices_id = self.cuda_devices
        else:
            cuda_devices_id = ""
        _dict = {
            "OFFV": self.offv,
            "EXE": self.pyhst_exe,
            "VERBOSE_FILE": self.verbose_file,
            "VERBOSE": self.verbose,
            "MAKE_OAR_FILE": self.make_oar_file,
            "CUDA_DEVICES": cuda_devices_id,
        }
        _dict.update(self.unmanaged_params)
        return _dict

    @staticmethod
    def from_dict(_dict):
        recons_param = PyhstRP()
        recons_param.load_from_dict(_dict)
        return recons_param

    def load_from_dict(self, _dict):
        self._load_unmanaged_params(_dict)
        self.offv = _dict["OFFV"]
        self.pyhst_exe = _dict["EXE"]
        self.verbose_file = _dict["VERBOSE_FILE"]
        self.verbose = _dict["VERBOSE"]
        self.make_oar_file = _dict["MAKE_OAR_FILE"]
        try:
            self.cuda_devices = _dict["CUDA_DEVICES"]
        except KeyError:
            _logger.info('no "CUDA_DEVICES" key')
