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
__date__ = "16/11/2020"


import logging
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.process.task import Task
from tomwer.core.scan.scanfactory import ScanFactory
from silx.utils.enum import Enum as _Enum
from tomwer.utils import docstring
import tomwer.version
import os

_logger = logging.getLogger(__name__)


class OutputType(_Enum):
    STATIC = "static"
    ONE_LEVEL_UPPER = "../volume"


def create_volume_symbolic_link(scan: TomwerScanBase, output_folder: str):
    """
    Create a symbolic link for each volume reconstructed of `scan`

    :param TomwerScanBase scan:
    :param str output_folder:
    """
    if scan.latest_vol_reconstructions is None:
        _logger.info("No volume reconstructed found")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for volume_url in scan.latest_vol_reconstructions:
        dst = os.path.join(output_folder, os.path.basename(volume_url.file_path()))
        if os.path.exists(dst):
            _logger.info("{} already exists. Cannot create a symbolic link on it")
        else:
            os.symlink(src=volume_url.file_path(), dst=dst)


class VolumeSymbolicLinkProcess(Task, input_names=("data",), output_names=("data",)):
    """
    Process class for volume symbolic link
    """

    def __init__(self, varinfo=None, inputs=None, label=None):
        super().__init__(varinfo=varinfo, inputs=inputs, label=label)
        self._output_type = OutputType.ONE_LEVEL_UPPER
        self._output_folder = None

    @docstring(Task.set_configuration)
    def set_configuration(self, properties):
        if "output_type" in properties:
            self._output_type = OutputType.from_value(properties["output_type"])
        if "output_folder" in properties:
            self._output_folder = properties["output_folder"]

    @docstring(Task.program_name)
    @staticmethod
    def program_name():
        return "tomwer_volume_symlink"

    @docstring(Task.program_version)
    @staticmethod
    def program_version():
        return tomwer.version.version

    @docstring(Task.run)
    def run(self):
        scan = self.inputs.data
        if type(scan) is dict:
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            scan = scan
        if scan is None:
            return
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(
                "scan is expected to be a dict or an instance "
                "of TomwerScanBase. Not {}".format(type(scan))
            )

        if self._output_type is OutputType.STATIC:
            if self._output_folder is None:
                raise ValueError(
                    "Manual setting of the output folder is "
                    "requested but None is provided."
                )
            else:
                output_folder = self._output_folder
                if not os.path.isabs(output_folder):
                    os.path.abspath(
                        os.path.join(os.path.realpath(scan.path), output_folder)
                    )
        elif self._output_type is OutputType.ONE_LEVEL_UPPER:
            output_folder = os.path.realpath(scan.path)
            output_folder = os.path.abspath(
                os.path.join(output_folder, self._output_type.value)
            )
        else:
            raise ValueError(
                "output type {} is not managed".format(self._output_type.value)
            )
        create_volume_symbolic_link(scan=scan, output_folder=output_folder)
        self.outputs.data = scan

    @docstring(Task.definition)
    @staticmethod
    def definition():
        return "Create a symbolic link to the volume folder"
