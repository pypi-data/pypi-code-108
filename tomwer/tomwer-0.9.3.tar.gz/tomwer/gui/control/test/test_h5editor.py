# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
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
__date__ = "14/02/2017"


import logging
import pytest
from silx.gui import qt
from silx.gui.utils.testutils import TestCaseQt
from tomwer.core.process.reconstruction.ftseries.params.beamgeo import BeamGeoType
from tomwer.core.process.reconstruction.darkref.params import Method as dkrf_method
from tomwer.core.process.reconstruction.ftseries.params.ft import VolSelMode
from tomwer.core.process.reconstruction.ftseries.params.paganin import PaganinMode
from tomwer.core.process.reconstruction.ftseries.params.pyhst import PyhstRP
from tomwer.gui.reconstruction.ftserie.reconsparamseditor import ReconsParamsEditor
from tomwer.synctools.ftseries import QReconsParams
from tomwer.test.utils import skip_gui_test
import gc

logging.disable(logging.INFO)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestSimplifyH5EditorDisplay(TestCaseQt):
    """Make sure we are displayig the correct things"""

    def setUp(self):
        super(TestSimplifyH5EditorDisplay, self).setUp()
        self.h5Editor = ReconsParamsEditor(None)
        self.h5Editor.setAttribute(qt.Qt.WA_DeleteOnClose)

        self.input = QReconsParams()

    def tearDown(self):
        self.h5Editor.close()
        self.h5Editor = None
        gc.collect()
        self.qapp.processEvents()
        super(TestCaseQt, self).tearDown()

    def testPAGANIN(self):
        """As test are 'raw' and based on the values of the FastSetupDefineGlobals
        We are checking the values of FastSetupDefineGlobals by assert
        to make the difference with the 'True' unittest
        """
        widget = self.h5Editor._PaganinWidget
        self.h5Editor.loadReconsParams(self.input)

        # check Mode conbobox
        assert "MODE" in self.input["PAGANIN"].all_params
        assert self.input["PAGANIN"]["MODE"] == PaganinMode.off
        self.assertTrue(widget._qcbpaganin.currentIndex() == 0)
        self.assertTrue(widget._qcbpaganin.currentText() == "off")

        # test alpha/beta
        assert "DB2" in self.input["PAGANIN"].all_params
        assert self.input["PAGANIN"]["DB2"] == 100.0
        self.assertTrue(widget._qleSigmaBeta2.text() == str(100.0))

        # unsharp coefficient
        assert "UNSHARP_COEFF" in self.input["PAGANIN"].all_params
        assert self.input["PAGANIN"]["UNSHARP_COEFF"] == 3.0
        self.assertTrue(widget._unsharp_sigma_coeff.text() == str(3.0))

        # dilate coefficient
        assert "DILATE" in self.input["PAGANIN"].all_params
        assert self.input["PAGANIN"]["DILATE"] == 2
        self.assertTrue(widget._qleDilatation.text() == str(2))

        # high absorption
        assert "MKEEP_BONE" in self.input["PAGANIN"].all_params
        assert self.input["PAGANIN"]["MKEEP_BONE"] is False
        self.assertFalse(widget._qcbKeepBone.isChecked())

    def testPYHST(self):
        """test that the display of the PyHST widget is correct"""
        widget = self.h5Editor._PyHSTWidget
        self.h5Editor.loadReconsParams(self.input)

        # checkversion
        assert "EXE" in self.input["PYHSTEXE"].all_params
        self.assertTrue(widget._qcbPyHSTVersion.currentText() == PyhstRP.OFFV)

        # checkofficialversion
        assert "OFFV" in self.input["PYHSTEXE"].all_params
        assert self.input["PYHSTEXE"]["OFFV"] == PyhstRP.OFFV
        self.assertTrue(widget._qlOfficalVersion.text() == PyhstRP.OFFV)

        # #check verbose
        assert "VERBOSE" in self.input["PYHSTEXE"].all_params
        assert self.input["PYHSTEXE"]["VERBOSE"] == 0
        self.assertFalse(widget._qcbverbose.isChecked())

        # # check output file
        assert "VERBOSE_FILE" in self.input["PYHSTEXE"].all_params
        assert self.input["PYHSTEXE"]["VERBOSE_FILE"] == "pyhst_out.txt"
        self.assertTrue(widget._qleVerboseFile.text() == "pyhst_out.txt")

    def testBeamGEO(self):
        """test that the display of the BeamGeo widget is correct"""
        widget = self.h5Editor._beamGeoWidget
        self.h5Editor.loadReconsParams(self.input)

        # test reconstruction geometry
        assert "TYPE" in self.input["BEAMGEO"].all_params
        assert self.input["BEAMGEO"]["TYPE"] == BeamGeoType.parallel
        self.assertTrue(widget._qcbType.currentText() == "parallel")

        # test source X
        assert "SX" in self.input["BEAMGEO"].all_params
        assert self.input["BEAMGEO"]["SX"] == 0.0
        self.assertTrue(widget._qleSX.text() == str(0.0))

        # test source Y
        assert "SY" in self.input["BEAMGEO"].all_params
        assert self.input["BEAMGEO"]["SY"] == 0.0
        self.assertTrue(widget._qleSY.text() == str(0.0))

        # test source Distance
        assert "DIST" in self.input["BEAMGEO"].all_params
        assert self.input["BEAMGEO"]["DIST"] == 55.0
        self.assertTrue(widget._qleDIST.text() == str(55.0))

    def testFT(self):
        # parameters from the main widget
        widget = self.h5Editor._mainWidget
        self.h5Editor.loadReconsParams(self.input)

        assert "FIXEDSLICE" in self.input["FT"].all_params
        assert self.input["FT"]["FIXEDSLICE"].name == "middle"
        self.assertTrue(widget._qcbSelectSlice.currentText() == "middle")

        assert "VOLOUTFILE" in self.input["FT"].all_params
        assert self.input["FT"]["VOLOUTFILE"] == 0
        self.assertTrue(widget._qcbEDFStack.isChecked())
        self.assertFalse(widget._qcbSingleVolFile.isChecked())

        assert "CORRECT_SPIKES_THRESHOLD" in self.input["FT"].all_params
        assert self.input["FT"]["CORRECT_SPIKES_THRESHOLD"] == 0.04
        self.assertTrue(widget._qleThresholdSpikesRm.text() == str(0.04))

        assert "DO_TEST_SLICE" in self.input["FT"].all_params
        assert self.input["FT"]["DO_TEST_SLICE"] == 1
        self.assertTrue(widget._qcbDoTestSlice.isChecked())

        assert "VOLSELECT" in self.input["FT"].all_params
        assert self.input["FT"]["VOLSELECT"] == VolSelMode.total
        self.assertTrue(widget._qcbVolumeSelection.currentText() == "total")

        assert "VOLSELECTION_REMEMBER" in self.input["FT"].all_params
        assert self.input["FT"]["VOLSELECTION_REMEMBER"] == 0
        self.assertFalse(widget._qcbVolSelRemenber.isChecked())

        assert "RINGSCORRECTION" in self.input["FT"].all_params
        assert self.input["FT"]["RINGSCORRECTION"] == 0
        self.assertFalse(widget._qcbRingsCorrection.isChecked())

        # parameters from display widget
        widget = self.h5Editor._displayWidget
        self.h5Editor.loadReconsParams(self.input)

        assert "SHOWPROJ" in self.input["FT"].all_params
        assert self.input["FT"]["SHOWPROJ"] == 0
        self.assertFalse(widget._qcbShowProj.isChecked())

        assert "SHOWSLICE" in self.input["FT"].all_params
        assert self.input["FT"]["SHOWSLICE"] == 1
        self.assertTrue(widget._qcbShowSlice.isChecked())

        assert "ANGLE_OFFSET_VALUE" in self.input["FT"].all_params
        assert self.input["FT"]["ANGLE_OFFSET_VALUE"] == 0.0
        self.assertTrue(widget._qleAngleOffset.text() == str(0.0))

        # parameters fron expert widget
        widget = self.h5Editor._expertWidget
        self.h5Editor.loadReconsParams(self.input)

        assert "NUM_PART" in self.input["FT"].all_params
        assert self.input["FT"]["NUM_PART"] == 4
        self.assertTrue(widget._getNumericalPart() == 4)

        assert "VERSION" in self.input["FT"].all_params
        assert self.input["FT"]["VERSION"] == "fastomo3 3.2"
        self.assertTrue(widget._qleVersion.text() == "fastomo3 3.2")

        assert "DATABASE" in self.input["FT"].all_params
        assert self.input["FT"]["DATABASE"] == 0
        self.assertFalse(widget._qcbDataBase.isChecked())

        assert "NO_CHECK" in self.input["FT"].all_params
        assert self.input["FT"]["NO_CHECK"] == 0
        self.assertFalse(widget._qcbNocheck.isChecked())

        assert "ZEROOFFMASK" in self.input["FT"].all_params
        assert self.input["FT"]["ZEROOFFMASK"] == 1
        self.assertTrue(widget._qcbZeroRegionMask.isChecked())

        assert "FIXHD" in self.input["FT"].all_params
        assert self.input["FT"]["FIXHD"] == 0
        self.assertFalse(widget._qcbFixHD.isChecked())

    def testFTAxis(self):
        widget = self.h5Editor._axisWidget
        self.h5Editor.loadReconsParams(self.input)

        self.assertTrue("DO_AXIS_CORRECTION" in self.input["FTAXIS"].all_params)
        self.assertEqual(self.input["FTAXIS"]["DO_AXIS_CORRECTION"], True)
        widget._doAxisCorrection.setChecked(False)
        self.assertTrue(self.input["FTAXIS"]["DO_AXIS_CORRECTION"], False)

        self.assertTrue("USE_TOMWER_AXIS" in self.input["FTAXIS"].all_params)
        self.assertEqual(self.input["FTAXIS"]["USE_TOMWER_AXIS"], True)
        widget._useTomwerAxis.setChecked(False)
        self.assertTrue(self.input["FTAXIS"]["USE_TOMWER_AXIS"], False)

        self.assertTrue("TRY_USE_OLD_TOMWER_AXIS" in self.input["FTAXIS"].all_params)
        self.assertEqual(self.input["FTAXIS"]["TRY_USE_OLD_TOMWER_AXIS"], True)
        widget._useOldTomwerAxis.setChecked(False)
        self.assertTrue(self.input["FTAXIS"]["TRY_USE_OLD_TOMWER_AXIS"], False)

        self.assertTrue("HALF_ACQ" in self.input["FT"].all_params)
        self.assertEqual(self.input["FT"]["HALF_ACQ"], False)
        widget._qcbHalfAcq.isChecked()
        self.assertTrue(self.input["FTAXIS"]["TRY_USE_OLD_TOMWER_AXIS"], True)

    def testDKRF(self):
        widget = self.h5Editor._dkRefWidget
        self.h5Editor.loadReconsParams(self.input)

        assert "DARKCAL" in self.input["DKRF"].all_params
        assert self.input["DKRF"]["DARKCAL"] == dkrf_method.average
        self.assertTrue(widget._qcbDKMode.getMode() == dkrf_method.average)

        assert "REFSCAL" in self.input["DKRF"].all_params
        assert self.input["DKRF"]["REFSCAL"] == dkrf_method.median
        self.assertTrue(widget._qcbRefMode.getMode() == dkrf_method.median)

        assert "DKFILE" in self.input["DKRF"].all_params
        assert self.input["DKRF"]["DKFILE"] == "darkend[0-9]{3,4}"
        self.assertTrue(widget._qleDKPattern.text() == "darkend[0-9]{3,4}")

        assert "RFFILE" in self.input["DKRF"].all_params
        assert self.input["DKRF"]["RFFILE"] == "ref*.*[0-9]{3,4}_[0-9]{3,4}"
        self.assertTrue(widget._qleRefsPattern.text() == "ref*.*[0-9]{3,4}_[0-9]{3,4}")

        assert "REFSRMV" in self.input["DKRF"].all_params
        assert self.input["DKRF"]["REFSRMV"] == 0
        self.assertFalse(widget._qcbRmRef.isChecked())

        assert "REFSOVE" in self.input["DKRF"].all_params
        assert self.input["DKRF"]["REFSOVE"] == 0
        self.assertTrue(widget._qcbSkipRef.isChecked())


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestSimplifyH5EditorSave(TestCaseQt):
    """test that h5editor is returning the correct H5 structures"""

    def setUp(self):
        super(TestSimplifyH5EditorSave, self).setUp()
        self.h5Editor = ReconsParamsEditor(None)
        self.h5Editor.setAttribute(qt.Qt.WA_DeleteOnClose)

        self.input = QReconsParams()
        self.h5Editor.loadReconsParams(self.input)

    def tearDown(self):
        self.qapp.processEvents()
        self.h5Editor.close()
        self.h5Editor = None
        gc.collect()
        self.qapp.processEvents()
        super(TestSimplifyH5EditorSave, self).tearDown()

    def testSaving(self):
        # changing some values in BEAMGEO
        assert self.input.to_dict()["BEAMGEO"]["TYPE"] == "p"
        self.input["BEAMGEO"]["TYPE"] = "c"
        # changing some values in PAGANIN
        assert self.input["PAGANIN"]["MKEEP_BONE"] == 0
        self.input["PAGANIN"]["MKEEP_BONE"] = 1
        # changing some values in PYHSTEXE
        assert self.input["PYHSTEXE"]["VERBOSE_FILE"] == "pyhst_out.txt"
        self.input["PYHSTEXE"]["VERBOSE_FILE"] = "pyhst_out2.txt"
        assert self.input["PYHSTEXE"]["OFFV"] == PyhstRP.OFFV
        self.input["PYHSTEXE"]["OFFV"] = "randomString"
        # changing some FT value
        self.input["FT"]["CORRECT_SPIKES_THRESHOLD"] = "Inf"
        self.input["FT"]["RINGSCORRECTION"] = 1
        self.input["FT"]["ANGLE_OFFSET_VALUE"] = 25.0
        self.input["FT"]["FIXEDSLICE"] = "12"
        self.input["FT"]["SHOWSLICE"] = 0

        # changing Paganin values
        self.input["PAGANIN"]["MODE"] = 3

        # changing the DKRF values
        self.input["DKRF"]["REFSCAL"] = "Average"
        self.input["DKRF"]["DARKCAL"] = "None"
        self.input["DKRF"]["RFFILE"] = "toto.*"
        self.input["DKRF"]["REFSRMV"] = 0

        # loading from new values
        self.h5Editor.loadReconsParams(self.input)

        # changing again some values
        self.h5Editor._PaganinWidget._qcbpaganin.setCurrentIndex(1)
        self.h5Editor._PyHSTWidget._qcbverbose.setCheckState(qt.Qt.Unchecked)
        self.h5Editor._beamGeoWidget._qleSY.setText("12.0")
        # add some checking on the FT
        self.assertFalse(
            self.h5Editor._mainWidget._grpThreshold.isChecked()
        )  # this shouldn't be activated

        # saving the values
        savedStructures = self.h5Editor.getStructs()
        self.assertTrue("BEAMGEO" in savedStructures)
        self.assertTrue("PYHSTEXE" in savedStructures)
        self.assertTrue("PAGANIN" in savedStructures)
        self.assertTrue("FT" in savedStructures)
        self.assertTrue("FTAXIS" in savedStructures)
        self.assertTrue(savedStructures["BEAMGEO"]["TYPE"] == "c")
        self.assertTrue(savedStructures["BEAMGEO"]["SY"] == 12.0)

        self.assertTrue(savedStructures["PAGANIN"]["MKEEP_BONE"] == 1)
        self.assertTrue(savedStructures["PAGANIN"]["MODE"] == 1)

        self.assertTrue(savedStructures["PYHSTEXE"]["VERBOSE_FILE"] == "pyhst_out2.txt")
        self.assertTrue(savedStructures["PYHSTEXE"]["OFFV"] == "randomString")
        self.assertTrue(savedStructures["PYHSTEXE"]["VERBOSE"] == 0)

        self.assertTrue(savedStructures["FT"]["CORRECT_SPIKES_THRESHOLD"] == "Inf")
        self.assertTrue(savedStructures["FT"]["RINGSCORRECTION"] == 1)
        self.assertTrue(savedStructures["FT"]["ANGLE_OFFSET"] == 1)
        self.assertEqual(savedStructures["FT"]["FIXEDSLICE"], "12")
        self.assertTrue(savedStructures["FT"]["SHOWSLICE"] == 0)

        self.assertTrue(savedStructures["FTAXIS"]["DO_AXIS_CORRECTION"] == 1)
