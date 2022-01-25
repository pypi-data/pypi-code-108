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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "05/02/2020"


import os
from silx.gui import qt
from tomwer.test.utils import skip_gui_test
from tomwer.gui.reconstruction.nabu.nabuflow import NabuFlowControl
from tomwer.gui.reconstruction.nabu.nabuconfig.preprocessing import (
    _NabuPreProcessingConfig,
    _RingCorrectionMethod,
)
from tomwer.gui.reconstruction.nabu.nabuconfig.phase import _NabuPhaseConfig
from tomwer.gui.reconstruction.nabu.nabuconfig.reconstruction import (
    _NabuReconstructionConfig,
)
from tomwer.gui.reconstruction.nabu.nabuconfig.output import _NabuOutputConfig
from tomwer.gui.reconstruction.nabu.volume import NabuVolumeWidget
from silx.gui.utils.testutils import TestCaseQt
import pytest


class ProcessClass:
    """Simple class for unit tests"""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestNabuFlow(TestCaseQt):
    def setUp(self) -> None:
        TestCaseQt.setUp(self)
        self.nabuWidget = NabuFlowControl(parent=None, direction="vertical")

    def tearDown(self):
        self.nabuWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.nabuWidget.close()
        del self.nabuWidget

    def testFlow1(self):
        style = qt.QApplication.style()
        icon_1 = style.standardIcon(qt.QStyle.SP_DialogApplyButton)
        icon_2 = style.standardIcon(qt.QStyle.SP_FileLinkIcon)
        icon_3 = style.standardIcon(qt.QStyle.SP_ArrowLeft)
        icon_4 = style.standardIcon(qt.QStyle.SP_ArrowRight)
        icon_5 = style.standardIcon(qt.QStyle.SP_BrowserStop)

        preprocess = "reading files", ProcessClass(name="other preprocessing")
        preprocess_icons = None, icon_1
        self.nabuWidget.setPreProcessing(processes=preprocess, icons=preprocess_icons)

        processes = (
            "processing 1",
            ProcessClass("in between processing"),
            "other processing",
        )
        processes_icons = icon_2, None, icon_3
        self.nabuWidget.setProcessing(processes=processes, icons=processes_icons)

        postprocess = "post processing", ProcessClass("writing result")
        postprocess_icons = icon_4, icon_5
        self.nabuWidget.setPostProcessing(
            processes=postprocess, icons=postprocess_icons
        )


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestNabuPreProcConfig(TestCaseQt):
    def setUp(self):
        TestCaseQt.setUp(self)
        self.nabuWidget = _NabuPreProcessingConfig(parent=None, scrollArea=None)

    def tearDown(self):
        self.nabuWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.nabuWidget.close()
        del self.nabuWidget
        self.qapp.processEvents()
        TestCaseQt.tearDown(self)

    def testGetInitialConfiguration(self):
        """Test that the get configuration is working"""
        ini_conf = {
            "flatfield_enabled": 1,
            "double_flatfield_enabled": 0,
            "dff_sigma": 0.0,
            "ccd_filter_enabled": 0,
            "ccd_filter_threshold": 0.04,
            "log_min_clip": 1e-6,
            "log_max_clip": 10.0,
            "take_logarithm": True,
            "sino_rings_correction": _RingCorrectionMethod.NONE.value,
        }
        self.assertEqual(self.nabuWidget.getConfiguration(), ini_conf)

    def testSetConfiguration(self):
        """Test that the set configuration is working"""
        conf = {
            "flatfield_enabled": 0,
            "double_flatfield_enabled": 1,
            "dff_sigma": 2.0,
            "ccd_filter_enabled": 1,
            "ccd_filter_threshold": 0.98,
            "log_min_clip": 1e-3,
            "log_max_clip": 250.0,
            "take_logarithm": False,
            "sino_rings_correction": _RingCorrectionMethod.MUNCH.value,
        }
        self.nabuWidget.setConfiguration(conf=conf)
        self.assertEqual(self.nabuWidget.getConfiguration(), conf)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestNabuPhaseConfig(TestCaseQt):
    def setUp(self):
        TestCaseQt.setUp(self)
        self.nabuWidget = _NabuPhaseConfig(parent=None, scrollArea=None)

    def tearDown(self):
        self.nabuWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.nabuWidget.close()
        del self.nabuWidget
        TestCaseQt.tearDown(self)

    def testGetInitialConfiguration(self):
        """Test that the get configuration is working"""
        ini_conf = {
            "method": "Paganin",
            "delta_beta": "100.0",
            "padding_type": "edge",
            "unsharp_coeff": 0,
            "unsharp_sigma": 0,
        }
        self.assertEqual(self.nabuWidget.getConfiguration(), ini_conf)

    def testSetConfiguration(self):
        """Test that the set configuration is working"""
        conf = {
            "method": "Paganin",
            "delta_beta": "200.0",
            "padding_type": "zeros",
            "unsharp_coeff": 3.6,
            "unsharp_sigma": 2.1,
        }
        self.nabuWidget.setConfiguration(conf)
        self.nabuWidget.show()
        # check visibility of some widgets
        unsharp_widget = self.nabuWidget._unsharpOpts
        self.assertEqual(unsharp_widget._unsharpCoeffQLE.text(), "3.6")
        self.assertTrue(unsharp_widget._unsharpCoeffCB.isChecked())

        self.assertEqual(unsharp_widget._unsharpSigmaQLE.text(), "2.1")
        self.assertTrue(unsharp_widget._unsharpSigmaCB.isChecked())
        paganin_widget = self.nabuWidget._paganinOpts
        self.assertEqual(paganin_widget._deltaBetaQLE.text(), "200.0")
        self.assertEqual(paganin_widget._paddingTypeCB.currentText(), "zeros")

        # check the generated configuration
        self.assertEqual(self.nabuWidget.getConfiguration(), conf)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestNabuReconstructionConfig(TestCaseQt):
    def setUp(self):
        TestCaseQt.setUp(self)
        self.nabuWidget = _NabuReconstructionConfig(parent=None, scrollArea=None)

    def tearDown(self):
        self.nabuWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.nabuWidget.close()
        del self.nabuWidget
        TestCaseQt.tearDown(self)

    def testGetInitialConfiguration(self):
        """Test that the get configuration is working"""
        ini_conf = {
            "method": "FBP",
            "angles_file": "",
            "axis_correction_file": "",
            "angle_offset": 0.0,
            "fbp_filter_type": "ramlak",
            "padding_type": "zeros",
            "start_x": 0,
            "end_x": -1,
            "start_y": 0,
            "end_y": -1,
            "start_z": 0,
            "end_z": -1,
            "iterations": 200,
            "optim_algorithm": "chambolle-pock",
            "weight_tv": 1.0e-2,
            "preconditioning_filter": 1,
            "rotation_axis_position": "",
            "positivity_constraint": 1,
            "translation_movements_file": "",
        }
        self.assertEqual(self.nabuWidget.getConfiguration(), ini_conf)

    def testSetConfiguration(self):
        """Test that the set configuration is working"""
        ini_conf = {
            "method": "FBP",
            "angles_file": "",
            "axis_correction_file": "",
            "angle_offset": 12.5,
            "fbp_filter_type": "none",
            "padding_type": "edges",
            "start_x": 0,
            "end_x": 23,
            "start_y": 12,
            "end_y": 56,
            "start_z": 560,
            "end_z": -1,
            "iterations": 20,
            "optim_algorithm": "chambolle-pock",
            "weight_tv": 1.5e-2,
            "preconditioning_filter": 0,
            "rotation_axis_position": "",
            "positivity_constraint": 0,
            "translation_movements_file": "my_file.csv",
        }
        self.nabuWidget.setConfiguration(ini_conf)
        qt.QApplication.processEvents()
        self.nabuWidget.show()

        # check visibility of some widgets
        self.assertEqual(self.nabuWidget._angleOffsetQDSB.value(), 12.5)
        subRegionWidget = self.nabuWidget._subRegionSelector
        self.assertFalse(subRegionWidget._xSubRegion._minCB.isChecked())
        self.assertFalse(subRegionWidget._xSubRegion._minQLE.isEnabled())
        self.assertTrue(subRegionWidget._xSubRegion._maxQLE.isEnabled())
        self.assertTrue(subRegionWidget._ySubRegion._minQLE.isEnabled())
        self.assertTrue(subRegionWidget._ySubRegion._maxQLE.isEnabled())
        self.assertTrue(subRegionWidget._zSubRegion._minQLE.isEnabled())
        self.assertFalse(subRegionWidget._zSubRegion._maxQLE.isEnabled())
        self.assertFalse(self.nabuWidget._preconditioningFilter.isChecked())

        # check the generated configuration
        self.assertEqual(self.nabuWidget.getConfiguration(), ini_conf)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestNabuOutputConfig(TestCaseQt):
    """Test the output configuration interface"""

    def setUp(self):
        TestCaseQt.setUp(self)
        self.nabuWidget = _NabuOutputConfig(parent=None)

    def tearDown(self):
        self.nabuWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.nabuWidget.close()
        self.nabuWidget = None
        self.qapp.processEvents()
        TestCaseQt.tearDown(self)

    def testGetConfiguration(self):
        ini_conf = {"file_format": "hdf5", "location": ""}
        self.assertEqual(self.nabuWidget.getConfiguration(), ini_conf)

    def testSetConfiguration(self):
        conf = {"file_format": "tiff", "location": os.sep.join(("tmp", "my_output"))}
        self.nabuWidget.setConfiguration(conf)
        self.nabuWidget.show()
        self.qapp.processEvents()
        # check some widget visibility
        self.assertTrue(self.nabuWidget._outputDirQLE.isVisible())
        self.assertFalse(self.nabuWidget._defaultOutput.isChecked())

        self.assertEqual(self.nabuWidget.getConfiguration(), conf)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestNabuVolumeWidget(TestCaseQt):
    def setUp(self):
        TestCaseQt.setUp(self)
        self.nabuWidget = NabuVolumeWidget(parent=None)

    def tearDown(self):
        self.nabuWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.nabuWidget.close()
        self.nabuWidget = None
        TestCaseQt.tearDown(self)

    def testGetConfiguration(self):
        ini_conf = {
            "start_z": 0,
            "end_z": -1,
            "gpu_mem_fraction": 0.9,
            "postproc": {"output_histogram": 0},
            "cpu_mem_fraction": 0.9,
            "use_phase_margin": True,
        }
        self.assertEqual(self.nabuWidget.getConfiguration(), ini_conf)

    def testSetConfiguration(self):
        conf = {
            "start_z": 10,
            "end_z": 24,
            "gpu_mem_fraction": 0.8,
            "postproc": {"output_histogram": 0},
            "cpu_mem_fraction": 0.1,
            "use_phase_margin": False,
        }
        self.nabuWidget.setConfiguration(conf)
        self.nabuWidget.show()
        self.qapp.processEvents()
        self.assertEqual(self.nabuWidget.getConfiguration(), conf)
