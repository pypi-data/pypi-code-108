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
__date__ = "05/04/2019"


import os
import shutil
import tempfile
import unittest
import numpy
import time
from tomwer.core.utils.scanutils import MockEDF, MockHDF5
from tomwer.core.process.reconstruction.darkref.params import DKRFRP, Method as cMethod
from tomwer.core.scan.scanbase import TomwerScanBase
from ..reconstruction.darkref.darkrefs import DarkRefs
from ..reconstruction.darkref.darkrefscopy import DarkRefsCopy
from tomwer.test.utils import UtilsTest
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from silx.io.utils import get_data


class TestDarkRefIO(unittest.TestCase):
    """Test inputs and outputs types of the handler functions"""

    def setUp(self):
        self.scan_folder = tempfile.mkdtemp()

        self.scan_edf = MockEDF.mockScan(
            scanID=self.scan_folder, nRadio=10, nRecons=1, nPagRecons=4, dim=10
        )
        self.mock_hdf5 = MockHDF5(scan_path=self.scan_folder, n_proj=10, n_pag_recons=0)
        self.scan_hdf5 = self.mock_hdf5.scan

        self.recons_params = DKRFRP()

    def tearDown(self):
        shutil.rmtree(self.scan_folder)

    def testInputOutput(self):
        for scan, scan_type in zip(
            (self.scan_edf, self.scan_hdf5), ("edf scan", "hdf5 scan")
        ):
            for input_type in (dict, TomwerScanBase):
                for return_dict in (True, False):
                    with self.subTest(
                        return_dict=return_dict,
                        input_type=input_type,
                        scan_type=scan_type,
                    ):
                        input_obj = scan
                        if input_obj is dict:
                            input_obj = input_obj.to_dict()
                        process = DarkRefs(
                            inputs={
                                "dark_ref_params": self.recons_params,
                                "data": input_obj,
                                "return_dict": return_dict,
                            }
                        )
                        process.run()
                        out = process.outputs.data
                        if return_dict:
                            self.assertTrue(isinstance(out, dict))
                        else:
                            self.assertTrue(isinstance(out, TomwerScanBase))


class TestDarkRefCopyIO(unittest.TestCase):
    """Test inputs and outputs types of the handler functions"""

    def setUp(self):
        self.scan_folder = tempfile.mkdtemp()

        self.scan_edf = MockEDF.mockScan(
            scanID=self.scan_folder, nRadio=10, nRecons=1, nPagRecons=4, dim=10
        )
        self.scan_hdf5 = MockHDF5(
            scan_path=self.scan_folder, n_proj=10, n_pag_recons=0
        ).scan
        self.recons_params = DKRFRP()
        self._save_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.scan_folder)

    def testInputOutput(self):
        for scan, scan_type in zip(
            (self.scan_edf, self.scan_hdf5), ("edf scan", "hdf5 scan")
        ):
            for input_type in (dict, TomwerScanBase):
                for return_dict in (True, False):
                    with self.subTest(
                        return_dict=return_dict,
                        input_type=input_type,
                        scan_type=scan_type,
                    ):
                        input_obj = scan
                        if input_obj is dict:
                            input_obj = input_obj.to_dict()
                        dkrf_process = DarkRefsCopy(
                            inputs={
                                "dark_ref_params": self.recons_params,
                                "data": input_obj,
                                "return_dict": return_dict,
                                "save_dir": self._save_dir,
                            }
                        )
                        dkrf_process.run()
                        out = dkrf_process.outputs.data
                        if return_dict:
                            self.assertTrue(isinstance(out, dict))
                        else:
                            self.assertTrue(isinstance(out, TomwerScanBase))


class TestDarkRefEdf(unittest.TestCase):
    """
    Test dark ref is correctly processing with h5 refs
    """

    def setUp(self) -> None:
        self.scan_folder = tempfile.mkdtemp()
        self.dark_data = numpy.array(
            numpy.random.random(4 * 200 * 200) * 100, numpy.uint16
        ).reshape(4, 200, 200)
        self.flat_data = numpy.array(
            numpy.random.random(4 * 200 * 200) * 100, numpy.uint32
        ).reshape(4, 200, 200)
        self.scan = MockEDF.mockScan(
            scanID=self.scan_folder,
            nRadio=10,
            nRecons=1,
            nPagRecons=4,
            dim=200,
            start_dark=True,
            start_flat=True,
            start_dark_data=self.dark_data,
            start_flat_data=self.flat_data,
        )
        self.recons_params = DKRFRP()
        self.recons_params.overwrite_dark = True
        self.recons_params.overwrite_ref = True
        self.assertFalse(os.path.exists(self.scan.process_file))

    def tearDown(self) -> None:
        shutil.rmtree(self.scan_folder)

    def testDark(self):
        """
        Test darks are computed when only dark are requested
        """
        method_to_test = (
            cMethod.median,
            cMethod.average,
            cMethod.first,
            cMethod.last,
        )
        th_results = (
            numpy.median(self.dark_data, axis=0),
            numpy.mean(self.dark_data, axis=0),
            self.dark_data[0],
            self.dark_data[-1],
        )
        for method, th_res in zip(method_to_test, th_results):
            with self.subTest(method=method):
                if os.path.exists(self.scan.process_file):
                    os.remove(self.scan.process_file)
                process = DarkRefs(
                    inputs={
                        "dark_ref_params": self.recons_params,
                        "data": self.scan,
                    }
                )

                self.recons_params.dark_calc_method = method
                self.recons_params.ref_calc_method = cMethod.none
                process.run()
                self.assertTrue(os.path.exists(self.scan.process_file))
                darks = DarkRefs.get_darks_frm_process_file(
                    self.scan.process_file, entry="entry"
                )
                self.assertEqual(len(darks), 1)
                numpy.testing.assert_array_almost_equal(
                    self.scan.normed_darks[0], th_res.astype(numpy.uint16)
                )

    def testFlat(self):
        """
        Test flats are computed when only flat are requested
        """
        method_to_test = (
            cMethod.median,
            cMethod.average,
            cMethod.first,
            cMethod.last,
        )
        th_results = (
            numpy.median(self.flat_data, axis=0),
            numpy.mean(self.flat_data, axis=0),
            self.flat_data[0],
            self.flat_data[-1],
        )
        for method, th_res in zip(method_to_test, th_results):
            with self.subTest(method=method):
                if os.path.exists(self.scan.process_file):
                    os.remove(self.scan.process_file)
                self.recons_params.dark_calc_method = cMethod.none
                self.recons_params.ref_calc_method = method
                process = DarkRefs(
                    inputs={
                        "dark_ref_params": self.recons_params,
                        "data": self.scan,
                    }
                )
                process.run()
                self.assertTrue(os.path.exists(self.scan.process_file))
                flats = DarkRefs.get_flats_frm_process_file(
                    self.scan.process_file, entry="entry"
                )
                self.assertEqual(len(flats), 1)
                numpy.testing.assert_array_almost_equal(
                    self.scan.normed_flats[0], th_res.astype(numpy.uint16)
                )


class TestDarkRefNx(unittest.TestCase):
    """
    Test dark ref is correctly processing with h5 refs
    """

    def setUp(self) -> None:
        super().setUp()
        dataset_name = "frm_edftomomill_twoentries.nx"
        self.scan_folder = tempfile.mkdtemp()
        self._file_path = os.path.join(self.scan_folder, dataset_name)
        shutil.copyfile(
            src=UtilsTest.getH5Dataset(folderID=dataset_name), dst=self._file_path
        )
        self.scan = HDF5TomoScan(scan=self._file_path, entry="entry0000")
        self.assertFalse(os.path.exists(self.scan.process_file))
        self.recons_params = DKRFRP()
        self.recons_params.overwrite_dark = True
        self.recons_params.overwrite_ref = True

    def tearDown(self) -> None:
        shutil.rmtree(self.scan_folder)
        super().tearDown()

    def testDark(self):
        """
        Test darks are computed when only dark are requested
        """
        darks = self.scan.darks
        self.assertEqual(len(darks), 1)
        dark_data = get_data(list(darks.values())[0])

        method_to_test = (cMethod.average, cMethod.median, cMethod.last, cMethod.last)
        for method in method_to_test:
            with self.subTest(method=method):
                self.recons_params.dark_calc_method = method
                self.recons_params.ref_calc_method = cMethod.none
                process = DarkRefs(
                    inputs={
                        "dark_ref_params": self.recons_params,
                        "data": self.scan,
                    }
                )
                if os.path.exists(self.scan.process_file):
                    os.remove(self.scan.process_file)

                process.run()
                self.assertTrue(os.path.exists(self.scan.process_file))
                darks = DarkRefs.get_darks_frm_process_file(
                    self.scan.process_file, entry=self.scan.entry
                )
                self.assertEqual(len(darks), 1)
                self.assertTrue(numpy.allclose(darks[0], dark_data))
                flats = DarkRefs.get_flats_frm_process_file(
                    self.scan.process_file, entry=self.scan.entry
                )
                self.assertEqual(len(flats), 0)

    def testFlat(self):
        """
        Test flats are computed when only flat are requested
        """
        flats = self.scan.flats
        self.assertEqual(len(flats), 42)
        url_flat_serie_1 = [flats[index] for index in range(1, 22)]
        url_flat_serie_2 = [flats[index] for index in range(1521, 1542)]
        assert len(url_flat_serie_1) == 21
        assert len(url_flat_serie_2) == 21
        data_flat_serie_1 = [get_data(url) for url in url_flat_serie_1]
        data_flat_serie_2 = [get_data(url) for url in url_flat_serie_2]

        self.recons_params.overwrite_dark = True
        self.recons_params.overwrite_ref = True

        method_to_test = (cMethod.average, cMethod.median, cMethod.last, cMethod.last)
        for method in method_to_test:
            with self.subTest(method=method):
                if method is cMethod.median:
                    expected_res_s1 = numpy.median(data_flat_serie_1, axis=0)
                    expected_res_s2 = numpy.median(data_flat_serie_2, axis=0)
                elif method is cMethod.average:
                    expected_res_s1 = numpy.mean(data_flat_serie_1, axis=0)
                    expected_res_s2 = numpy.mean(data_flat_serie_2, axis=0)
                elif method is cMethod.first:
                    expected_res_s1 = data_flat_serie_1[0]
                    expected_res_s2 = data_flat_serie_2[0]
                elif method is cMethod.last:
                    expected_res_s1 = data_flat_serie_1[-1]
                    expected_res_s2 = data_flat_serie_2[-1]
                else:
                    raise ValueError("method not managed")

                self.recons_params.dark_calc_method = cMethod.none
                self.recons_params.ref_calc_method = method
                process = DarkRefs(
                    inputs={
                        "dark_ref_params": self.recons_params,
                        "data": self.scan,
                    }
                )
                process.run()
                self.assertTrue(os.path.exists(self.scan.process_file))
                darks = DarkRefs.get_darks_frm_process_file(
                    self.scan.process_file, entry=self.scan.entry
                )
                self.assertEqual(len(darks), 0)
                flats = DarkRefs.get_flats_frm_process_file(
                    self.scan.process_file, entry=self.scan.entry
                )
                self.assertEqual(len(flats), 2)
                self.assertTrue(1 in flats)
                self.assertTrue(1521 in flats)
                self.assertTrue(numpy.allclose(flats[1], expected_res_s1))
                self.assertTrue(numpy.allclose(flats[1521], expected_res_s2))

    def testDarkAndFlat(self):
        """
        Test darks and flats are computed when both are requested
        """
        flats = self.scan.flats
        self.assertEqual(len(flats), 42)
        url_flat_serie_1 = [flats[index] for index in range(1, 22)]
        url_flat_serie_2 = [flats[index] for index in range(1521, 1542)]
        assert len(url_flat_serie_1) == 21
        assert len(url_flat_serie_2) == 21
        data_flat_serie_1 = [get_data(url) for url in url_flat_serie_1]
        data_flat_serie_2 = [get_data(url) for url in url_flat_serie_2]

        self.recons_params.dark_calc_method = cMethod.average
        self.recons_params.ref_calc_method = cMethod.median
        darks = self.scan.darks
        self.assertEqual(len(darks), 1)
        dark_data = get_data(list(darks.values())[0])

        expected_flats_s1 = numpy.median(data_flat_serie_1, axis=0)
        expected_flats_s2 = numpy.median(data_flat_serie_2, axis=0)
        process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "data": self.scan,
            }
        )
        process.run()
        self.assertTrue(os.path.exists(self.scan.process_file))
        darks = DarkRefs.get_darks_frm_process_file(
            self.scan.process_file, entry=self.scan.entry
        )
        self.assertEqual(len(darks), 1)
        flats = DarkRefs.get_flats_frm_process_file(
            self.scan.process_file, entry=self.scan.entry
        )
        self.assertEqual(len(flats), 2)
        self.assertTrue(0 in darks)
        self.assertTrue(1 in flats)
        self.assertTrue(1521 in flats)
        self.assertTrue(numpy.allclose(flats[1], expected_flats_s1))
        self.assertTrue(numpy.allclose(flats[1521], expected_flats_s2))
        self.assertTrue(numpy.allclose(darks[0], dark_data))

    def testReprocessing(self):
        """
        Make sure computation is executed only when necessary
        """
        self.assertEqual(self.scan.normed_darks, None)
        self.assertEqual(self.scan.normed_flats, None)
        process = DarkRefs(
            inputs={
                "dark_ref_params": self.recons_params,
                "data": self.scan,
            }
        )
        process.run()
        self.assertEqual(len(self.scan.normed_darks), 1)
        self.assertEqual(len(self.scan.normed_flats), 2)

        # test behavior if overwrite is False
        self.recons_params.overwrite_dark = False
        self.recons_params.overwrite_ref = False
        self.scan.set_normed_darks(None)
        self.scan.set_normed_flats(None)
        timestamp_tomwer_processes = os.path.getmtime(self.scan.process_file)
        time.sleep(1)
        process.run()
        self.assertEqual(
            timestamp_tomwer_processes, os.path.getmtime(self.scan.process_file)
        )
        self.assertEqual(len(self.scan.normed_darks), 1)
        self.assertEqual(len(self.scan.normed_flats), 2)

        # test behavior if overwrite is True
        self.recons_params.overwrite_dark = True
        self.recons_params.overwrite_ref = True
        self.scan.set_normed_darks(None)
        self.scan.set_normed_flats(None)

        timestamp_tomwer_processes = os.path.getmtime(self.scan.process_file)
        time.sleep(1)
        process.run()
        self.assertNotEqual(
            timestamp_tomwer_processes, os.path.getmtime(self.scan.process_file)
        )
        self.assertEqual(len(self.scan.normed_darks), 1)
        self.assertEqual(len(self.scan.normed_flats), 2)


class TestDarkRefCopyNx(unittest.TestCase):
    """
    Test dark ref is correctly processing with h5 refs
    """

    def setUp(self) -> None:
        dataset_name = "frm_edftomomill_twoentries.nx"
        self.scan_folder = tempfile.mkdtemp()
        self._file_path = os.path.join(self.scan_folder, dataset_name)
        shutil.copyfile(
            src=UtilsTest.getH5Dataset(folderID=dataset_name), dst=self._file_path
        )
        self.scan_with_ref = HDF5TomoScan(scan=self._file_path, entry="entry0000")
        self.recons_params = DKRFRP()
        self.assertFalse(os.path.exists(self.scan_with_ref.process_file))

        mock = MockHDF5(
            scan_path=self.scan_folder,
            n_proj=10,
            n_ini_proj=2,
            n_pag_recons=0,
            create_ini_dark=False,
            create_ini_ref=False,
            dim=20,
        )
        self.scan_without_ref = mock.scan
        # make sure no ref and no dark registered
        assert len(self.scan_without_ref.darks) == 0
        assert len(self.scan_with_ref.darks) > 0
        assert len(self.scan_without_ref.flats) == 0
        assert len(self.scan_with_ref.flats) > 0
        assert self.scan_without_ref.normed_flats is None
        assert self.scan_with_ref.normed_flats is None
        assert self.scan_without_ref.normed_darks is None
        assert self.scan_with_ref.normed_darks is None
        self._save_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.scan_folder)

    def testCopyAuto(self):
        """Test copy in mode auto"""

        # step 1: check that ref will be registered
        copy_process = DarkRefsCopy(
            inputs={
                "dar_ref_params": self.recons_params,
                "data": self.scan_with_ref,
                "mode_auto": True,
                "save_dir": self._save_dir,
            }
        )
        self.assertTrue(copy_process.is_on_mode_auto)
        copy_process.run()
        self.assertTrue(copy_process.is_on_mode_auto)

        self.assertFalse(self.scan_with_ref.normed_flats is None)
        self.assertEqual(len(self.scan_with_ref.normed_flats), 2)
        self.assertFalse(self.scan_with_ref.normed_darks is None)
        self.assertEqual(len(self.scan_with_ref.normed_darks), 1)
        self.assertEqual(copy_process.has_dark_stored(), True)
        self.assertEqual(copy_process.has_flat_stored(), True)
        self.assertTrue(os.path.exists(copy_process._dark_save_file))
        self.assertTrue(os.path.exists(copy_process._ref_save_file))

        # step 2: check that registered ref will be copied
        copy_process = DarkRefsCopy(
            inputs={
                "dar_ref_params": self.recons_params,
                "data": self.scan_without_ref,
                "mode_auto": True,
                "save_dir": self._save_dir,
            }
        )
        self.assertTrue(os.path.exists(copy_process._dark_save_file))
        self.assertTrue(os.path.exists(copy_process._ref_save_file))
        copy_process.run()
        self.assertFalse(self.scan_without_ref.normed_flats is None)
        self.assertEqual(len(self.scan_without_ref.normed_flats), 2)
        self.assertFalse(self.scan_without_ref.normed_darks is None)
        self.assertEqual(len(self.scan_without_ref.normed_darks), 1)
        self.assertTrue(os.path.isfile(self.scan_with_ref.process_file))
        darks = DarkRefs.get_darks_frm_process_file(
            self.scan_without_ref.process_file, entry=self.scan_without_ref.entry
        )
        self.assertEqual(len(darks), 1)
        flats = DarkRefs.get_flats_frm_process_file(
            self.scan_without_ref.process_file, entry=self.scan_without_ref.entry
        )
        self.assertEqual(len(flats), 2)
