# coding: utf-8
# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
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
This module is used to define the process of the reference creator.
This is related to the issue #184
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "17/08/2021"


import os
from silx.io.utils import h5py_read_dataset
import fabio
import numpy
import typing
from silx.io.url import DataUrl
from tomwer.core import utils
from silx.io.dictdump import dicttoh5, h5todict
from tomoscan.io import HDF5File
import logging
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefs
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.edfscan import EDFTomoScan
from .settings import DARKHST_PREFIX, REFHST_PREFIX

logger = logging.getLogger(__name__)


class DarkRefsCopy(DarkRefs):
    """
    Reimplement Dark ref to deal with copy when there is no median/mean files
    """

    DEFAULT_SRCURRENT = 200.0  # mA

    def __init__(self, process_id=None, varinfo=None, inputs=None, label=None):
        super().__init__(
            process_id=process_id, varinfo=varinfo, inputs=inputs, label=label
        )
        if inputs is None:
            inputs = {}
        self._refHstPrefix = inputs.get("refhst_prefix", REFHST_PREFIX)
        self._darkHstPrefix = inputs.get("darkhst_prefix", DARKHST_PREFIX)
        self._mode_auto = inputs.get("mode_auto", True)
        if "savedir" in inputs:
            raise KeyError("savedir is not a valid key. Use save_dir")
        self._savedir = inputs.get("save_dir", None)
        if self._savedir is None:
            raise KeyError(
                "save_dir is expected (where the ref and dark file should be saved)"
            )
        self._dark_save_file = os.path.join(self._savedir, "dark.h5")
        self._ref_save_file = os.path.join(self._savedir, "refs.h5")
        info = "Ref copy will store files in " + self._savedir
        logger.info(info)
        """directory saved to store the dark and refHST reference files"""
        self._processOnlyCopy = inputs.get("process_only_copy", False)
        self._processOnlyDkRf = inputs.get("process_only_dkrf", False)
        init_ref_scan = inputs.get("init_dkrf_from", None)
        if init_ref_scan:
            if not isinstance(init_ref_scan, TomwerScanBase):
                raise TypeError(
                    "init_ref_scan is expected to be an instance of TomwerScanBase. Not {}".format(
                        type(init_ref_scan)
                    )
                )
            else:
                self.set_refs_from_scan(init_ref_scan)

    def set_process_only_dkRf(self, value: bool) -> None:
        self._processOnlyDkRf = value
        self._processOnlyCopy = False

    def set_process_only_copy(self, value: bool) -> None:
        self._processOnlyDkRf = False
        self._processOnlyCopy = value

    def set_refs_from_scan(self, scan: TomwerScanBase) -> bool:
        assert isinstance(scan, TomwerScanBase)
        if isinstance(scan, HDF5TomoScan):
            darks = DarkRefs.get_darks_frm_process_file(
                scan.process_file, entry=scan.entry, as_url=True
            )
            if len(darks) == 0:
                logger.warning("No dark found in %s")
            flats = DarkRefs.get_flats_frm_process_file(
                scan.process_file, entry=scan.entry, as_url=True
            )
            if len(flats) == 0:
                logger.warning("No flat found in %s")
            has_flat_or_dark = len(darks) > 0 or len(flats) > 0
            if not has_flat_or_dark:
                self._notice_user_no_ref_message(fileType="flat field", dir=scan)
                return False
            else:
                self.clean_save_files()
                if len(darks) == 0:
                    self._notice_user_no_ref_message(fileType="dark", dir=scan)
                else:
                    key_0 = sorted(darks.keys())[0]
                    self._copy_dark_from(dark_url=darks[key_0], scan=scan)

                if len(flats) == 0:
                    self._notice_user_no_ref_message(fileType="flat field", dir=scan)
                else:
                    key_0 = sorted(flats.keys())[0]
                    self._copy_ref_from(url=flats[key_0], scan=scan)
                self._ref_has_been_set(scan=scan)
                return True
        elif isinstance(scan, EDFTomoScan):
            if os.path.isdir(scan.path) is False:
                w = "given path (%s) is not a directory. Can't extract ref" % scan
                logger.warning(w)
                return False

            self.directory = scan
            if not self.contains_dark_or_ref(scan):
                self._notice_user_no_ref_message(fileType="flat field", dir=scan)
                return False
            else:
                self.clean_save_files()
                darkHSTFiles = sorted(
                    DarkRefs.getDarkHSTFiles(scan.path, prefix=self.darkHST_prefix)
                )
                refHSTFiles = sorted(
                    DarkRefs.getRefHSTFiles(scan.path, prefix=self.refHST_prefix)
                )
                if len(darkHSTFiles) == 0:
                    self._notice_user_no_ref_message(fileType="dark", dir=scan)
                else:
                    self._copy_dark_from(
                        dark_url=DataUrl(file_path=darkHSTFiles[0], scheme="fabio"),
                        scan=scan,
                    )

                if len(refHSTFiles) == 0:
                    self._notice_user_no_ref_message(fileType="flat field", dir=scan)
                else:
                    self._copy_ref_from(
                        url=DataUrl(file_path=refHSTFiles[0], scheme="fabio"), scan=scan
                    )

                """warning: dark should always be saved first because used for
                saving ref
                """
                self._ref_has_been_set(scan=scan)
                return True

    def _ref_has_been_set(self, scan):
        # TODO: this should be removed and set in the QObject inheritingtest_axis_darkrefs_ftseries from the DkrfCopy
        if hasattr(self, "sigRefSetted"):
            self.sigRefSetted.emit(scan)

    def _copy_to(self, scan):
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(
                "{} is expected to be a {} and not {}".format(
                    str(scan), TomwerScanBase, type(scan)
                )
            )

        if isinstance(scan, EDFTomoScan):
            if os.path.isdir(scan.path) is False:
                logger.warning(
                    str(scan) + " is not a directory. Cannot copy " "reference to it."
                )
                return
            if self.has_flat_or_dark_stored() is False:
                logger.error("No reference registred to be copy in %s" % scan)
                return

        # warning: get information if there is ref or dark before copying
        # because can bring interferences.
        _hasRef = self.contains_flat(scan)
        _hasDark = self.contains_dark(scan)
        # special treatment for dark and ref we want to store both at the same
        # time
        if isinstance(scan, HDF5TomoScan) and not _hasDark and not _hasRef:
            self._copy_dark_and_flat_to(scan)
        else:
            if self.has_dark_stored() and not _hasDark:
                self._copy_dark_to(scan)
            if self.has_flat_stored() and not _hasRef:
                self._copy_flat_to(scan)

    def _copy_dark_and_flat_to(
        self, scan: HDF5TomoScan, copy_dark: bool = True, copy_flats: bool = True
    ):
        """
        Function dedicated to the copy of dark and/or flat to HDF5TomoScan
        :param HDF5TomoScan scan:
        :param bool copy_dark:
        :param bool copy_flats:
        :return:
        """
        assert isinstance(scan, HDF5TomoScan), "function dedicated to HDF5TomoScan"
        if copy_dark is False and copy_flats is False:
            return

        results = {}
        shape_dark = None
        shape_flat = None
        if copy_dark:
            dark_info = self._get_dark_info()
            if dark_info is not None:
                results["darks"] = {"0": dark_info["data"]}
                shape_dark = dark_info["data"].shape
                scan.set_normed_darks(results["darks"])
        if copy_flats:
            flat_info = self._get_flat_info()
            if flat_info is not None:
                flats = {"0": flat_info["data_start"]}
                shape_flat = flat_info["data_start"].shape
                index_last_projection = max(scan.projections) or None
                if index_last_projection is not None and index_last_projection != 0:
                    flats[str(index_last_projection)] = flat_info["data_end"]
                results["flats"] = flats
                scan.set_normed_flats(results["flats"])

        # check dimensions of dark and flat compare to projections if any
        if scan.dim_1 is not None and scan.dim_2 is not None:
            shape_frame = (scan.dim_2, scan.dim_1)
            incoherent_with_dark = False
            incoherent_with_flat = False
            if shape_dark is not None:
                incoherent_with_dark = shape_dark != shape_frame
            if shape_flat is not None:
                incoherent_with_flat = shape_flat != shape_frame

            if incoherent_with_dark:
                logger.warning(
                    "Scan frame (%s) and dark (%s) to copy have"
                    "different shapes. Unable to do the copy"
                    "" % (shape_frame, shape_dark)
                )
            if incoherent_with_flat:
                logger.warning(
                    "Scan frame (%s) and flat (%s) to copy have"
                    "different shapes. Unable to do the copy"
                    "" % (shape_frame, shape_flat)
                )
            if incoherent_with_flat or incoherent_with_dark:
                return

        try:
            with scan.acquire_process_file_lock():
                DarkRefs._register_process(
                    process_file=scan.process_file,
                    entry=scan.entry,
                    process=DarkRefs,
                    configuration=self.recons_params.to_dict(),
                    results=results,
                    process_index=scan.pop_process_index(),
                    overwrite=True,
                )
        except Exception as e:
            logger.warning(f"Fail to register darkrefcopy process. Reason is {e}")

    def _copy_dark_to(self, scan):
        """The dark is copied without normalization"""
        assert isinstance(scan, TomwerScanBase)
        if not self.has_dark_stored():
            raise ValueError("require to copy dark but no dark stored")
        dark_info = self._get_dark_info()
        assert dark_info is not None, (
            "when this function is call you should insure"
            "that process has stored some dark"
        )
        if isinstance(scan, EDFTomoScan):
            # do never copy on an existing file (meaning ref already here)
            dark_file_name = dark_info["dark_basename"] or DARKHST_PREFIX
            dst = os.path.join(scan.path, os.path.basename(dark_file_name))
            if os.path.isfile(dst) is True:
                logger.info("%s exists, will not copy dark" % dst)
            else:
                header = dark_info["header"]
                data = dark_info["data"]
                file_desc = fabio.edfimage.EdfImage(data=data, header=header)
                file_desc.write(dst, force_type=numpy.int32)

        elif isinstance(scan, HDF5TomoScan):
            self._copy_dark_and_flat_to(scan=scan, copy_dark=True, copy_flats=False)
        else:
            raise ValueError("Tomo scan type not managed (%s)" % scan)

    def _copy_flat_to(self, scan):
        assert isinstance(scan, TomwerScanBase)
        if not self.has_flat_stored():
            raise ValueError("require to copy flat but no flat stored")
        if isinstance(scan, EDFTomoScan):

            def normalize(data, when):
                """normalize from dark_end and getting the SRCurrent at start or
                end"""
                assert when in ("start", "end")

                srCurrent = utils.getSRCurrent(scan_dir=scan.path, when=when)
                if srCurrent is None:
                    logger.warning(
                        "Can't find information about srCurrent," "set to default value"
                    )
                    srCurrent = self.DEFAULT_SRCURRENT
                dark_info = self._get_dark_info()
                if dark_info is None:
                    logger.info("no dark found, unable to normalize")
                    return None, srCurrent
                dark_data = dark_info["data"]
                if data.shape != dark_data.shape:
                    logger.warning(
                        "Image and dark have different shapes."
                        "Cannot normalize. (Dark ref file in %s)"
                        "" % self._dark_save_file
                    )
                    return data, srCurrent
                return (data * srCurrent).astype(numpy.float32) + dark_data, srCurrent

            flat_info = self._get_flat_info()
            if flat_info is None:
                raise RuntimeError("No ref found during processing")
            tomo_N = utils.getTomo_N(scan.path)
            if tomo_N in (None, -1):
                logger.error(
                    "Can't find the number of projection. " "Fail to create reference"
                )

            header = flat_info["header"]
            end_acqui = str(utils.getTomo_N(scan.path)).zfill(4)
            indexRefFile = {"start": "0000", "end": end_acqui}
            for when in ("start", "end"):
                data = flat_info["_".join(("data", when))]
                fileName = self.recons_params.ref_prefix + indexRefFile[when] + ".edf"
                filePath = os.path.join(scan.path, fileName)
                # do never copy on an existing file (meaning ref already here)
                if os.path.isfile(filePath):
                    continue
                _data, _srCurrent = normalize(data, when)

                _header = header.copy()
                # add some extra information on the header
                _header["SRCUR"] = _srCurrent
                file_desc = fabio.edfimage.EdfImage(data=_data, header=_header)
                file_desc.write(filePath, force_type=numpy.int32)
        elif isinstance(scan, HDF5TomoScan):
            self._copy_dark_and_flat_to(scan=scan, copy_dark=False, copy_flats=True)
        else:
            raise ValueError("Tomo scan type not managed (%s)" % scan)

    def _notice_user_no_ref_message(self, fileType, dir):
        logger.warning(self._get_no_ref_message(fileType, dir))

    def _get_no_ref_message(self, fileType, dir):
        mess = (
            "No %s found in the given directory %s. Won't be able to copy"
            " them" % (fileType, dir)
        )
        return mess

    def _copy_ref_from(self, scan, url):
        """
        Copy the data contained in _file in the given file to the `_savedir`
        and normalize the data from SRCurrent (intensity
        )"""

        def write(data_start, data_end, header):
            with HDF5File(self._ref_save_file, "w") as h5f:
                h5f["data_start"] = data_start
                h5f["data_end"] = data_end
                h5f["tomwer_info"] = "copied using refCopy"
                h5f["original_scan"] = str(scan)
                h5f["srcurrent"] = -1
            # update header if any edf write
            header["tomwer_info"] = "copied using refCopy"
            header["original_scan"] = str(scan)
            header["SRCUR"] = -1
            dicttoh5(
                header,
                h5file=self._ref_save_file,
                h5path="header",
                overwrite_data=False,
                mode="a",
            )

        assert isinstance(url, DataUrl)
        if url.scheme() == "fabio":

            def normalize_edf(data):
                srCurrent = utils.getClosestSRCurrent(
                    scan_dir=scan.path, refFile=url.file_path()
                )
                if srCurrent in (None, -1):
                    logger.warning(
                        "Can't find information about srCurrent,"
                        "set to default value for normalization"
                    )
                    srCurrent = self.DEFAULT_SRCURRENT

                if not self.contains_dark(scan=scan):
                    logger.warning("No darkHST recorded, unable to normalize")
                    return data, srCurrent

                dark_data = self._get_dark_info()
                if dark_data is None:
                    logger.warning("No darkHST found in %s" % self._dark_save_file)
                    return None, None
                else:
                    dark_data = dark_data["data"]
                if data.shape != dark_data.shape:
                    err = (
                        "cannot normalize data from %s, has different "
                        "dimensions" % (self._darkHST)
                    )
                    logger.error(err)
                    return data, srCurrent
                return (data - dark_data).astype(numpy.float32) / srCurrent, srCurrent

            with fabio.open(url.file_path()) as file_desc:
                data = file_desc.data
                header = file_desc.header
                data, sr_current = normalize_edf(data)
                write(data_start=data, data_end=data, header=header)
                # TODO: look but the writing should be more or less generic
        elif url.scheme() in ("silx", "h5py"):
            flats = DarkRefs.get_flats_frm_process_file(
                scan.process_file, entry=scan.entry, as_url=False
            )
            if len(flats) == 0:
                logger.warning(
                    "No flat found in %s, unable to copy" % scan.process_file
                )
                return
            key_0 = sorted(list(flats.keys()))[0]
            data_start = flats[key_0]
            if len(flats) > 2:
                key_end = sorted(list(flats.keys()))[-1]
                data_end = flats[key_end]
            else:
                data_end = data_start
            header = {}
            write(data_start=data_start, data_end=data_end, header=header)
        else:
            raise ValueError("scheme not managed")

    def _copy_dark_from(self, scan, dark_url: DataUrl):
        assert isinstance(dark_url, DataUrl)
        assert isinstance(scan, TomwerScanBase)
        if dark_url.scheme() == "fabio":
            with fabio.open(dark_url.file_path()) as dsc:
                header = dsc.header.copy()
                data = dsc.data.copy()
                dark_file_basename = os.path.basename(dark_url.file_path())
        elif dark_url.scheme() in ("h5py", "silx"):
            darks = DarkRefs.get_darks_frm_process_file(
                scan.process_file, entry=scan.entry, as_url=False
            )
            if len(darks) == 0:
                logger.warning(
                    "No dark found in %s, unable to copy" % scan.process_file
                )
                return
            key_0 = sorted(list(darks.keys()))[0]
            data = darks[key_0]
            dark_file_basename = None
            # TODO: get some metadata ?
            header = {}
        else:
            raise ValueError("scheme not managed")

        # add origin of the dark file
        with HDF5File(self._dark_save_file, "w") as h5f:
            # h5f['header'] = header
            h5f["tomwer_info"] = "copied using refCopy"
            h5f["original_scan"] = str(scan)
            h5f["data"] = data
            h5f["srcurrent"] = -1
            if dark_file_basename is not None:
                h5f["dark_basename"] = dark_file_basename
        header["tomwer_info"] = "copied using refCopy"
        header["original_scan"] = str(scan)
        header["SRCUR"] = -1
        dicttoh5(
            header,
            h5file=self._dark_save_file,
            h5path="header",
            overwrite_data=False,
            mode="a",
        )

    def _get_flat_info(self) -> typing.Union[None, dict]:
        """return ref data. Only one store for now"""
        if self.has_flat_stored():
            with HDF5File(self._ref_save_file, "r", swmr=True) as h5f:
                return {
                    "data_start": h5py_read_dataset(h5f["data_start"]),
                    "data_end": h5py_read_dataset(h5f["data_end"]),
                    "original_scan": h5py_read_dataset(h5f["original_scan"]),
                    "srcurrent": h5py_read_dataset(h5f["srcurrent"]),
                    "header": h5todict(h5file=self._dark_save_file, path="header"),
                    "tomwer_info": h5py_read_dataset(h5f["tomwer_info"]),
                }
        else:
            return None

    def _get_dark_info(self) -> typing.Union[None, dict]:
        """return dark data, header, original_scan"""
        if self.has_dark_stored():
            with HDF5File(self._dark_save_file, "r", swmr=True) as h5f:
                if "dark_basename" in h5f:
                    dark_basename = h5py_read_dataset(h5f["dark_basename"])
                else:
                    dark_basename = None
                res = {
                    "data": h5py_read_dataset(h5f["data"]),
                    "original_scan": h5py_read_dataset(h5f["original_scan"]),
                    "srcurrent": h5py_read_dataset(h5f["srcurrent"]),
                    "dark_basename": dark_basename,
                    "tomwer_info": h5py_read_dataset(h5f["tomwer_info"]),
                    "header": h5todict(h5file=self._dark_save_file, path="header"),
                }
                return res
        else:
            return None

    def clean_save_files(self):
        for f in os.listdir(self._savedir):
            if os.path.isfile(f) and os.path.exists(f):
                os.remove(f)

    def run(self):
        """
        This is function triggered when a new scan / data is received.
        As explained in issue #184 the behavior is the following:

        * if the scan has already ref files files won't be overwrite
        * if the mode is in `auto` will register last ref file met
        * if the scan has no ref files and refCopy has some register. Will
          create a copy of those, normalized from srCurrent (for flat field)
        """
        scan = self.inputs.data
        if not isinstance(scan, (type(None), TomwerScanBase, dict)):
            raise TypeError(
                f"self.inputs.data is expected to be an instance "
                f"of None, TomwerScanBase or dict. Not {type(scan)}"
            )
        if scan is None or scan.path is None:
            return
        # process dark and ref calculation
        super().run()
        # then copy if necessary
        if not self._processOnlyDkRf:
            if self.contains_dark_or_ref(scan):
                if self.is_on_mode_auto:
                    self.set_refs_from_scan(scan)
            if self.has_missing_dark_or_ref(scan):
                self._copy_to(scan)

    def has_flat_or_dark_stored(self) -> bool:
        """

        :return: True if the process has at least registered one flat or one
                 dark
        :rtype: bool
        """
        return self.has_flat_stored() or self.has_dark_stored()

    def has_flat_stored(self) -> bool:
        """

        :return: True if the process has registered at least one ref
        :rtype: bool
        """
        return os.path.exists(self._ref_save_file)

    def has_dark_stored(self) -> bool:
        """

        :return: True if the process has registered at least one dark
        :rtype: bool
        """
        return os.path.exists(self._dark_save_file)

    def contains_dark(self, scan: TomwerScanBase) -> bool:
        """Return True if the scan has already some dark processed"""
        if not isinstance(scan, TomwerScanBase):
            return TypeError(
                "scan is expected to be an instance of {} and not {}".format(
                    TomwerScanBase, type(scan)
                )
            )

        if isinstance(scan, EDFTomoScan):
            return (
                len(
                    DarkRefs.getDarkHSTFiles(
                        directory=scan.path, prefix=self.darkHST_prefix
                    )
                )
                > 0
            )
        elif isinstance(scan, HDF5TomoScan):
            if scan.process_file is None or not os.path.exists(scan.process_file):
                return False
            else:
                return (
                    len(
                        DarkRefs.get_darks_frm_process_file(
                            scan.process_file, entry=scan.entry, as_url=True
                        )
                    )
                    > 0
                )
        else:
            raise ValueError("scan type not managed")

    def contains_flat(self, scan: TomwerScanBase):
        """Return True if the scan has already some dark processed"""
        if not isinstance(scan, TomwerScanBase):
            return TypeError(
                "scan is expected to be an instance of {} and not {}".format(
                    TomwerScanBase, type(scan)
                )
            )

        if isinstance(scan, EDFTomoScan):
            return (
                len(
                    DarkRefs.getRefHSTFiles(
                        directory=scan.path, prefix=self.refHST_prefix
                    )
                )
                > 0
            )
        elif isinstance(scan, HDF5TomoScan):
            if scan.process_file is None or not os.path.exists(scan.process_file):
                return False
            else:
                return (
                    len(
                        DarkRefs.get_flats_frm_process_file(
                            scan.process_file, entry=scan.entry, as_url=True
                        )
                    )
                    > 0
                )
        else:
            raise ValueError("scan type not managed")

    def contains_dark_or_ref(self, scan):
        return self.contains_dark(scan=scan) or self.contains_flat(scan=scan)

    def has_missing_dark_or_ref(self, scan: TomwerScanBase) -> bool:
        """return True if the scan has no ref or no dark registered"""
        assert isinstance(scan, TomwerScanBase)
        return not self.contains_dark(scan) or not self.contains_flat(scan)

    def _signal_done(self, scan):
        assert isinstance(scan, TomwerScanBase)
        raise NotImplementedError("Abstract class")

    def set_mode_auto(self, b):
        self._mode_auto = b

    @property
    def is_on_mode_auto(self):
        return self._mode_auto

    @property
    def refHST_prefix(self):
        return self._refHstPrefix

    @property
    def darkHST_prefix(self):
        return self._darkHstPrefix

    def set_refHST_prefix(self, prefix):
        self._refHstPrefix = prefix

    def set_darkHST_prefix(self, prefix):
        self._darkHstPrefix = prefix

    def clear_ref(self):
        if self._ref_save_file is not None:
            os.remove(self._ref_save_file)
        if self._dark_save_file is not None:
            os.remove(self._dark_save_file)

    def get_dark_save_file(self):
        return self._dark_save_file

    def get_ref_save_file(self):
        return self._ref_save_file
