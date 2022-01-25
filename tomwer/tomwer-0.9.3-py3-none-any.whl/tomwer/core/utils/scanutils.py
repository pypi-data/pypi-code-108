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
"""
Utils to mock scans
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "30/09/2019"

import shutil

import h5py
import numpy
import time
import os
from xml.etree import cElementTree
import fabio
import fabio.edfimage
from tomoscan.esrf.hdf5scan import ImageKey
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomoscan.io import HDF5File
from tomwer.core.scan.blissscan import BlissScan
from silx.io.utils import h5py_read_dataset
import tempfile
from contextlib import AbstractContextManager


class _ScanMock:
    """Base class to mock as scan (radios, darks, refs, reconstructions...)"""

    PIXEL_SIZE = 0.457

    def __init__(
        self,
        scan_path,
        n_radio,
        n_ini_radio=None,
        n_extra_radio=0,
        scan_range=360,
        n_recons=0,
        n_pag_recons=0,
        recons_vol=False,
        dim=200,
        ref_n=0,
        dark_n=0,
        scene="noise",
    ):
        """

        :param scan_path:
        :param n_radio:
        :param n_ini_radio:
        :param n_extra_radio:
        :param scan_range:
        :param n_recons:
        :param n_pag_recons:
        :param recons_vol:
        :param dim:
        :param ref_n:
        :param dark_n:
        :param str scene: scene type.
                          * 'noise': generate radios from numpy.random
                          * `increase value`: first frame value will be0, then second 1...
                          * `arange`: arange through frames
                          * 'perfect-sphere: generate a sphere which just fit in the
                          detector dimensions
        TODO: add some differente scene type.
        """
        self.det_width = dim
        self.det_height = dim
        self.scan_path = scan_path
        self.n_radio = n_radio
        self.scene = scene

        if not os.path.exists(scan_path):
            os.makedirs(scan_path)

        self.write_metadata(
            n_radio=n_radio, scan_range=scan_range, ref_n=ref_n, dark_n=dark_n
        )

    def add_radio(self, index=None):
        raise NotImplementedError("Base class")

    def add_reconstruction(self, index=None):
        raise NotImplementedError("Base class")

    def add_pag_reconstruction(self, index=None):
        raise NotImplementedError("Base class")

    def add_recons_vol(self):
        raise NotImplementedError("Base class")

    def write_metadata(self, n_radio, scan_range, ref_n, dark_n):
        raise NotImplementedError("Base class")

    def end_acquisition(self):
        raise NotImplementedError("Base class")

    def _get_radio_data(self, index):
        if self.scene == "noise":
            return numpy.random.random((self.det_height * self.det_width)).reshape(
                (self.det_width, self.det_height)
            )
        elif self.scene == "increasing value":
            return numpy.zeros((self.det_width, self.det_height)) + index
        elif self.scene == "arange":
            start = index * (self.det_height * self.det_width)
            stop = (index + 1) * (self.det_height * self.det_width)
            return numpy.arange(start=start, stop=stop).reshape(
                self.det_width, self.det_height
            )
        elif self.scene == "perfect-sphere":
            background = numpy.zeros((self.det_height * self.det_width))
            radius = min(background.shape)

            def _compute_radius_to_center(data):
                assert data.ndim == 2
                xcenter = (data.shape[2]) // 2
                ycenter = (data.shape[1]) // 2
                y, x = numpy.ogrid[: data.shape[0], : data.shape[1]]
                r = numpy.sqrt((x - xcenter) ** 2 + (y - ycenter) ** 2)
                return r

            radii = _compute_radius_to_center(background)
            scale = 1
            background[radii < radius * scale] = 1.0
            return background
        else:
            raise ValueError("selected scene %s is no managed" % self.scene)


class MockHDF5(_ScanMock):
    """
    Mock an acquisition in a hdf5 file.

    note: for now the Mock class only manage one initial ref and one final
    """

    _PROJ_COUNT = 1

    def __init__(
        self,
        scan_path,
        n_proj,
        n_ini_proj=None,
        n_alignement_proj=0,
        scan_range=360,
        n_recons=0,
        n_pag_recons=0,
        recons_vol=False,
        dim=200,
        create_ini_dark=True,
        create_ini_ref=True,
        create_final_ref=False,
        n_refs=10,
        field_of_view="Full",
        estimated_cor_frm_motor=None,
    ):
        """

        :param scan_path: directory of the file containing the hdf5 acquisition
        :param n_proj: number of projections (does not contain alignement proj)
        :param n_ini_proj: number of projection do add in the constructor
        :param n_alignement_proj: number of alignment projection
        :param int scan_range:
        :param n_recons:
        :param n_pag_recons:
        :param recons_vol:
        :param dim: frame dim - only manage square fame for now
        :param create_ini_dark: create one initial dark frame on construction
        :param create_ini_ref: create the initial serie of ref (n_ref) on
                               construction (after creation of the dark)
        :param create_final_ref: create the final serie of ref (n_ref) on
                               construction (after creation of the dark)
        :param n_refs: number of refs per serie
        :param str field_of_view: type of acquisition, can be `Half` or `Full`
        :param Union[None, float]: estimated value of the center of rotation
                                   for the half acquisition if any
        """
        self.rotation_angle = numpy.linspace(start=0, stop=scan_range, num=n_proj + 1)
        self.rotation_angle_return = numpy.linspace(
            start=scan_range, stop=0, num=n_alignement_proj
        )
        self.scan_master_file = os.path.join(
            scan_path, os.path.basename((scan_path)) + ".h5"
        )
        self._n_refs = n_refs
        self.scan_entry = "entry"

        super(MockHDF5, self).__init__(
            scan_path=scan_path,
            n_radio=n_proj,
            n_ini_radio=n_ini_proj,
            n_extra_radio=n_alignement_proj,
            scan_range=scan_range,
            n_recons=n_recons,
            n_pag_recons=n_pag_recons,
            recons_vol=recons_vol,
            dim=dim,
        )
        if create_ini_dark:
            self.add_initial_dark()
        if create_ini_ref:
            self.add_initial_ref()
        if n_ini_proj is not None:
            for i_radio in range(n_ini_proj):
                self.add_radio(index=i_radio)
        if create_final_ref:
            self.add_final_ref()
        self._define_fov(field_of_view, estimated_cor_frm_motor)
        self.scan = HDF5TomoScan(scan=self.scan_master_file, entry="entry")

    def add_initial_dark(self):
        dark = numpy.random.random((self.det_height * self.det_width)).reshape(
            (1, self.det_width, self.det_height)
        )
        self._append_frame(
            data_=dark,
            rotation_angle=self.rotation_angle[-1],
            image_key=ImageKey.DARK_FIELD.value,
            image_key_control=ImageKey.DARK_FIELD.value,
        )

    def add_initial_ref(self):
        for i in range(self._n_refs):
            flat = numpy.random.random((self.det_height * self.det_width)).reshape(
                (1, self.det_width, self.det_height)
            )
            self._append_frame(
                data_=flat,
                rotation_angle=self.rotation_angle[0],
                image_key=ImageKey.FLAT_FIELD.value,
                image_key_control=ImageKey.FLAT_FIELD.value,
            )

    def add_final_ref(self):
        for i in range(self._n_refs):
            flat = numpy.random.random((self.det_height * self.det_width)).reshape(
                (1, self.det_width, self.det_height)
            )
            self._append_frame(
                data_=flat,
                rotation_angle=self.rotation_angle[-1],
                image_key=ImageKey.FLAT_FIELD.value,
                image_key_control=ImageKey.FLAT_FIELD.value,
            )

    def add_radio(self, index=None):
        radio = self._get_radio_data(index=index)
        radio = radio.reshape((1, self.det_height, self.det_width))
        self._append_frame(
            data_=radio,
            rotation_angle=self.rotation_angle[index],
            image_key=ImageKey.PROJECTION.value,
            image_key_control=ImageKey.PROJECTION.value,
        )

    def add_alignment_radio(self, index, angle):
        radio = self._get_radio_data(index=index)
        radio = radio.reshape((1, self.det_height, self.det_width))
        self._append_frame(
            data_=radio,
            rotation_angle=angle,
            image_key=ImageKey.PROJECTION.value,
            image_key_control=ImageKey.ALIGNMENT.value,
        )

    def _append_frame(self, data_, rotation_angle, image_key, image_key_control):

        with HDF5File(self.scan_master_file, "a") as h5_file:
            entry_one = h5_file.require_group(self.scan_entry)
            instrument_grp = entry_one.require_group("instrument")
            detector_grp = instrument_grp.require_group("detector")
            sample_grp = entry_one.require_group("sample")

            # add data
            if "data" in detector_grp:
                # read and remove data
                current_dataset = h5py_read_dataset(detector_grp["data"])
                new_dataset = numpy.append(current_dataset, data_)
                del detector_grp["data"]
                shape = list(current_dataset.shape)
                shape[0] += 1
                new_dataset = new_dataset.reshape(shape)
            else:
                new_dataset = data_

            # add rotation angle
            if "rotation_angle" in sample_grp:
                new_rot_angle = h5py_read_dataset(sample_grp["rotation_angle"])
                new_rot_angle = numpy.append(new_rot_angle, rotation_angle)
                del sample_grp["rotation_angle"]
            else:
                new_rot_angle = [rotation_angle]

            # add image_key
            if "image_key" in detector_grp:
                new_image_key = h5py_read_dataset(detector_grp["image_key"])
                new_image_key = numpy.append(new_image_key, image_key)
                del detector_grp["image_key"]
            else:
                new_image_key = [image_key]

            # add image_key_control
            if "image_key_control" in detector_grp:
                new_image_key_control = h5py_read_dataset(
                    detector_grp["image_key_control"]
                )
                new_image_key_control = numpy.append(
                    new_image_key_control, image_key_control
                )
                del detector_grp["image_key_control"]
            else:
                new_image_key_control = [image_key_control]

            # add count_time
            if "count_time" in detector_grp:
                new_count_time = h5py_read_dataset(detector_grp["count_time"])
                new_count_time = numpy.append(new_count_time, self._PROJ_COUNT)
                del detector_grp["count_time"]
            else:
                new_count_time = [self._PROJ_COUNT]

        with h5py.File(self.scan_master_file, "a") as h5_file:
            entry_one = h5_file.require_group(self.scan_entry)
            instrument_grp = entry_one.require_group("instrument")
            if "NX_class" not in instrument_grp.attrs:
                instrument_grp.attrs["NX_class"] = "NXinstrument"
            detector_grp = instrument_grp.require_group("detector")
            if "NX_class" not in detector_grp.attrs:
                detector_grp.attrs["NX_class"] = "NXdetector"
            sample_grp = entry_one.require_group("sample")
            if "NX_class" not in sample_grp.attrs:
                sample_grp.attrs["NX_class"] = "NXsample"
            # write camera information
            detector_grp["data"] = new_dataset
            detector_grp["image_key"] = new_image_key
            detector_grp["image_key_control"] = new_image_key_control
            detector_grp["count_time"] = new_count_time
            # write sample information
            sample_grp["rotation_angle"] = new_rot_angle

    def write_metadata(self, n_radio, scan_range, ref_n, dark_n):
        with h5py.File(self.scan_master_file, "a") as h5_file:
            entry_one = h5_file.require_group(self.scan_entry)
            instrument_grp = entry_one.require_group("instrument")
            detector_grp = instrument_grp.require_group("detector")

            entry_one.attrs["NX_class"] = u"NXentry"
            entry_one.attrs["definition"] = u"NXtomo"
            if "x_pixel_size" not in detector_grp:
                detector_grp["x_pixel_size"] = _ScanMock.PIXEL_SIZE
            if "y_pixel_size" not in detector_grp:
                detector_grp["y_pixel_size"] = _ScanMock.PIXEL_SIZE

    def end_acquisition(self):
        # no specific operation to do
        pass

    def _define_fov(self, acquisition_fov, estimated_cor_from_motor):
        with h5py.File(self.scan_master_file, "a") as h5_file:
            entry_one = h5_file.require_group(self.scan_entry)
            instrument_grp = entry_one.require_group("instrument")
            detector_grp = instrument_grp.require_group("detector")
            if "field_of_view" not in detector_grp:
                detector_grp["field_of_view"] = acquisition_fov
            if estimated_cor_from_motor is not None:
                detector_grp["estimated_cor_from_motor"] = estimated_cor_from_motor


class MockEDF(_ScanMock):
    """Mock a EDF acquisition"""

    _RECONS_PATTERN = "_slice_"

    _PAG_RECONS_PATTERN = "_slice_pag_"

    def __init__(
        self,
        scan_path,
        n_radio,
        n_ini_radio=None,
        n_extra_radio=0,
        scan_range=360,
        n_recons=0,
        n_pag_recons=0,
        recons_vol=False,
        dim=200,
        scene="noise",
    ):
        self._last_radio_index = -1
        super(MockEDF, self).__init__(
            scan_path=scan_path,
            n_radio=n_radio,
            n_ini_radio=n_ini_radio,
            n_extra_radio=n_extra_radio,
            scan_range=scan_range,
            n_recons=n_recons,
            n_pag_recons=n_pag_recons,
            recons_vol=recons_vol,
            dim=dim,
            scene=scene,
        )
        if n_ini_radio:
            for i_radio in range(n_ini_radio):
                self.add_radio(i_radio)
        for i_extra_radio in range(n_extra_radio):
            self.add_radio(i_extra_radio)
        for i_recons in range(n_recons):
            self.add_reconstruction(i_recons)
        for i_recons in range(n_pag_recons):
            self.add_pag_reconstruction(i_recons)
        if recons_vol is True:
            self.add_recons_vol()

    def get_info_file(self):
        return os.path.join(self.scan_path, os.path.basename(self.scan_path) + ".info")

    def end_acquisition(self):
        # create xml file
        xml_file = os.path.join(
            self.scan_path, os.path.basename(self.scan_path) + ".xml"
        )
        if not os.path.exists(xml_file):
            # write the final xml file
            root = cElementTree.Element("root")
            tree = cElementTree.ElementTree(root)
            tree.write(xml_file)

    def write_metadata(self, n_radio, scan_range, ref_n, dark_n):
        info_file = self.get_info_file()
        if not os.path.exists(info_file):
            # write the info file
            with open(self.get_info_file(), "w") as info_file:
                info_file.write("TOMO_N=    " + str(n_radio) + "\n")
                info_file.write("ScanRange= " + str(scan_range) + "\n")
                info_file.write("REF_N=     " + str(ref_n) + "\n")
                info_file.write("REF_ON=    " + str(n_radio) + "\n")
                info_file.write("DARK_N=    " + str(dark_n) + "\n")
                info_file.write("Dim_1=     " + str(self.det_width) + "\n")
                info_file.write("Dim_2=     " + str(self.det_height) + "\n")
                info_file.write("Col_beg=    0" + "\n")
                info_file.write("Col_end=   " + str(self.det_width) + "\n")
                info_file.write("Row_beg=    0" + "\n")
                info_file.write("Row_end=    " + str(self.det_height) + "\n")
                info_file.write("PixelSize=  " + str(_ScanMock.PIXEL_SIZE) + "\n")

    def add_radio(self, index=None):
        if index is not None:
            self._last_radio_index = index
            index_ = index
        else:
            self._last_radio_index += 1
            index_ = self._last_radio_index
        file_name = (
            os.path.basename(self.scan_path) + "_{0:04d}".format(index_) + ".edf"
        )
        f = os.path.join(self.scan_path, file_name)
        if not os.path.exists(f):
            data = self._get_radio_data(index=index_)
            assert data is not None
            assert data.shape == (self.det_width, self.det_height)
            edf_writer = fabio.edfimage.EdfImage(data=data, header={"tata": "toto"})
            edf_writer.write(f)

    @staticmethod
    def mockReconstruction(folder, nRecons=5, nPagRecons=0, volFile=False, dim=200):
        """
        create reconstruction files into the given folder

        :param str folder: the path of the folder where to save the reconstruction
        :param nRecons: the number of reconstruction to mock
        :param nPagRecons: the number of paganin reconstruction to mock
        :param volFile: true if we want to add a volFile with reconstruction
        """
        assert type(nRecons) is int and nRecons >= 0
        basename = os.path.basename(folder)
        for i in range(nRecons):
            f = os.path.join(
                folder, basename + str(MockEDF._RECONS_PATTERN + str(i) + ".edf")
            )
            data = numpy.zeros((dim, dim))
            data[:: i + 2, :: i + 2] = 1.0
            edf_writer = fabio.edfimage.EdfImage(data=data, header={"tata": "toto"})
            edf_writer.write(f)

        for i in range(nPagRecons):
            f = os.path.join(
                folder, basename + str(MockEDF._PAG_RECONS_PATTERN + str(i) + ".edf")
            )
            data = numpy.zeros((dim, dim))
            data[:: i + 2, :: i + 2] = 1.0
            edf_writer = fabio.edfimage.EdfImage(data=data, header={"tata": "toto"})
            edf_writer.write(f)

        if volFile is True:
            volFile = os.path.join(folder, basename + ".vol")
            infoVolFile = os.path.join(folder, basename + ".vol.info")
            dataShape = (nRecons, dim, dim)
            data = numpy.random.random(nRecons * dim * dim).reshape(nRecons, dim, dim)
            data.astype(numpy.float32).tofile(volFile)
            MockEDF._createVolInfoFile(filePath=infoVolFile, shape=dataShape)

    @staticmethod
    def _createVolInfoFile(
        filePath,
        shape,
        voxelSize=1,
        valMin=0.0,
        valMax=1.0,
        s1=0.0,
        s2=1.0,
        S1=0.0,
        S2=1.0,
    ):
        assert len(shape) == 3
        f = open(filePath, "w")
        f.writelines(
            "\n".join(
                [
                    "! PyHST_SLAVE VOLUME INFO FILE",
                    "NUM_X =  %s" % shape[2],
                    "NUM_Y =  %s" % shape[1],
                    "NUM_Z =  %s" % shape[0],
                    "voxelSize =  %s" % voxelSize,
                    "BYTEORDER = LOWBYTEFIRST",
                    "ValMin =  %s" % valMin,
                    "ValMax =  %s" % valMax,
                    "s1 =  %s" % s1,
                    "s2 =  %s" % s2,
                    "S1 =  %s" % S1,
                    "S2 =  %s" % S2,
                ]
            )
        )
        f.close()

    @staticmethod
    def fastMockAcquisition(
        folder, n_radio=20, n_extra_radio=0, scan_range=360, dim=200
    ):
        """
        Simple function creating an acquisition into the given directory
        This won't complete data, scan.info of scan.xml files but just create the
        structure that data watcher is able to detect in edf mode.
        """
        assert type(n_radio) is int and n_radio > 0
        basename = os.path.basename(folder)
        if not os.path.exists(folder):
            os.makedirs(folder)

        # create info file
        info_file = os.path.join(folder, basename + ".info")
        if not os.path.exists(info_file):
            # write the info file
            with open(info_file, "w") as info_file:
                info_file.write("TOMO_N=                 " + str(n_radio) + "\n")
                info_file.write("ScanRange=                 " + str(scan_range) + "\n")

        # create scan files
        for i in range((n_radio + n_extra_radio)):
            file_name = basename + "_{0:04d}".format(i) + ".edf"
            f = os.path.join(folder, file_name)
            if not os.path.exists(f):
                data = numpy.random.random(dim * dim).reshape(dim, dim)
                edf_writer = fabio.edfimage.EdfImage(data=data, header={"tata": "toto"})
                edf_writer.write(f)

        # create xml file
        xml_file = os.path.join(folder, basename + ".xml")
        if not os.path.exists(xml_file):
            # write the final xml file
            root = cElementTree.Element("root")
            tree = cElementTree.ElementTree(root)
            tree.write(xml_file)

    @staticmethod
    def mockScan(
        scanID,
        nRadio=5,
        nRecons=1,
        nPagRecons=0,
        dim=10,
        scan_range=360,
        n_extra_radio=0,
        start_dark=False,
        end_dark=False,
        start_flat=False,
        end_flat=False,
        start_dark_data=None,
        end_dark_data=None,
        start_flat_data=None,
        end_flat_data=None,
    ):
        """
        Create some random radios and reconstruction in the folder

        :param str scanID: the folder where to save the radios and scans
        :param int nRadio: The number of radios to create
        :param int nRecons: the number of reconstruction to mock
        :param int nRecons: the number of paganin reconstruction to mock
        :param int dim: dimension of the files (nb row/columns)
        :param int scan_range: scan range, usually 180 or 360
        :param int n_extra_radio: number of radio run after the full range is made
                                  usually used to observe any sample movement
                                  during acquisition
        :param bool start_dark:
        :param bool end_dark:
        :param bool start_flat:
        :param bool end_flat:
        :param start_dark_data:
        :param end_dark_data:
        :param start_flat_data:
        :param end_flat_data:
        """
        assert type(scanID) is str
        assert type(nRadio) is int
        assert type(nRecons) is int
        assert type(dim) is int
        from tomwer.core.scan.scanfactory import ScanFactory  # avoid cyclic import

        MockEDF.fastMockAcquisition(
            folder=scanID,
            n_radio=nRadio,
            scan_range=scan_range,
            n_extra_radio=n_extra_radio,
            dim=dim,
        )
        MockEDF.mockReconstruction(
            folder=scanID, nRecons=nRecons, nPagRecons=nPagRecons, dim=dim
        )

        if start_dark:
            MockEDF.add_dark_serie(
                scan_path=scanID, n_elmt=4, index=0, dim=dim, data=start_dark_data
            )
        if start_flat:
            MockEDF.add_flat_serie(
                scan_path=scanID, n_elmt=4, index=0, dim=dim, data=start_flat_data
            )
        if end_dark:
            MockEDF.add_dark_serie(
                scan_path=scanID,
                n_elmt=4,
                index=nRadio - 1,
                dim=dim,
                data=end_dark_data,
            )
        if end_flat:
            MockEDF.add_flat_serie(
                scan_path=scanID,
                n_elmt=4,
                index=nRadio - 1,
                dim=dim,
                data=end_flat_data,
            )

        return ScanFactory.create_scan_object(scanID)

    @staticmethod
    def add_flat_serie(scan_path, n_elmt, index, dim, data):
        ref_file = os.path.join(scan_path, "ref0000_{}.edf".format(str(index).zfill(4)))
        if data is None:
            data = numpy.array(
                numpy.random.random(n_elmt * dim * dim) * 100, numpy.uint32
            )
        data.shape = (n_elmt, dim, dim)
        edf_writer = fabio.edfimage.EdfImage(data=data[0], header={"tata": "toto"})
        for frame in data[1:]:
            edf_writer.append_frame(data=frame)
        edf_writer.write(ref_file)

    @staticmethod
    def add_dark_serie(scan_path, n_elmt, index, dim, data):
        dark_file = os.path.join(scan_path, "darkend{}.edf".format(str(index).zfill(4)))
        if data is None:
            data = numpy.array(
                numpy.random.random(n_elmt * dim * dim) * 100, numpy.uint32
            )
        data.shape = (n_elmt, dim, dim)
        edf_writer = fabio.edfimage.EdfImage(data=data[0], header={"tata": "toto"})
        for frame in data[1:]:
            edf_writer.append_frame(data=frame)
        edf_writer.write(dark_file)


class _BlissSample:
    """
    Simple mock of a bliss sample. For now we wonyl create the hierarchy of
    files.
    """

    def __init__(
        self,
        sample_dir,
        sample_file,
        n_sequence,
        n_scan_per_sequence,
        n_darks,
        n_flats,
        with_nx,
        detector_name="pcolinux",
    ):
        self.__sample_dir = sample_dir
        self.__sample_file = sample_file
        self.__n_sequence = n_sequence
        self.__n_scan_per_seq = n_scan_per_sequence
        self.__n_darks = n_darks
        self.__n_flats = n_flats
        self.__scan_folders = []
        self._index = 1
        self.__with_nx = with_nx
        self.__detector_name = detector_name
        self.__det_width = 256
        self.__det_height = 256
        self.__n_frame_per_scan = 100
        self.__energy = 19.0
        for i_sequence in range(n_sequence):
            self.add_sequence()

    def get_next_free_index(self):
        idx = self._index
        self._index += 1
        return idx

    @staticmethod
    def get_title(scan_type):
        if scan_type == "dark":
            return "dark images"
        elif scan_type == "flat":
            return "reference images 1"
        elif scan_type == "projection":
            return "projections 1 - 2000"
        else:
            raise ValueError("Not implemented")

    def add_sequence(self):
        # reserve the index for the 'initialization' sequence. No scan folder
        # will be created for this one.
        seq_ini_index = self.get_next_free_index()

        # add sequence init information
        with h5py.File(self.sample_file, mode="a") as h5f:
            seq_node = h5f.require_group(str(seq_ini_index) + ".1")
            seq_node.attrs["NX_class"] = u"NXentry"
            seq_node["title"] = "tomo:fullturn"
            # write energy
            seq_node["technique/scan/energy"] = self.__energy

        def register_scan_in_parent_seq(parent_index, scan_index):
            with h5py.File(self.sample_file, mode="a") as h5f:
                # write scan numbers
                seq_node = h5f.require_group(str(parent_index) + ".1")
                if "measurement/scan_numbers" in seq_node:
                    scan_numbers = h5py_read_dataset(
                        seq_node["measurement/scan_numbers"]
                    )
                    res = list(scan_numbers)
                    del seq_node["measurement/scan_numbers"]
                else:
                    res = []
                res.append(scan_index)
                seq_node["measurement/scan_numbers"] = numpy.asarray(res)

        def add_scan(scan_type):
            scan_idx = self.get_next_free_index()
            scan_name = str(scan_idx).zfill(4)
            scan_path = os.path.join(self.path, scan_name)
            self.__scan_folders.append(
                _BlissScan(folder=scan_path, scan_type=scan_type)
            )
            register_scan_in_parent_seq(parent_index=seq_ini_index, scan_index=scan_idx)
            # register the scan information
            with h5py.File(self.sample_file, mode="a") as h5f:
                seq_node = h5f.require_group(str(scan_idx) + ".1")
                # write title
                title = self.get_title(scan_type=scan_type)
                seq_node["title"] = title
                # write data
                data = (
                    numpy.random.random(
                        self.__det_height * self.__det_width * self.__n_frame_per_scan
                    )
                    * 256
                )
                data = data.reshape(
                    self.__n_frame_per_scan, self.__det_height, self.__det_width
                )
                data = data.astype(numpy.uint16)
                det_path_1 = "/".join(("instrument", self.__detector_name))
                det_grp = seq_node.require_group(det_path_1)
                det_grp["data"] = data
                det_grp.attrs["NX_class"] = "NXdetector"
                acq_grp = det_grp.require_group("acq_parameters")
                acq_grp["acq_expo_time"] = 4
                det_path_2 = "/".join(("technique", "scan", self.__detector_name))
                seq_node[det_path_2] = data
                seq_node.attrs["NX_class"] = u"NXentry"
                # write rotation angle value and translations
                hrsrot_pos = seq_node.require_group(
                    "/".join(("instrument", "positioners"))
                )
                hrsrot_pos["hrsrot"] = numpy.random.randint(
                    low=0.0, high=360, size=self.__n_frame_per_scan
                )
                hrsrot_pos["sx"] = numpy.array(
                    numpy.random.random(size=self.__n_frame_per_scan)
                )
                hrsrot_pos["sy"] = numpy.random.random(size=self.__n_frame_per_scan)
                hrsrot_pos["sz"] = numpy.random.random(size=self.__n_frame_per_scan)

        if self.n_darks > 0:
            add_scan(scan_type="dark")

        if self.__n_flats > 0:
            add_scan(scan_type="flat")

        for i_proj_seq in range(self.__n_scan_per_seq):
            add_scan(scan_type="projection")

        # write end time
        with HDF5File(self.sample_file, mode="a") as h5f:
            h5f["/".join((str(seq_ini_index) + ".1", "end_time"))] = str(time.ctime())

        if self.__with_nx:
            nx_file = "sample_{}.nx".format(str(seq_ini_index).zfill(4))
            nx_file = os.path.join(self.path, nx_file)
            with h5py.File(nx_file, "a") as h5f:
                pass

    @property
    def path(self):
        return self.__sample_dir

    @property
    def sample_directory(self):
        return self.__sample_dir

    @property
    def sample_file(self):
        return self.__sample_file

    def scans_folders(self):
        return self.__scan_folders

    @property
    def n_darks(self):
        return self.__n_darks


class _BlissScan:
    """
    mock of a bliss scan
    """

    def __init__(self, folder, scan_type: str):
        assert scan_type in ("dark", "flat", "projection")
        self.__path = folder

    def path(self):
        return self.__path


class MockBlissAcquisition:
    """

    :param n_sequence: number of sequence to create
    :param n_scan_per_sequence: number of scans (projection serie) per sequence
    :param n_projections_per_scan: number of projection frame in a scan
    :param n_darks: number of dark frame in the serie. Only one serie at the
                    beginning
    :param int n_flats: number of flats to create. In this case will only
                        create one serie of n flats after dark if any
    :param str output_dir: will contain the proposal file and one folder per
                           sequence.
    """

    def __init__(
        self,
        n_sample,
        n_sequence,
        n_scan_per_sequence,
        n_darks,
        n_flats,
        output_dir,
        with_nx=False,
    ):
        self.__folder = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.__proposal_file = os.path.join(self.__folder, "ihproposal_file.h5")

        # create sample
        self.__samples = []
        for sample_i in range(n_sample):
            dir_name = "_".join(("sample", str(sample_i)))
            sample_dir = os.path.join(self.path, dir_name)
            os.makedirs(sample_dir)
            sample_file = os.path.join(sample_dir, dir_name + ".h5")
            self.__samples.append(
                _BlissSample(
                    sample_dir=sample_dir,
                    sample_file=sample_file,
                    n_sequence=n_sequence,
                    n_scan_per_sequence=n_scan_per_sequence,
                    n_darks=n_darks,
                    n_flats=n_flats,
                    with_nx=with_nx,
                )
            )

    @property
    def samples(self):
        return self.__samples

    @property
    def proposal_file(self):
        # for now a simple file
        return self.__proposal_file

    @property
    def path(self):
        return self.__folder

    def create_bliss_scan(self):
        master_file = self.samples[0].sample_file
        assert os.path.exists(master_file)
        return BlissScan(
            master_file=master_file, entry="/1.1", proposal_file=self.__proposal_file
        )


class _MockContext(AbstractContextManager):
    def __init__(self, output_folder):
        self._output_folder = output_folder
        if self._output_folder is None:
            tempfile.mkdtemp()
            self._output_folder_existed = False
        elif not os.path.exists(self._output_folder):
            os.makedirs(self._output_folder)
            self._output_folder_existed = False
        else:
            self._output_folder_existed = True
        super().__init__()

    def __init_subclass__(cls, **kwargs):
        mock_class = kwargs.get("mock_class", None)
        if mock_class is None:
            raise KeyError("mock_class should be provided to the " "metaclass")
        cls._mock_class = mock_class

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._output_folder_existed:
            shutil.rmtree(self._output_folder)


class HDF5MockContext(_MockContext, mock_class=MockHDF5):
    """
    Util class to provide a context with a new Mock HDF5 file
    """

    def __init__(self, scan_path, n_proj, **kwargs):
        super().__init__(output_folder=os.path.dirname(scan_path))
        self._n_proj = n_proj
        self._mocks_params = kwargs
        self._scan_path = scan_path

    def __enter__(self):
        return MockHDF5(
            scan_path=self._scan_path, n_proj=self._n_proj, **self._mocks_params
        ).scan
