# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017-2019 European Synchrotron Radiation Facility
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
__date__ = "03/02/2021"


from tomwer.test.utils import skip_gui_test
from tomwer.gui.reconstruction.saaxis.dimensionwidget import DimensionWidget
from tomoscan.unitsystem import metricsystem
from silx.gui.utils.testutils import TestCaseQt
from tomwer.core.utils.scanutils import MockHDF5
from tomwer.gui.reconstruction.saaxis.saaxis import SAAxisWindow
from tomwer.core.process.reconstruction.saaxis.params import (
    SAAxisParams,
    ReconstructionMode,
)
from tomwer.core.process.reconstruction.scores import ComputedScore
from tomwer.core.process.reconstruction.scores.params import ScoreMethod
from silx.io.url import DataUrl
from silx.gui import qt
import unittest
import pytest
import numpy
import shutil
import tempfile
import os
import h5py


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDimensionWidget(TestCaseQt):
    """Test that the axis widget work correctly"""

    def setUp(self):
        self._window = DimensionWidget(title="test window")

    def tearDown(self):
        self._window.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._window.close()

    def testDimension(self):
        """Insure setting dimensions values and unit are correct"""
        self.assertTrue(self._window.unit() is metricsystem.MetricSystem.MILLIMETER)
        # check initial values
        self.assertEqual(
            self._window.getValues(),
            (0.001, 0.001, 0.001, metricsystem.MetricSystem.METER),
        )
        # set dim 0 to 20 mm
        self._window._dim0ValueQLE.setValue(20)
        self._window._dim0ValueQLE.editingFinished.emit()
        self.qapp.processEvents()
        self.assertEqual(
            self._window.getValues(),
            (0.02, 0.001, 0.001, metricsystem.MetricSystem.METER),
        )
        # set dim 1 to 0.6 millimeter
        self._window._dim1ValueQLE.setValue(0.6)
        self._window._dim1ValueQLE.editingFinished.emit()
        self.qapp.processEvents()
        self.assertEqual(
            self._window.getValues(),
            (0.02, 0.0006, 0.001, metricsystem.MetricSystem.METER),
        )
        # change display to micrometer
        self._window.setUnit(metricsystem.MetricSystem.MICROMETER)
        self.assertEqual(
            self._window.getValues(),
            (0.02, 0.0006, 0.001, metricsystem.MetricSystem.METER),
        )
        self.assertEqual(
            self._window._dim0ValueQLE.value(),
            20
            * metricsystem.MetricSystem.MILLIMETER.value
            / metricsystem.MetricSystem.MICROMETER.value,
        )
        self._window._dim2ValueQLE.setValue(500)
        self._window._dim2ValueQLE.editingFinished.emit()
        self.qapp.processEvents()
        self.assertEqual(
            self._window.getValues(),
            (0.02, 0.0006, 0.0005, metricsystem.MetricSystem.METER),
        )

    def testConstructorWithColors(self):
        """Insure passing colors works"""
        DimensionWidget(title="title", dims_colors=("#ffff5a", "#62efff", "#ff5bff"))

    def testConstructorWithdimNames(self):
        """Insure passing colors works"""
        DimensionWidget(title="title", dims_name=("x", "y", "z"))


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestSAAxisWindow(TestCaseQt):
    """Test the SAAxisWindow interface"""

    _N_OUTPUT_URLS = 10

    def setUp(self):
        super().setUp()
        self._window = SAAxisWindow()
        self.folder = tempfile.mkdtemp()
        self._output_urls = []
        self._cor_scores = {}

        for i in range(self._N_OUTPUT_URLS):
            output_file = os.path.join(self.folder, "recons_{}.h5".format(i))
            with h5py.File(output_file, mode="a") as h5f:
                h5f["data"] = numpy.random.random(100 * 100).reshape(100, 100)
                url = DataUrl(file_path=output_file, data_path="data", scheme="silx")
                assert url.is_valid()
            self._output_urls.append(url)
            score = ComputedScore(
                tv=numpy.random.randint(10),
                std=numpy.random.randint(100),
            )
            self._cor_scores[i] = (url, score)

        # create a scan
        self.folder = tempfile.mkdtemp()
        dim = 10
        mock = MockHDF5(
            scan_path=self.folder, n_proj=10, n_ini_proj=10, scan_range=180, dim=dim
        )
        mock.add_alignment_radio(index=10, angle=90)
        mock.add_alignment_radio(index=10, angle=0)
        self.scan = mock.scan

        self._window.setScan(self.scan)

    def tearDown(self):
        self._window.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._window.close()
        self._window = None
        shutil.rmtree(self.folder)
        super().tearDown()

    def testGetConfiguration(self):
        """Insure configuration getter works"""
        conf = self._window.getConfiguration()
        # the configuration should be convertible to
        conf = SAAxisParams.from_dict(conf)
        self.assertEqual(conf.slice_indexes, "middle")
        self.assertEqual(conf.file_format, "hdf5")
        self.assertTrue(isinstance(conf.nabu_params, dict))
        for key in (
            "preproc",
            "reconstruction",
            "dataset",
            "tomwer_slices",
            "output",
            "phase",
        ):
            with self.subTest(key=key):
                self.assertTrue(key in conf.nabu_params)
        self.assertEqual(conf._dry_run, False)
        self.assertEqual(conf.mode, ReconstructionMode.VERTICAL)
        self.assertEqual(conf.score_method, ScoreMethod.TV_INVERSE)
        self.assertEqual(conf.output_dir, None)
        self.assertEqual(conf.scores, None)

    def testSetConfiguration(self):
        """Insure configuration setter works"""
        self._window.setSlicesRange(0, 20)
        configuration = {
            "slice_indexes": {"Slice": 2},
            "estimated_cor": 0.24,
            "research_width": 0.8,
            "n_reconstruction": 5,
        }
        self._window.setConfiguration(configuration)
        res_conf = self._window.getConfiguration()
        for key in (
            "slice_indexes",
            "estimated_cor",
            "research_width",
            "n_reconstruction",
        ):
            self.assertEqual(configuration[key], res_conf[key])

    def testSetResults(self):
        """Test setting results"""
        self._window.setCorScores(self._cor_scores, score_method="standard deviation")


def suite():
    test_suite = unittest.TestSuite()
    for ui in (
        TestDimensionWidget,
        TestSAAxisWindow,
    ):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
    return test_suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
