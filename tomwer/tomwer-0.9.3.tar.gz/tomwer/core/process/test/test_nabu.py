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
__date__ = "14/02/2020"


import os
import shutil
import tempfile
from glob import glob
import unittest
from tomwer.test.utils import UtilsTest
from tomwer.core.process.reconstruction.nabu import nabuslices as nabu
from tomwer.core.process.reconstruction.nabu import utils as nabuutils
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.process.reconstruction.nabu.nabuslices import NabuSliceMode
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.process.reconstruction.axis import AxisRP
from tomwer.core.process.reconstruction.nabu import settings as nabu_settings


class TestNabuDescUtils(unittest.TestCase):
    """Test the util function for creating the description of nabu"""

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.top_dir = tempfile.mkdtemp()
        self.dataset = "scan_3_"
        data_test_dir = UtilsTest.getEDFDataset(self.dataset)
        scan_folder = os.path.join(self.top_dir, self.dataset)
        shutil.copytree(data_test_dir, scan_folder)
        self.scan = ScanFactory.create_scan_object(scan_folder)

    def tearDown(self) -> None:
        shutil.rmtree(self.scan.path)

    def testResourcesDescriptor(self):
        nabuutils.get_nabu_resources_desc(scan=self.scan, method="local")
        nabuutils.get_nabu_resources_desc(scan=self.scan, method="slurm")

    def testDatasetDescriptor(self):
        self.scan.get_nabu_dataset_info()


class TestNabuIni(unittest.TestCase):
    """Test creation of nabu .cfg files according to tomwer configuration"""

    def setUp(self) -> None:
        self.dataset = "scan_3_"
        self._root_dir = tempfile.mkdtemp()
        data_test_dir = UtilsTest.getEDFDataset(self.dataset)
        scan_folder = os.path.join(self._root_dir, self.dataset)
        shutil.copytree(data_test_dir, scan_folder)
        self.scan = EDFTomoScan(scan_folder)
        self._nabu_cfg_folder = os.path.join(
            self.scan.path, nabu_settings.NABU_CFG_FILE_FOLDER
        )
        [os.remove(cfg_file) for cfg_file in glob(self.scan.path + os.sep + "*.cfg")]
        if os.path.exists(self._nabu_cfg_folder):
            shutil.rmtree(self._nabu_cfg_folder)

        assert len(self.getNabuIniFiles()) == 0
        # a random configuration
        self.config = get_nabu_default_config(output_dir=self.scan.path)

    def tearDown(self) -> None:
        shutil.rmtree(self._root_dir)

    def testNoSlices(self):
        """If no slices selected, in this case we will only create a .cfg
        for the volume
        """
        self.config["tomwer_slices"] = None
        self.config["phase"]["method"] = ""
        self.assertEqual(
            len(
                nabu.interpret_tomwer_configuration(config=self.config, scan=self.scan)
            ),
            1,
        )
        nabu.run_slices_reconstruction(scan=self.scan, config=self.config, dry_run=True)
        nabu_files = self.getNabuIniFiles()
        self.assertEqual(len(nabu_files), 1)
        # check volume and slice .cfg files for nabu reconstruction are here
        ini_file = os.path.basename(self.scan.path) + ".cfg"
        ini_file = os.path.join(self._nabu_cfg_folder, ini_file)
        self.assertTrue(ini_file in nabu_files)

    def testSingleSlice(self):
        """Test the behavior if we only request one slice without Paganin"""
        self.config["tomwer_slices"] = "1"
        self.config["phase"]["method"] = ""
        self.assertEqual(
            len(
                nabu.interpret_tomwer_configuration(config=self.config, scan=self.scan)
            ),
            2,
        )
        nabu.run_slices_reconstruction(scan=self.scan, config=self.config, dry_run=True)
        nabu_files = self.getNabuIniFiles()
        self.assertEqual(len(nabu_files), 2)
        # check volume and slice .cfg files for nabu reconstruction are here
        for file_name in (
            os.path.basename(self.scan.path) + ".cfg",
            os.path.basename(self.scan.path) + "slice_0001" + ".cfg",
        ):
            with self.subTest(file_name=file_name):
                self.assertTrue(
                    os.path.join(self._nabu_cfg_folder, file_name) in nabu_files
                )

    def testSinglePagSlice(self):
        """Test the behavior if we only request one Paganin slice"""
        self.config["phase"]["method"] = "Paganin"
        self.config["tomwer_slices"] = "1"
        self.config["phase"]["delta_beta"] = "100.0"
        self.assertEqual(
            len(
                nabu.interpret_tomwer_configuration(config=self.config, scan=self.scan)
            ),
            2,
        )
        nabu.run_slices_reconstruction(scan=self.scan, config=self.config, dry_run=True)
        nabu_files = self.getNabuIniFiles()
        self.assertEqual(len(nabu_files), 2)
        # check volume and slice .cfg files for nabu reconstruction are here
        for file_name in (
            os.path.basename(self.scan.path) + "pag_db0100.cfg",
            os.path.basename(self.scan.path) + "slice_pag_0001_db0100" + ".cfg",
        ):
            with self.subTest(file_name=file_name):
                self.assertTrue(
                    os.path.join(self._nabu_cfg_folder, file_name) in nabu_files
                )

    def testSeveralSlices(self):
        """Test the behavior if we request several slices without Paganin"""
        slices = (1, 4, 12)
        self.config["tomwer_slices"] = str(slices)
        self.config["phase"]["method"] = ""
        self.assertEqual(
            len(
                nabu.interpret_tomwer_configuration(config=self.config, scan=self.scan)
            ),
            len(slices) + 1,
        )
        nabu.run_slices_reconstruction(scan=self.scan, config=self.config, dry_run=True)
        nabu_files = self.getNabuIniFiles()
        self.assertEqual(len(nabu_files), len(slices) + 1)
        # check volume and slice .ini files for nabu reconstruction are here
        ini_files = [os.path.basename(self.scan.path) + ".cfg"]
        for slice_index in slices:
            ini_files.append(
                os.path.basename(self.scan.path)
                + "slice_"
                + str(slice_index).zfill(4)
                + ".cfg"
            )

        for ini_file in ini_files:
            with self.subTest(file_name=ini_file):
                self.assertTrue(
                    os.path.join(self._nabu_cfg_folder, ini_file) in nabu_files
                )

    def testSeveralPags(self):
        """behavior when several paganin slices are requested"""
        self.config["tomwer_slices"] = "1"
        self.config["phase"]["method"] = "Paganin"
        pag_dbs = [200.0, 300.0, 600.0, 700.0]
        self.config["phase"]["delta_beta"] = str(pag_dbs)
        sub_configs = nabu.interpret_tomwer_configuration(
            config=self.config, scan=self.scan
        )
        self.assertEqual(len(sub_configs), len(pag_dbs) * 2)
        # check that each dbs and slices values are in sub configurations
        existing_dbs = [config[0]["phase"]["delta_beta"] for config in sub_configs]
        existing_dbs = set(existing_dbs)
        for pag_db in pag_dbs:
            with self.subTest(pag_db=pag_db):
                self.assertTrue(str(pag_db) in existing_dbs)

        nabu.run_slices_reconstruction(scan=self.scan, config=self.config, dry_run=True)
        nabu_files = self.getNabuIniFiles()
        self.assertEqual(len(nabu_files), len(pag_dbs) * 2)

        # check volume and slice .conf files for nabu reconstruction are here
        ini_files = []
        for pag_db in pag_dbs:
            # add volume ini file
            ini_files.append(
                os.path.basename(self.scan.path)
                + "pag_db"
                + str(int(pag_db)).zfill(4)
                + ".cfg"
            )
            # add slice ini file
            ini_files.append(
                os.path.basename(self.scan.path)
                + "slice_pag_0001_db"
                + str(int(pag_db)).zfill(4)
                + ".cfg"
            )

        for ini_file in ini_files:
            with self.subTest(file_name=ini_file):
                self.assertTrue(
                    os.path.join(self._nabu_cfg_folder, ini_file) in nabu_files
                )

    def testSeveralPagsSeveralSlices(self):
        """behavior when several paganin slices are requested with several
        delta / beta values"""
        slices = (1, 4, 12)
        self.config["tomwer_slices"] = str(slices)
        self.config["phase"]["method"] = "Paganin"
        pag_dbs = [200, 300, 600, 700]
        self.config["phase"]["delta_beta"] = str(pag_dbs)
        self.assertEqual(
            len(
                nabu.interpret_tomwer_configuration(config=self.config, scan=self.scan)
            ),
            len(slices) * len(pag_dbs) + len(pag_dbs),
        )
        nabu.run_slices_reconstruction(scan=self.scan, config=self.config, dry_run=True)
        nabu_files = self.getNabuIniFiles()
        self.assertEqual(len(nabu_files), len(slices) * len(pag_dbs) + len(pag_dbs))
        # check volume and slice .cfg files for nabu reconstruction are here
        ini_files = []
        for slice_index in slices:
            for pag_db in pag_dbs:
                # add volume ini file
                ini_files.append(
                    os.path.basename(self.scan.path)
                    + "pag_db"
                    + str(pag_db).zfill(4)
                    + ".cfg"
                )
                # add slice ini file
                ini_files.append(
                    os.path.basename(self.scan.path)
                    + "slice_pag_"
                    + str(slice_index).zfill(4)
                    + "_db"
                    + str(pag_db).zfill(4)
                    + ".cfg"
                )

        for ini_file in ini_files:
            with self.subTest(file_name=ini_file):
                self.assertTrue(
                    os.path.join(self._nabu_cfg_folder, ini_file) in nabu_files
                )

    def getNabuIniFiles(self):
        return glob(self._nabu_cfg_folder + os.sep + "*.cfg")


class TestTomwerConfForNabu(unittest.TestCase):
    """
    Test the nabu configuration created from tomwer.
    Tomwer can request several slice or several paganin db values.
    We insure we can retrieve the correct nabu configuration for those

    note: the `_interpret_tomwer_configuration` function create each time a
          'None' slice which is the reconstruction of the entire volume
    """

    def setUp(self) -> None:
        self.scan = MockEDF.mockScan(scanID=tempfile.mkdtemp())
        # initial configuration
        self.conf = {"reconstruction": {}}

    def tearDown(self) -> None:
        shutil.rmtree(self.scan.path)

    def testSlices(self):
        # check if single value
        for slice in ("1", NabuSliceMode.MIDDLE):
            with self.subTest(slice=slice):
                self.conf["tomwer_slices"] = slice

                sub_confs = nabu.interpret_tomwer_configuration(
                    self.conf, scan=self.scan
                )
                # not 1 because return each time the 'None' slice which is
                # the reconstruction of the entire volume
                self.assertEqual(len(sub_confs), 1 + 1)

        # check single values or list of values
        for slice in ("[2, 3, 7]", "(6, 9,56)", "5;6; 9"):
            with self.subTest(slice=slice):
                self.conf["tomwer_slices"] = slice

                sub_confs = nabu.interpret_tomwer_configuration(
                    self.conf, scan=self.scan
                )
                self.assertEqual(len(sub_confs), 3 + 1)
        # check from:to:step
        self.conf["tomwer_slices"] = "2:10:2"
        sub_confs = nabu.interpret_tomwer_configuration(self.conf, scan=self.scan)
        self.assertEqual(len(sub_confs), 5 + 1)

    def testPaganinDB(self):
        """Test that tomwer generate one configuration per paganin db"""
        self.conf["phase"] = {}
        # check if single value
        self.conf["phase"]["delta_beta"] = "100"
        sub_confs = nabu.interpret_tomwer_configuration(self.conf, scan=self.scan)
        # not 1 because return each time the 'None' slice which is
        # the reconstruction of the entire volume
        self.assertEqual(len(sub_confs), 1)

        # check single values or list of values
        for pag_db in ("[100, 200, ]", "(225, 230)", "5;6;"):
            with self.subTest(pag_db=pag_db):
                self.conf["phase"]["delta_beta"] = pag_db
                sub_confs = nabu.interpret_tomwer_configuration(
                    self.conf, scan=self.scan
                )
                self.assertEqual(len(sub_confs), 2)
        # check from:to:step
        self.conf["phase"]["delta_beta"] = "200:1000:100"
        sub_confs = nabu.interpret_tomwer_configuration(self.conf, scan=self.scan)
        self.assertEqual(len(sub_confs), 9)


class TestNabuAndAxis(unittest.TestCase):
    """Test that nabu process and axis process are compatible"""

    def setUp(self) -> None:
        self.dataset = "scan_3_"
        self._root_dir = tempfile.mkdtemp()
        data_test_dir = UtilsTest.getEDFDataset(self.dataset)
        scan_folder = os.path.join(self._root_dir, self.dataset)
        shutil.copytree(data_test_dir, scan_folder)
        self.scan = EDFTomoScan(scan_folder)
        [os.remove(cfg_file) for cfg_file in glob(self.scan.path + os.sep + "*.cfg")]

        # initial configuration
        self.conf = get_nabu_default_config(output_dir=self.scan.path)

        self.nabu_process = nabu.NabuSlices(inputs={"data": self.scan})
        self.nabu_process.set_dry_run(True)
        self.nabu_process.set_configuration(self.conf)
        self.scan._axis_params = AxisRP()
        self.nabu_cfg_folder = os.path.join(
            self.scan.path, nabu_settings.NABU_CFG_FILE_FOLDER
        )
        # make sure no .cfg files already exists
        assert len(glob(self.nabu_cfg_folder + os.sep + "*.cfg")) == 0

    def tearDown(self) -> None:
        shutil.rmtree(self._root_dir)

    def test_output_dir(self):
        self.conf["output"]["location"] = "{scan_basename}/output"
        self.nabu_process.set_configuration(self.conf)
        output_dir = self.scan.scan_basename() + os.sep + "output"
        self.assertFalse(os.path.exists(output_dir))
        self.nabu_process.run()
        self.assertTrue(os.path.exists(output_dir))
        nabu_conf_files = glob(
            output_dir + os.sep + nabu_settings.NABU_CFG_FILE_FOLDER + os.sep + "*.cfg"
        )
        self.assertEqual(len(nabu_conf_files), 1)

    def get_saved_rotation_axis(self, nabu_out_file):
        """return the saved value for 'rotation axis' in the nabu
        configuration file"""
        with open(nabu_out_file, "r") as nabu_file:
            lines = nabu_file
            for line in lines:
                if line.startswith("rotation_axis_position"):
                    return line.replace("\n", "").replace(" ", "").split("=")[-1]
            return None

    def testNoCOR(self):
        """test if axis is executed and no COR are set, nabu won't mind"""
        self.scan._axis_params.set_relative_value(None)
        self.nabu_process.run()

        nabu_conf_files = glob(self.nabu_cfg_folder + os.sep + "*.cfg")
        self.assertEqual(len(nabu_conf_files), 1)
        nabu_rotation_axis_value = self.get_saved_rotation_axis(nabu_conf_files[0])
        self.assertEqual(nabu_rotation_axis_value, "")

    def testCOR(self):
        """test that if cor is computed, cor will be registered for nabu"""
        self.scan._axis_params.set_relative_value(2.3)
        self.nabu_process.run()

        nabu_conf_files = glob(self.nabu_cfg_folder + os.sep + "*.cfg")
        self.assertEqual(len(nabu_conf_files), 1)
        nabu_rotation_axis_value = self.get_saved_rotation_axis(nabu_conf_files[0])
        self.assertEqual(
            nabu_rotation_axis_value,
            str(self.scan._axis_params.value_ref_tomwer + self.scan.dim_1 / 2.0),
        )


def get_nabu_default_config(output_dir):
    """:return a default configuration for nabu"""
    return {
        "phase": {
            "padding_type": "edge",
            "method": "",
            "delta_beta": "100.0",
            "margin": 50,
            "unsharp_sigma": 0,
            "unsharp_coeff": 0,
        },
        "preproc": {
            "ccd_filter_threshold": 0.04,
            "take_logarithm": True,
            "log_min_clip": 1e-06,
            "ccd_filter_enabled": 0,
            "log_max_clip": 10.0,
            "flatfield_enabled": 1,
        },
        "dataset": {
            "project_name": "hair_A1_50nm_tomo3_1_",
            "location": "/tmp_14_days/payno/hair_A1_50nm_tomo3_1_",
            "flat_file_prefix": "refHST",
            "projections_subsampling": 1,
            "binning": 1,
            "dark_file_prefix": "dark.edf",
            "binning_z": 1,
        },
        "reconstruction": {
            "positivity_constraint": 1,
            "start_z": 0,
            "end_y": -1,
            "optim_algorithm": "chambolle-pock",
            "enable_halftomo": 0,
            "end_z": -1,
            "iterations": 200,
            "start_x": 0,
            "fbp_filter_type": "ramlak",
            "angle_offset": 0.0,
            "end_x": -1,
            "method": "FBP",
            "angles_file": "",
            "rotation_axis_position": "",
            "start_y": 0,
            "preconditioning_filter": 1,
            "padding_type": "zeros",
            "weight_tv": 0.01,
            "translation_movements_file": "",
            "axis_correction_file": "",
        },
        "output": {"file_format": "hdf5", "location": output_dir},
    }
