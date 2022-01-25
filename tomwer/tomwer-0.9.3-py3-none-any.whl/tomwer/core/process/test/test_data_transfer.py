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


import unittest
import tempfile
import shutil
import time
import os
import h5py
import numpy

from tomoscan.io import HDF5File
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.process.control.scantransfer import ScanTransfer
from tomwer.test.utils import UtilsTest
from tomwer.synctools.rsyncmanager import RSyncManager
from tomwer.core.process.control.datalistener import DataListener
from nxtomomill.converter import h5_to_nx
import pytest
from tomoscan.validator import is_valid_for_reconstruction
from tomoscan.esrf.hdf5scan import ImageKey


class TestDataTransferIO(unittest.TestCase):
    """Test inputs and outputs types of the handler functions"""

    def setUp(self):
        super().setUp()
        self._used_folders = []
        self.origin_folder = None
        self.output_folder = None

    def tearDown(self):
        for folder in self._used_folders:
            shutil.rmtree(folder)
        super().tearDown()

    def testInputOutput(self):
        """Test that io using TomoBase instance work"""
        for input_type in (dict, TomwerScanBase):
            for return_dict in (True, False):
                with self.subTest(
                    return_dict=return_dict,
                    input_type=input_type,
                ):
                    output_folder = tempfile.mkdtemp()
                    origin_folder = tempfile.mkdtemp()
                    scan_folder = os.path.join(origin_folder, "scan_toto")
                    os.makedirs(scan_folder)
                    os.makedirs(os.path.join(output_folder, "scan_toto"))
                    self._used_folders.append(output_folder)
                    self._used_folders.append(origin_folder)

                    scan = MockEDF.mockScan(
                        scanID=scan_folder,
                        nRadio=10,
                        nRecons=1,
                        nPagRecons=4,
                        dim=10,
                    )

                    transfert_process = ScanTransfer(
                        inputs={
                            "data": scan,
                            "dest_dir": output_folder,
                            "return_dict": return_dict,
                        }
                    )

                    self.assertTrue(os.path.exists(output_folder))
                    input_obj = scan
                    if input_obj is dict:
                        input_obj = input_obj.to_dict()
                    transfert_process.run()
                    out = transfert_process.outputs.data
                    if return_dict:
                        self.assertTrue(isinstance(out, dict))
                    else:
                        self.assertTrue(isinstance(out, TomwerScanBase))


@pytest.mark.skipif(not RSyncManager().has_rsync(), reason="requires rsync")
class TestBlissDataTransfer(unittest.TestCase):
    """Make sure we can transfer data from bliss acquisition"""

    def setUp(self):
        self.input_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        shutil.copytree(
            UtilsTest.getBlissDataset(folderID="sample"),
            os.path.join(self.input_dir, "sample"),
        )

        self._proposal_file = os.path.join(
            self.input_dir, "sample", "ihpayno_sample.h5"
        )
        self._sample_file = os.path.join(
            self.input_dir, "sample", "sample_29042021", "sample_29042021.h5"
        )
        self._sample_file_entry = "1.1"
        assert os.path.exists(self._sample_file)

        # mock data listener: the processing of the Data transfer requires
        # knowledge of bliss files origin.
        self.assertTrue(os.path.exists(self._proposal_file))
        data_listener = DataListener()
        scans = data_listener.process_sample_file(
            sample_file=self._sample_file,
            entry=self._sample_file_entry,
            proposal_file=self._proposal_file,
            master_sample_file=None,
        )
        self.scan = scans[0]
        self.assertTrue(os.path.exists(self.scan.process_file))

    def tearDown(self):
        shutil.rmtree(self.input_dir)
        shutil.rmtree(self.output_dir)

    def testDataTransfer(self):
        """Make sure the data transfer is able to retrieve the scan,
        proposal file and scan file to transfer.
        Check that only the specific scan folders will be copy and removed
        and the other won't be affected.
        """
        out_nx = os.path.join(
            self.output_dir, "sample_29042021", "sample_29042021_1_1.nx"
        )
        self.assertFalse(os.path.exists(out_nx))
        out_proposal = os.path.join(self.output_dir, "ihpayno_sample.h5")
        self.assertFalse(os.path.exists(out_proposal))
        out_sample_file = os.path.join(
            self.output_dir, "sample_29042021", "sample_29042021.h5"
        )
        self.assertFalse(os.path.exists(out_sample_file))
        out_included_scans = [
            os.path.join(self.output_dir, "sample_29042021", "scan0002")
        ]
        for scan_path in out_included_scans:
            self.assertFalse(os.path.exists(scan_path))
        out_not_included_scans = [
            os.path.join(self.output_dir, "sample_29042021", "scan0004"),
            os.path.join(self.output_dir, "sample_29042021", "scan0006"),
            os.path.join(self.output_dir, "sample_29042021", "scan0008"),
        ]
        for scan_path in out_not_included_scans:
            self.assertFalse(os.path.exists(scan_path))

        process = ScanTransfer(
            inputs={
                "data": self.scan,
                "block": True,
                "dest_dir": self.output_dir,
            }
        )
        process.run()

        time.sleep(1)
        self.assertTrue(os.path.exists(out_nx), f"{out_nx} does not exists")
        # self.assertTrue(os.path.exists(out_proposal), f"{out_proposal} does not exists")
        self.assertTrue(
            os.path.exists(out_sample_file), f"{out_sample_file} does not exists"
        )
        for scan_path in out_included_scans:
            self.assertTrue(os.path.exists(scan_path))
        for scan_path in out_not_included_scans:
            self.assertFalse(os.path.exists(scan_path))

        # insure we can convert it using nxtomomill once converted
        output_file = out_sample_file.replace("29042021.h5", "29042021.nx")
        assert output_file != out_sample_file
        h5_to_nx(
            input_file_path=out_sample_file,
            output_file=output_file,
            single_file=True,
            file_extension=".nx",
        )
        assert os.path.exists(output_file)
        assert is_valid_for_reconstruction(HDF5TomoScan(output_file, entry="entry0000"))


@pytest.mark.skipif(not RSyncManager().has_rsync(), reason="requires rsync")
class NXTomoDataTransferBase(unittest.TestCase):
    """Make sure we can transfer data from an NXTomo with linked dependancies"""

    def setUp(self) -> None:
        super().setUp()
        self._src_dir = tempfile.mkdtemp()
        self._dst_dir = tempfile.mkdtemp()

    def create_nexus_file(self, relative_links=True):
        dims = 100, 200
        n_darks = 2
        n_flats = 3
        n_projections = 10
        scans = {
            "scan0002": (ImageKey.DARK_FIELD, n_darks),
            "scan0003": (ImageKey.FLAT_FIELD, n_flats),
            "scan0004": (ImageKey.PROJECTION, n_projections),
        }
        self.nexus_file_path = os.path.join(self._src_dir, "my_acquisition.nx")
        sources = []
        sources_len = []
        image_keys = []
        # create raw data
        for scan_name, (image_key, n_frames) in scans.items():
            dir_path = os.path.join(self._src_dir, scan_name)
            os.makedirs(dir_path)
            file_path = os.path.join(dir_path, "pcolinux_0000.h5")
            with HDF5File(file_path, mode="w") as h5s:
                pcolinux_grp = h5s.require_group("entry0000/instrument/pcolinux")
                shape = (n_frames, dims[1], dims[0])
                data = numpy.random.random(shape)
                data *= 100
                pcolinux_grp["data"] = data.astype(dtype=numpy.uint16)
                # create a link tp measurement
                h5s["entry0000/measurement/data"] = h5py.SoftLink(
                    "/".join(("/entry0000", "instrument", "pcolinux", "data"))
                )
            vsource_path = os.path.join(scan_name, "pcolinux_0000.h5")
            if not relative_links:
                vsource_path = os.path.normpath(
                    os.path.join(self._src_dir, vsource_path)
                )
            sources.append(
                h5py.VirtualSource(
                    vsource_path,
                    name="entry0000/instrument/pcolinux/data",
                    shape=shape,
                )
            )
            sources_len.append(n_frames)
            image_keys.extend([image_key.value] * n_frames)
        # create virtual dataset to the raw data
        with HDF5File(self.nexus_file_path, mode="w") as h5s:
            entry_node = h5s.require_group("entry0000")

            # write detector
            detector_node = entry_node.require_group("detector")
            shape = (
                n_darks + n_flats + n_projections,
                dims[1],
                dims[0],
            )
            layout = h5py.VirtualLayout(shape=shape, dtype=numpy.uint16)
            i_frame = 0
            for v_source, v_source_length in zip(sources, sources_len):
                layout[i_frame : i_frame + v_source_length] = v_source
                i_frame += v_source_length
            n_frames = i_frame
            detector_node.create_virtual_dataset("data", layout, fillvalue=numpy.nan)
            detector_node["count_time"] = numpy.array([0.1] * n_frames)
            detector_node["distance"] = 0.17
            detector_node["distance"].attrs["unit"] = "m"
            # write general information
            entry_node["definition"] = "NXtomo"
            entry_node["end_time"] = "2021-03-03T15:51:00.986554+01:00"
            entry_node["start_time"] = "2021-03-03T15:43:00.693382+01:00"
            entry_node["title"] = "0001"
            entry_node["field_of_view"] = "Half"
            entry_node["tomo_n"] = n_frames
            entry_node["x_pixel_size"] = 3.25e-7
            entry_node["y_pixel_size"] = 3.25e-7

            # write beam: add an absolute link for energy to insure this is style valid and that relative files won't be moved
            file_with_energy = os.path.join(self._src_dir, "energy.h5")
            with HDF5File(file_with_energy, mode="w") as energy_file:
                energy_file["energy"] = 19
                energy_file["energy"].attrs["unit"] = "keV"

            entry_node["instrument/beam/incident_energy"] = h5py.ExternalLink(
                file_with_energy, "/energy"
            )

            entry_node["beam"] = h5py.SoftLink(
                "/".join(("/entry0000", "instrument", "beam"))
            )
            # write sample
            sample_node = entry_node.require_group("sample")
            sample_node["name"] = "sample name"
            sample_node["image_key"] = numpy.array(image_keys)
            sample_node["image_key_control"] = numpy.array(image_keys)
            sample_node["rotation_angle"] = numpy.linspace(0, 360, n_frames)
            sample_node["x_translation"] = numpy.array([0.13] * n_frames)
            sample_node["y_translation"] = numpy.array([0.0063] * n_frames)
            sample_node["z_translation"] = numpy.array([0.6] * n_frames)

    def tearDown(self) -> None:
        shutil.rmtree(self._src_dir)
        shutil.rmtree(self._dst_dir)
        return super().tearDown()

    def test(self):
        src_scan = HDF5TomoScan(self.nexus_file_path, entry="entry0000")
        assert is_valid_for_reconstruction(src_scan)
        process = ScanTransfer(
            inputs={
                "data": src_scan,
                "turn_off_print": True,
                "dest_dir": self._dst_dir,
                "block": True,
                "noRsync": False,
            }
        )
        process.run()
        dst_scan = process.outputs.data
        assert dst_scan.master_file != self.nexus_file_path
        assert is_valid_for_reconstruction(dst_scan, check_values=True)
        with HDF5File(src_scan.master_file, mode="r") as h5s_src:
            src_dataset = h5s_src["entry0000/detector/data"][...]
        with HDF5File(dst_scan.master_file, mode="r") as h5s_dst:
            dst_dataset = h5s_dst["entry0000/detector/data"][...]
        assert numpy.array_equal(src_dataset, dst_dataset)


@pytest.mark.skipif(not RSyncManager().has_rsync(), reason="requires rsync")
class TestNXtomoTransferRelativeLink(NXTomoDataTransferBase):
    """Insure NXtomo conversion will work if it contains relative links"""

    def setUp(self) -> None:
        super().setUp()
        self.create_nexus_file(relative_links=True)

    def test(self):
        super().test()
        # make sure there is the .nx file there and the folder containing file linked the relative
        assert (
            len(
                os.listdir(os.path.join(self._dst_dir, self._src_dir.split(os.sep)[-1]))
            )
            == 4
        )


@pytest.mark.skipif(not RSyncManager().has_rsync(), reason="requires rsync")
class TestNXtomoTransferAbsoluteLink(NXTomoDataTransferBase):
    """Insure NXtomo conversion will work if it contains absolute links"""

    def setUp(self) -> None:
        super().setUp()
        self.create_nexus_file(relative_links=False)

    def test(self):
        super().test()
        # make sure there is only the .nx file there
        assert (
            len(
                os.listdir(os.path.join(self._dst_dir, self._src_dir.split(os.sep)[-1]))
            )
            == 1
        )
