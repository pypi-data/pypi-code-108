# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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
#############################################################################*/


__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "03/08/2020"


from tomwer.core.process.task import Task
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.scan.edfscan import EDFTomoScan
import tomwer.version
import logging
import code


_logger = logging.getLogger(__name__)


class PythonScript(Task, input_names=("data",), output_names=("data",)):
    def run(self):
        scan = self.inputs.data
        if isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        elif isinstance(scan, TomwerScanBase):
            scan = scan
        else:
            raise ValueError(
                "input type of {}: {} is not managed" "".format(scan, type(scan))
            )

        cfg = self.get_configuration()
        interpreter = code.InteractiveConsole(locals={"in_data": scan})
        interpreter.runcode(cfg["scriptText"])
        res = interpreter.locals.get("out_data")

        # register process
        if isinstance(scan, EDFTomoScan):
            entry = None
        else:
            entry = scan.entry

        results = {}
        if res is not None:
            if hasattr(res, "to_dict"):
                results = res.to_dict()
            else:
                results = res
        try:
            self.register_process(
                process_file=scan.process_file,
                entry=entry,
                configuration={"scriptText": self.get_configuration()["scriptText"]},
                results=results,
                process_index=scan.pop_process_index(),
                overwrite=True,
            )
        except Exception as e:
            _logger.error("Fail to register process. Error is " + str(e))

        self.outputs.data = res

    @staticmethod
    def program_name():
        """Name of the program used for this processing"""
        return "Python script"

    @staticmethod
    def program_version():
        """version of the program used for this processing"""
        return tomwer.version.version

    @staticmethod
    def definition():
        """definition of the process"""
        return "Execute some random python code"
