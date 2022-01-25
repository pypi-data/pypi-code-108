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
"""Utils for devices (GPU, CPU...)"""

__authors__ = ["H. Payno"]

try:
    import pycuda.driver as cuda
except ImportError:
    cuda = None
from silx.opencl import ocl


class _DeviceBase:
    """base class for device definition"""

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class OpenCLDevice(_DeviceBase):
    """Definition of an opencl device"""

    def __init__(self, name, platform_id, device_id):
        super(OpenCLDevice, self).__init__(name=name)
        self._platform_id = platform_id
        self._device_id = device_id

    @property
    def platform_id(self):
        return self._platform_id

    @property
    def device_id(self):
        return self._device_id


class CudaDevice(_DeviceBase):
    """Definition of an opencl device"""

    def __init__(self, name, id_):
        super(CudaDevice, self).__init__(name=name)
        self._id = id_

    @property
    def id(self):
        """

        :return: ID of the cuda device
        :rtype: int
        """
        return self._id


class _CudaPlatformBase:
    def getExistingDevices(self):
        """

        :return: all existing cuda device
        """
        devices = []
        if cuda is not None:
            cuda.init()
            for i_device in range(cuda.Device.count()):
                device = CudaDevice(cuda.Device(i_device).name(), id_=i_device)
                devices.append(device)
        return devices


class _OpenCLPlatformBase:
    def getExistingDevices(self):
        """

        :return: all existing opencl platform
        """
        devices = []
        if ocl is not None:
            for platform_id, platform in enumerate(ocl.platforms):
                for device_id, dev in enumerate(platform.devices):
                    devices.append(
                        OpenCLDevice(
                            name=dev.name, platform_id=platform_id, device_id=device_id
                        )
                    )
        return devices
