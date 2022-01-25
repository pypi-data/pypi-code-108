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
__date__ = "21/03/2019"


import unittest
import tempfile
import platform
from tomwer.core.process.reconstruction.ftseries.params.paganin import (
    PaganinRP,
    PaganinMode,
)
from tomwer.core.process.reconstruction.darkref.params import (
    DKRFRP,
    Method as Dkrf_Method,
)
from tomwer.core.process.reconstruction.ftseries.params.ft import FTRP
from tomwer.core.process.reconstruction.ftseries.params import ReconsParams
from tomwer.core.utils import ftseriesutils
import os
import pytest


class TestReconsParamSet(unittest.TestCase):
    """
    test the generation of unique reconstruction parameters list
    """

    def testReconsParamListPaganin(self):
        """Test that several values of paganin db, db2 are bringing several
        reconstructions parameters set"""
        paganin_param = PaganinRP()
        paganin_param.db = [5.0, 6.0]
        paganin_param.db2 = [1.0, 1.0, 2.0]
        recons_list = paganin_param.to_unique_recons_set(as_to_dict=False)
        self.assertEqual(len(recons_list), 4)

    def testReconsParamListDKRF(self):
        dkrf = DKRFRP()
        for as_to_dict, th_value in zip((True, False), ("Median", Dkrf_Method.median)):
            with self.subTest(as_to_dict=as_to_dict):
                _unique = dkrf.to_unique_recons_set(as_to_dict=as_to_dict)
                self.assertEqual(len(_unique), 1)
                self.assertEqual(_unique[0]["REFSCAL"], th_value)

    def testPagReconsParamList(self):
        """Same test as testReconsParamListPaganin but from an instance of
        ReconsParams"""
        paganin_param = PaganinRP()
        paganin_param.db = [5.0, 6.0]
        paganin_param.db2 = [1.0, 1.0, 2.0]

        for empty in (True, False):
            with self.subTest(empty=empty):
                rp = ReconsParams(empty=empty)
                rp.paganin = paganin_param
                recons_list = rp.to_unique_recons_set(as_to_dict=True)
                self.assertEqual(len(recons_list), 4)
                for param_set in recons_list:
                    self.assertTrue(isinstance(param_set, dict))

    @pytest.mark.skipif(
        platform.system() == "Windows", reason="No rights on conda installation"
    )
    def testReconsParamList(self):
        """Same test as testReconsParamListPaganin but from an instance of
        ReconsParams"""
        paganin_param = PaganinRP()
        paganin_param.db = [5.0, 6.0]
        paganin_param.db2 = [1.0, 1.0, 2.0]

        fp_param = FTRP()
        fp_param.correct_spikes_threshold = (True, False)

        recons_params = ReconsParams()
        recons_params.ft = fp_param
        recons_params.paganin = paganin_param

        recons_list = recons_params.to_unique_recons_set(as_to_dict=True)
        self.assertEqual(len(recons_list), 8)
        for param_set in recons_list:
            self.assertTrue(isinstance(param_set, dict))
            tmp_file = tempfile.NamedTemporaryFile(suffix=".h5")
            with tmp_file as tmpH5File:
                # test writing h5 file
                ftseriesutils.saveH5File(
                    h5File=tmpH5File.name, structs=param_set, displayInfo=False
                )
            if os.path.exists(tmp_file.name):
                os.remove(tmp_file.name)

    def testSingleValuesReconsParams(self):
        """Make sure that a default instance of ReconsParams with only
        single values generate a single set of reconstruction parameters"""
        recons_params = ReconsParams()
        rp_list = recons_params.to_unique_recons_set(as_to_dict=True)
        self.assertEqual(len(rp_list), 1)
        self.assertTrue(isinstance(rp_list[0], dict))

    def testParamsSetWithSlicesAndPaganin(self):
        """Test that the `_UNSPLIT_KEYS` is correctly taking into account"""
        ft_param = FTRP()
        ft_param.fixed_slice = (12, 16)

        self.assertEqual(len(ft_param.to_unique_recons_set()), 1)


class TestReconsParamCopy(unittest.TestCase):
    """Test copy of the reconstruction parameters"""

    def setUp(self):
        self._rp_empty = ReconsParams(empty=True)
        self._rp_full = ReconsParams(empty=False)
        assert self._rp_full.paganin.mode is PaganinMode.off
        self._pag_rp = PaganinRP()
        self._pag_rp.mode = PaganinMode.on
        self._dkrf_rp = DKRFRP()
        assert self._rp_full.dkrf.dark_calc_method is Dkrf_Method.average
        self._dkrf_rp.dark_calc_method = Dkrf_Method.none

    def testCopy(self):
        """make sure copy function is valid"""
        for rp in (self._rp_empty, self._rp_full):
            rp.copy(self._pag_rp)
            rp.copy(self._dkrf_rp)
            if rp is self._rp_empty:
                self.assertTrue(rp.paganin is not None)
                self.assertTrue(rp.beam_geo is None)
                self.assertTrue(rp.pyhst is None)
            self.assertTrue(rp.paganin is not self._pag_rp)
            self.assertTrue(rp.dkrf is not self._dkrf_rp)
            self.assertTrue(rp.paganin.mode is PaganinMode.on)
            self.assertTrue(rp.dkrf.dark_calc_method is Dkrf_Method.none)
            self.assertEqual(len(rp.to_unique_recons_set()), 1)

            self._pag_rp.copy(rp.paganin)
            self.assertEqual(len(rp.paganin.to_unique_recons_set()), 1)
            self._dkrf_rp.copy(rp.dkrf)
            self.assertEqual(len(rp.dkrf.to_unique_recons_set()), 1)

    def testReconsParamsUnmanagedParamsCopy(self):
        self._rp_full._add_unmanaged_param(param="TEST", value=12)
        self._rp_empty.copy(self._rp_full)
        self.assertTrue("TEST" in self._rp_empty.unmanaged_params)
        self.assertTrue("TEST" in self._rp_empty.all_params)
        self.assertEqual(self._rp_empty["TEST"], 12)

    def testFTRPUnmanagedParamsCopy(self):
        rp_1 = FTRP()
        rp_2 = FTRP()
        rp_2._add_unmanaged_param("TOTO", 12)
        rp_2._add_unmanaged_param("TATA", "dadsad")
        rp_2._add_unmanaged_param("KAWA", (23, 5))
        rp_1.copy(rp_2)
        self.assertTrue(rp_1.to_dict() == rp_2.to_dict())
