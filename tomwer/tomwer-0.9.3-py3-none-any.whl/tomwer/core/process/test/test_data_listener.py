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
__date__ = "09/06/2020"


import unittest
import requests
import tempfile
import shutil
import os
import h5py
from tomwer.core.process.control.datalistener.rpcserver import _BaseDataListenerThread


class JSONRPCClient:
    """Simulate call from bliss"""

    def scan_started(self, scan_number):
        return {
            "method": "scan_started",
            "params": [scan_number],
            "jsonrpc": "2.0",
            "id": 0,
        }

    def scan_ended(self, scan_number):
        return {
            "method": "scan_ended",
            "params": [scan_number],
            "jsonrpc": "2.0",
            "id": 1,
        }

    def sequence_started(
        self, saving_file, scan_title, sequence_scan_number, proposal_file, sample_file
    ):
        params = [
            saving_file,
            scan_title,
            sequence_scan_number,
            proposal_file,
            sample_file,
        ]
        return {
            "method": "sequence_started",
            "params": params,
            "jsonrpc": "2.0",
            "id": 2,
        }

    def sequence_ended(self, saving_file, sequence_scan_number, success):
        return {
            "method": "sequence_ended",
            "params": [saving_file, sequence_scan_number, success],
            "jsonrpc": "2.0",
            "id": 3,
        }

    def execute(self):
        url = "http://localhost:4000/jsonrpc"
        timeout = 1.5

        requests.post(
            url,
            json=self.sequence_started(
                saving_file="saving_file.h5",
                scan_title="my scan title",
                entry_name="entry0000",
                proposal_file="ihpropfile.h5",
            ),
            timeout=timeout,
        ).json()
        requests.post(
            url, json=self.scan_started(scan_number="0001"), timeout=timeout
        ).json()
        requests.post(
            url, json=self.scan_ended(scan_number="0001"), timeout=timeout
        ).json()
        requests.post(
            url,
            json=self.sequence_ended(
                saving_file="saving_file.h5", entry_name="entry0000", suceed=True
            ),
            timeout=timeout,
        ).json()


class TestJsonRPCServer(unittest.TestCase):
    """test the json rpc server"""

    def setUp(self):
        self.input_dir = tempfile.mkdtemp()
        sample_dir = os.path.join(self.input_dir, "sample")
        os.makedirs(sample_dir)
        self._proposal_file = os.path.join(sample_dir, "ihpayno_sample.h5")
        with h5py.File(self._proposal_file, mode="w") as h5f:
            h5f["test"] = "toto"

        os.makedirs(os.path.join(sample_dir, "sample_29042021"))
        self._sample_file = os.path.join(
            sample_dir, "sample_29042021", "sample_29042021.h5"
        )
        self._sample_file_entry = "1.1"

        with h5py.File(self._sample_file, mode="w") as h5f:
            h5f[self._sample_file_entry] = "tata"

        self.data_listener = _BaseDataListenerThread(host="localhost", port=4000)

    def tearDown(self):
        shutil.rmtree(self.input_dir)
        self.data_listener.stop()

    def testStartStop(self):
        self.data_listener.start()
        self.data_listener.stop()
