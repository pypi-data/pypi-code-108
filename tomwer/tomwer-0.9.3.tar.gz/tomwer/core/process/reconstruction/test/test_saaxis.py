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
__date__ = "27/02/2021"


import unittest
from tomwer.core.process.reconstruction.scores.scores import compute_score_contrast_std
from tomwer.core.process.reconstruction.scores.scores import _METHOD_TO_FCT
from tomwer.core.process.reconstruction.saaxis.saaxis import SAAxisProcess
from tomwer.core.process.reconstruction.saaxis.params import SAAxisParams
from tomwer.core.utils.scanutils import MockHDF5
import os
import tempfile
import shutil
import numpy


class TestScoreFunctions(unittest.TestCase):
    """Test all the score functions"""

    def test_img_contrast_std_score(self):
        """simple test of the API to call compute_score_contrast_std"""
        data = numpy.random.random(100 * 100).reshape(100, 100)
        compute_score_contrast_std(data)

    def test_method_to_function(self):
        """Test the dictionary used to for linking the score method to the
        callback function"""
        data = numpy.random.random(100 * 100).reshape(100, 100)
        for method_name, fct in _METHOD_TO_FCT.items():
            with self.subTest(method_name=method_name, fct=fct):
                res = fct(data)
                self.assertFalse(res is None)
                self.assertTrue(isinstance(res, float))


class TestSAAxisProcess(unittest.TestCase):
    """Test the SAAxisProcess class"""

    def setUp(self) -> None:
        self.tempdir = tempfile.mkdtemp()
        dim = 10
        mock = MockHDF5(
            scan_path=self.tempdir, n_proj=10, n_ini_proj=10, scan_range=180, dim=dim
        )
        mock.add_alignment_radio(index=10, angle=90)
        mock.add_alignment_radio(index=10, angle=0)
        self.scan = mock.scan

        self._default_saaxis_params = SAAxisParams()
        self._default_saaxis_params.output_dir = os.path.join(
            self.tempdir, "output_dir"
        )
        self._default_saaxis_params.slice_indexes = {"slice": 4}
        self._default_saaxis_params.nabu_config = {}
        self._default_saaxis_params.dry_run = True
        self._default_saaxis_params.file_format = "hdf5"

    def tearDown(self) -> None:
        shutil.rmtree(self.tempdir)

    def test(self):
        process = SAAxisProcess(inputs={"data": self.scan})
        with self.assertRaises(Exception):
            process.run()
        process.set_configuration(self._default_saaxis_params)
        with self.assertRaises(ValueError):
            process.run()
        self._default_saaxis_params.estimated_cor = 11
        self._default_saaxis_params.research_width = 2
        process.set_configuration(self._default_saaxis_params)
        process.run()
        process = SAAxisProcess(
            inputs={"data": self.scan, "sa_axis_params": self._default_saaxis_params}
        )
        process.run()
