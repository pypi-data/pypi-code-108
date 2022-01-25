# /*##########################################################################
# Copyright (C) 2016-2017 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
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

__author__ = ["PJ.Gouttenoire", "H. Payno"]
__license__ = "MIT"
__date__ = "22/01/2018"

from tomwer.core.process.task import Task
import tomwer.version as tomwer_version
from tomwer.core.utils.pyhstutils import _getPyHSTDir
from tomwer.core.process.reconstruction.ftseries.params.paganin import PaganinMode
from tomwer.core.process.reconstruction.ftseries.params.ft import FixedSliceMode
from tomwer.core.process.reconstruction.ftseries.params import ReconsParams
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.settings import get_lbsram_path, get_dest_path
from silx.io.url import DataUrl
import logging
from tomwer.core import settings
from tomoscan.unitsystem import metricsystem
from .pyhstnxconverter import convert_nx_to_pyhst_hdf5, _pyhst_hdf5_info
import socket
import subprocess
import typing
import os

logger = logging.getLogger(__name__)


class PyHSTCaller(Task, input_names=("data",), output_names=("data",)):
    """Simple class containing information to be able to call PyHST"""

    REC_EXT = ".rec"
    """Extension of the record file"""
    PAR_EXT = ".par"
    """Extension of the reconstruction parameters file"""

    def __init__(self, varinfo=None, inputs=None, label=None):
        super().__init__(varinfo=varinfo, inputs=inputs, label=label)
        self._scan = inputs.get("data", None)
        self._dry_run = inputs.get("dry_run", False)
        self._rec_slices_only = inputs.get("rec_slices_only", True)
        self._full_rec_to_dest = inputs.get("full_rec_to_dest", True)
        self._slices_rec_to_dest = inputs.get("slices_rec_to_dest", False)
        if "recons_params" in inputs:
            raise KeyError(
                "Do not use recons_params but `pyhst2_recons_params` instead"
            )
        recons_params = inputs.get("pyhst2_params", None)
        if isinstance(recons_params, dict):
            self._recons_params = ReconsParams.from_dict(recons_params)
        else:
            self._recons_params = recons_params
        if self._recons_params is None:
            raise ValueError(
                "'pyhst2_recons_params' (ftseries reconstruction parameters) should be provided"
            )
        if self._recons_params is None:
            raise ValueError("'data' (scan) should be provided")

        self.execDir = _getPyHSTDir()

    @staticmethod
    def program_name():
        """Name of the program used for this processing"""
        return "PyHST2"

    @staticmethod
    def program_version():
        """version of the program used for this processing"""
        return "defined in configuration"

    @staticmethod
    def definition():
        """definition of the process"""
        return "call PyHST2 to run tomography reconstructions"

    @staticmethod
    def isvalid(exec_dir, pyhst_exe):
        """

        :param exec_dir: directory containing the pyhst executable(s)
        :param pyhst_exe: name of the selected pyhst executable
        :returns: True if the exe file exists
        :rtype: bool
        """
        if pyhst_exe in os.environ.keys():
            return os.path.isfile(os.environ[pyhst_exe])
        elif exec_dir is None or pyhst_exe is None:
            return False
        else:
            return os.path.isfile(os.path.join(exec_dir, pyhst_exe))

    def _get_basefile_name_with_pag_des(
        self, paganin_opts: dict, scan_path: str, slice: typing.Union[None, int]
    ) -> str:
        """Return the *.par, *.rec and the *_correct.txt file name including
        the description of the paganin reconstruction

        :param several_pag: is there several paganin reconstruction to run
        :type: bool
        :param paganin_opts: paganin options for this reconstruction
        :type: dict
        :param scan_path: scan path
        :type: str
        :param slice: slice to reconstruct. If None then we want to reconstruct
                      the full volume
        :type: Union[None, int]
        :return: basename to use for file reconstruction
        :rtype: str
        """
        assert "DB" in paganin_opts, "requested to determine basefile name"
        assert "DB2" in paganin_opts, "requested to determine basefile name"
        assert "MODE" in paganin_opts, "requested to determine basefile name"
        scan_basename = os.path.basename(scan_path)
        pag_mod = PaganinMode.from_value(paganin_opts["MODE"])

        if pag_mod == PaganinMode.off:
            raise ValueError(
                "This function should not be call if paganin mode" " is off"
            )
        elif pag_mod in (PaganinMode.on, PaganinMode.both):
            if slice is None:
                try:
                    return "_".join(
                        (scan_basename + "pag", "%04d" % int(paganin_opts["DB"]))
                    )

                except Exception:
                    return "_".join(
                        (scan_basename + "pag", "%04.4i" % float(paganin_opts["DB"]))
                    )
            else:
                try:
                    return "_".join(
                        (scan_basename + "slice_pag", "%04d" % int(paganin_opts["DB"]))
                    )
                except Exception:
                    return "_".join(
                        (scan_basename + "slice_pag%04.4i" % float(paganin_opts["DB"]))
                    )

        elif pag_mod == PaganinMode.multi:
            if slice is None:
                multi_pag_val = "db%04.4i-db%04.4i" % (
                    paganin_opts["DB"],
                    float(paganin_opts["DB2"]),
                )
                return "_".join((scan_basename + "multipag", multi_pag_val))
            else:
                multi_pag_val = "db%04.4i-db%04.4i" % (
                    paganin_opts["DB"],
                    paganin_opts["DB2"],
                )
                return "_".join((scan_basename + "slice_multipag", multi_pag_val))

    def run(self):
        """
        The goal of this section is to generate all requested .rec and .par
        files that will ce executed later.

        Create the .par file and execute pyhst on it.
        Tomwer is looking one some specific folders to find the pyhst
        installation directory (first 'PYHST_DIR' if this environment variable
        is defined then /usr/bin. Get also pysht version defined as an
        environment variable like 'PyHST2_*')

        :param scan: acquisition to reconstruct
        :type: :class:`TomoBase`
        :param dry_run: if True then skip call to pyhst and only create .par
                        and .rec files
        :type: bool
        :param rec_slices_only: if True only call pyhst for the slice to be
                                reconstructed if any.
        :type: bool
        :param full_rec_to_dest: replace LBSRAM_ID by DEST_ID on the .par files
                                 used for full volume reconstruction
        :type: bool
        :param slices_rec_to_dest: replace LBSRAM_ID by DEST_ID on the .par
                                   files used for full slices reconstruction
        :type: bool
        """
        if self._scan is None:
            return None
        elif not isinstance(self._scan, TomwerScanBase):
            raise TypeError(
                "scan is expected to be an instance of "
                "TomwerScanBase. Not {}".format(type(self._scan))
            )
        self._scan.ftseries_recons_params = self._recons_params
        cuda_devices = self._scan.ftseries_recons_params.pyhst.cuda_devices

        def filter_paganin_values(rp):
            """We can have some value store in db and db2 but without a
            paganin mode turn on. If this is the case we want to avoid
            calling several time the same .par file"""
            assert rp is not None
            assert rp.paganin.mode in PaganinMode
            if rp.paganin.mode is PaganinMode.multi:
                pass
            elif rp.paganin.mode in (PaganinMode.on, PaganinMode.both):
                rp.paganin.db2 = "(-1, )"
            elif rp.paganin.mode is PaganinMode.off:
                rp.paganin.db = "(-1, )"
                rp.paganin.db2 = "(-1, )"
            return rp

        # cuda devices to use
        recons_params = ReconsParams(empty=False)
        recons_params.copy(self._scan.ftseries_recons_params)
        recons_params = filter_paganin_values(recons_params)
        recons_list = recons_params.to_unique_recons_set(as_to_dict=True)
        # set of unique reconstruction parameters
        has_several_pag = recons_params.paganin.has_several_db_param()

        # if needed convert hdf5 files
        if isinstance(self._scan, HDF5TomoScan):
            hdf5_info = convert_nx_to_pyhst_hdf5(scan=self._scan)
        else:
            hdf5_info = None

        slices = set((None,))
        if recons_params.ft.do_test_slice:
            fixed_slice = self._scan.ftseries_recons_params.ft.fixed_slice_as_list()
            try:
                fixed_slice = FixedSliceMode.from_value(fixed_slice)
            except (ValueError, TypeError):
                # in this case we are in row n and the value set is the
                # value(s) of the slice to reconstruct
                pass

            if fixed_slice is FixedSliceMode.middle:
                n_slice = self._scan.dim_2 or 2048
                slices.add(n_slice // 2)
            else:
                # in this case we are on row n mode
                if isinstance(fixed_slice, typing.Iterable):
                    [slices.add(slice) for slice in fixed_slice]
                else:
                    slices.add(fixed_slice)
        recons_urls = []
        for slice in slices:
            for recons_param in recons_list:
                if slice is None and self._rec_slices_only is True:
                    run_recons = False
                else:
                    run_recons = True
                if slice is None:
                    convert_lbsram_to_dest = self._full_rec_to_dest
                else:
                    convert_lbsram_to_dest = self._slices_rec_to_dest
                recons_urls.extend(
                    self._process_frm_one_slice_one_rp_set(
                        scan=self._scan,
                        slice=slice,
                        recons_param=recons_param,
                        has_several_pag=has_several_pag,
                        dry_run=self._dry_run,
                        run_recons=run_recons,
                        cuda_devices=cuda_devices,
                        convert_lbsram_to_dest=convert_lbsram_to_dest,
                        hdf5_info=hdf5_info,
                    )
                )
        self._scan.set_latest_reconstructions(recons_urls)

        if self._dry_run is False:
            entry = "entry"
            if isinstance(self._scan, HDF5TomoScan):
                entry = self._scan.entry
            with self._scan.acquire_process_file_lock():
                self.register_process(
                    process_file=self._scan.process_file,
                    entry=entry,
                    configuration=recons_params.to_dict(),
                    results={},
                    process_index=self._scan.pop_process_index(),
                    overwrite=True,
                )
        return self._scan

    def _process_frm_one_slice_one_rp_set(
        self,
        scan: TomwerScanBase,
        slice: typing.Union[int, None],
        recons_param: dict,
        cuda_devices: typing.Union[None, typing.Iterable],
        has_several_pag: bool,
        run_recons: bool,
        convert_lbsram_to_dest: bool,
        dry_run: bool,
        hdf5_info: _pyhst_hdf5_info,
    ) -> list:
        """
        process pyhstcaller from one specific slice indice and one set
        of reconstruction parameter (so all paramter should be unique)

        :param TomwerScanBase scan: scan to reconstruct
        :param Union[int, None] slice: slice index or None. If None then we
                                       will process the entire volume.
        :param recons_param: reconstruction parameters. warning: this set of
                             parameter should only contain unique values
                             contrary to the one given in process. This peace
                             of code won't apply the `to_unique_recons_set`
                             function
        :type recons_param: dict
        :param Union[None, Iterable] cuda_devices: list of cuda devices to use
                                                   for reconstruction
        :param bool has_several_pag: should we run several Paganin
                                     reconstruction for this scan.
        :param bool run_recons: if True then call pyhst within the created .par
                                file (depending on dry-run parameter of course)
        :param bool convert_lbsram_to_dest: if True then convert all path to
                                            the 'dest folder'.
        :param bool dry_run: if True then skip call to pyhst and only create
                             .par and .rec files
        :param hdf5_info: information regarding hdf5 if any created
        :return: list of the url to access the slice reconstructed
        :rtype: list
        """
        assert isinstance(recons_param, dict)
        assert isinstance(slice, (type(None), int))
        if slice is None:
            logger.info("manage .par for volume")
        else:
            logger.info("manage .par for slice %s" % slice)
        # deduce file base name
        if PaganinMode.from_value(recons_param["PAGANIN"]["MODE"]) == PaganinMode.off:
            base_file_name = os.path.basename(scan.path)
            if slice is not None:
                base_file_name = base_file_name + "slice"
                par_file_name = base_file_name + ("_%04d.par" % slice)
            else:
                par_file_name = base_file_name

            if not par_file_name.endswith(".par"):
                par_file_name = par_file_name + ".par"
            correct_file_name = os.path.join(scan.path, "correct.txt")
        else:
            base_file_name = self._get_basefile_name_with_pag_des(
                paganin_opts=recons_param["PAGANIN"], scan_path=scan.path, slice=slice
            )
            # note: adding the slice on the name file is done on the
            # `_get_basefile_name_with_pag_des` function
            correct_file_name = base_file_name + "_correct.txt"
            if slice is None:
                par_file_name = base_file_name + ".par"
            else:
                par_file_name = base_file_name + "_%04d.par" % slice

        # create correct.txt, .par, .rec and execute the .par using physt
        try:
            if recons_param["FTAXIS"]["DO_AXIS_CORRECTION"] and (
                recons_param["FTAXIS"]["USE_TOMWER_AXIS"]
                or recons_param["FTAXIS"]["TRY_USE_OLD_TOMWER_AXIS"]
            ):
                cor = self.get_center_of_rotation(
                    scan=scan,
                    use_tomwer_axis=recons_param["FTAXIS"]["USE_TOMWER_AXIS"],
                    use_old_tomwer_processes=recons_param["FTAXIS"][
                        "TRY_USE_OLD_TOMWER_AXIS"
                    ],
                    output_file=correct_file_name,
                )
                cor = cor if cor is None else float(cor)
            else:
                cor = None
            self.make_par_file(
                dirname=scan.path,
                scan=scan,
                recons_param=recons_param,
                out_base_file_name=base_file_name,
                slice=slice,
                convert_path=convert_lbsram_to_dest,
                par_file_path=os.path.join(scan.path, par_file_name),
                cor=cor,
                hdf5_info=hdf5_info,
            )
            assert os.path.exists(os.path.join(scan.path, par_file_name))
        except ValueError as e:
            logger.error("Fail to generate .par file. " + str(e))
            return list()
        else:
            if recons_param["PYHSTEXE"]["MAKE_OAR_FILE"]:
                # create .rec if needed
                prefix = base_file_name or os.path.basename(scan.path)
                rec_file_name = os.path.join(scan.path, prefix + PyHSTCaller.REC_EXT)
                self.make_rec_file(
                    rec_file=rec_file_name,
                    recons_params=recons_param,
                    par_file=par_file_name,
                )

            # execute pyhst
            exec_dir = _getPyHSTDir()
            pyhst_exe = recons_param["PYHSTEXE"]["EXE"]
            if recons_param["PYHSTEXE"]["VERBOSE"]:
                pyhst_out = None
            else:
                pyhst_out = os.path.join(
                    scan.path, recons_param["PYHSTEXE"]["VERBOSE_FILE"]
                )
            if run_recons is True:
                if isinstance(scan, HDF5TomoScan):
                    exec_path = scan.path
                else:
                    exec_path = None
                try:
                    self.execute(
                        exec_dir=exec_dir,
                        pyhst_exe=pyhst_exe,
                        par_file=os.path.join(scan.path, par_file_name),
                        cuda_devices=cuda_devices,
                        dry_run=dry_run,
                        pyhst_out=pyhst_out,
                        exec_path=exec_path,
                    )
                except ValueError as e:
                    logger.error(e)
                    return list()
                else:
                    if dry_run is True:
                        return list()
                    else:
                        if recons_param["FT"]["VOLOUTFILE"] == 1:
                            output_file_ext = ".vol"
                            scheme = "tomwer"
                        else:
                            output_file_ext = ".edf"
                            scheme = "fabio"
                        recons_file = par_file_name.replace(".par", output_file_ext)
                        recons_file = os.path.join(scan.path, recons_file)
                        recons_url = DataUrl(
                            file_path=recons_file, data_slice=None, scheme=scheme
                        )
                        return [recons_url]
            else:
                return list()

    def get_center_of_rotation(
        self,
        scan: TomwerScanBase,
        use_tomwer_axis: bool,
        use_old_tomwer_processes: str,
        output_file: str,
    ):
        """

        :param scan: scan for which we want to create the correct file.
                     if `USE_TOMWER_AXIS` is True then will first look for some
                     axis process computation in the history.
                     if `TRY_USE_OLD_TOMWER_AXIS` is True then will look for
                     any tomwer_processes file store in the scan directory
                     to extract it the center of rotation value
        :type: TomoBase
        :param use_tomwer_axis: use the history contained in the axis file
        :type: bool
        :param use_old_tomwer_processes: use information contained in the
                                         tomwer_processes file
        :type: bool
        :param output_file: output file name
        :type: str
        :return: name of the file where the center of rotation information
                 has been written. None if not cor information stored
        :type: Union[None,str]
        """
        if use_tomwer_axis:
            if (
                scan.axis_params is not None
                and scan.axis_params.relative_cor_value is not None
            ):
                logger.info(
                    "load center of rotation from previous axis "
                    "process: %s" % scan.axis_params.relative_cor_value
                )
                return scan.axis_params.relative_cor_value
        if use_old_tomwer_processes and scan.process_file is not None:
            if os.path.exists(scan.process_file):
                from tomwer.core.process.reconstruction.axis import AxisRP

                cor = AxisRP.get_cor_position_frm_tomwer_file(
                    file_path=scan.process_file
                )
                logger.info(
                    "load center of rotation from %s: %s" % (scan.process_file, cor)
                )
                return cor
        return None

    def execute(
        self,
        exec_dir: str,
        pyhst_exe: str,
        par_file: str,
        cuda_devices: list,
        dry_run: bool = False,
        pyhst_out: typing.Union[None, str] = None,
        exec_path=None,
    ) -> bool:
        """
        Run pyhst for the given par file

        :param exec_dir: directory containing the pyhst executable(s)
        :param str pyhst_exe: name of the selected pyhst executable
        :param str par_file: file to use to call pyhst
        :param list cuda_devices: list of `CudaDevice` to use in localhost for
                             executing the reconstruction
        :param bool dry_run: if True, won't execute the pyhst reconstruction
        :param pyhst_out: if specify, link to pyhst log file
        :rtype: Union[None,str]
        """
        assert par_file is not None
        if dry_run is False:
            if not os.path.exists(par_file):
                raise IOError(par_file + "does not exists")

            if not PyHSTCaller.isvalid(pyhst_exe=pyhst_exe, exec_dir=exec_dir):
                raise ValueError(
                    "physt executable definition, %s, %s is invalid"
                    % (exec_dir, pyhst_exe)
                )

        try:
            if pyhst_exe in os.environ.keys():
                pyhst_exe = os.environ[pyhst_exe]
            gpu_cmd_opt = self._get_gpu_command(cuda_devices)
            logger.info(" ".join(("launching: ", pyhst_exe, par_file, gpu_cmd_opt)))
            if dry_run is False:
                if pyhst_out is not None:
                    with open(pyhst_out, "w") as fout:
                        self.__execute(
                            pyhst_exe=pyhst_exe,
                            par_file=par_file,
                            gpu_cmd_opt=gpu_cmd_opt,
                            stdout=fout,
                            exec_path=exec_path,
                        )
                else:
                    self.__execute(
                        pyhst_exe=pyhst_exe,
                        par_file=par_file,
                        gpu_cmd_opt=gpu_cmd_opt,
                        stdout=None,
                        exec_path=exec_path,
                    )
        except OSError as e:
            logger.error("reconstruction fails", e)
            return False
        else:
            logger.info("reconstruction of %s finished." % par_file)
            return True

    def __execute(self, pyhst_exe, par_file, gpu_cmd_opt, stdout, exec_path):
        logger.info("processing pyhst reconstruction... (%s)" % par_file)
        subprocess.call(
            " ".join((pyhst_exe, par_file, gpu_cmd_opt)),
            shell=True,
            stdout=stdout,
            stderr=stdout,
            cwd=exec_path,
        )
        logger.info("pyhst reconstruction finished (%s)" % par_file)

    @staticmethod
    def _get_gpu_command(devices):
        """compute the extension of the command to use specific gpus"""
        if devices is None:
            return ""
        else:
            devices_id = []
            for device in devices:
                from tomwer.core.utils.device import CudaDevice

                if isinstance(device, CudaDevice):
                    devices_id.append(str(device.id))
                elif isinstance(device, int):
                    devices_id.append(str(device))
            devices_id.insert(0, socket.gethostname())
            return ",".join(devices_id)

    def make_par_file(
        self,
        dirname,
        scan,
        recons_param,
        slice,
        convert_path,
        par_file_path: str,
        hdf5_info,
        out_base_file_name=None,
        options=None,
        cor=None,
    ):
        """
        Function creating the .par file

        creates parameter file for processing with PyHST
        The par file requires 9 fixed arguments:

        * argument 1: direc : path of the scan directory
        * argument 2: prefix : scan prefix
        * argument 3: nvue : number of angles used in the reconstruction
        * argument 4: num_image_1 : number of pixels in the projections along the first axis (horizontal)
        * argument 5: num_image_2 : number of pixels in the projections along the second axis (vertical)
        * argument 6: image_pixel_size : pixel size in microns
        * argument 7: corr : do flatfield correction + log or not: 'YES' or 'NO'
        * argument 8: refon : interval between the flatfield files: e.g. 100
        * argument 9: offset : position of rotation axis with respect to middle in pixels

        :param dirname: the directory to store the .par file
        :param TomwerScanBase scan: scan to reconstruct
        :param slice: slice to reconstruct. If None then we will reconstruct
                      the entire volume
        :type: int
        :param convert_path: if true, convert all path to destination path
                             (used on lbsram system)
        :type: bool
        :param out_base_file_name: the par file name.
        :type: Union[None,str]
        :param correct_file: text file containing the correction to apply
        :type: str
        :param options: dictionary with options you want to set.
                        Regular options are:

                        * 'parfilename': parameter file ( default: direc/prefix.par )
                        * 'start_voxel_1': first pixel in x (starting from 1)
                          (default 1)
                        * 'start_voxel_2': first pixel in y (starting from 1)
                          (default 1)
                        * 'start_voxel_3': first pixel in z (starting from 1)
                          (default 1)
                        * 'end_voxel_1': last pixel in x (starting from 1)
                          (default num_image_1)
                        * 'end_voxel_2': last pixel in y (starting from 1)
                          (default num_image_1)
                        * 'end_voxel_3': last pixel in z (starting from 1)
                          (default num_image_2)
                        * 'angle_offset': offset angle in degrees
                          (default 0)
                        * 'output_file': name of the volume file
                          (default: direc/prefix.vol)
                        * 'ff_prefix': prefix of the flatfield images
                          (default: direc/refHST)
                        * 'background_file': name of the dark file
                          (default: = direc/dark.edf)
                        * 'horaxis': rotation axis horizontal (=constant y) (1)
                          or not (=constant x) (0) ( default 0 )
                        * 'correct_spikes_threshold' : threshold value for ccd
                          filter when value is given, ccd filter will be
                          applied with this parameter (default : parameter is
                          set to 0.04, but DO_CCD_FILTER = 'NO')
                        * 'ccd_filter': filter for correction of spikes
                          (default: 'CCD_Filter')
                        * 'ccd_filter_para': parameters for ccd filter when
                          given overrides choice with correct_spikes_threshold
                        * 'do_axis_correction' : correct for sample motion
                          (default: 'NO')
                        * 'axis_correction_file': name of file with sample
                          movement (default: 'correct.txt' )
                        * 'first column': x motion [ , second column: y motion]
                        * 'do_sino_filter': correction of rings by filtering
                          the sinogram ( default: 'NO' )
                        * 'sino_filter': filter for correction of rings
                          (default: 'SINO_Filter')
                        * 'correct_rings_nb': number of elements (`|f|>0`) that
                          will not be filtered from sinograms (default 8)
                        * 'padding': padding at edges with edge values 'E' or
                          zero '0' ( default: 'E' )
                        * 'axis_to_the_center' : move axis to the center 'Y' or
                          not 'N' (default: 'Y') !!!
                        * 'angle_between_projections': angle between successive
                          projections ( default 180/nvue )
                        * 'doubleffcorrection': name of the file (e.g.
                          filtered_mean.edf) for double flatfield subtracted
                          after normal flatfield and logarithm.
                        * 'do_projection_median': calculate median of
                          projections (after flat/log) (default: 'NO')
                        * 'projection_median_filename' : name of output
                          edf-file with median (default: median.edf)
                        * 'do_projection_mean': calculate mean of projections
                          (after flat/log) (default: 'NO')
                        * 'projection_mean_filename': name of output edf-file
                          with mean (default: mean.edf) PyHST uses for both
                          median and mean PROJECTION_MEDIAN_FILENAME

                    Advanced options (= do not change, except if you know what
                    you are doing):

                        * 'zeroclipvalue': minimum value of radiographs after
                          flatfield / before logarithm values below are clipped
                          (default 1e-9)
                        * 'oneclipvalue': maximum value of radiographs after
                          flatfield / before logarithm values above are clipped
                          (default: not applied)
                        * 'multiframe': more than one projection in input file
                          (default: 0)
                        * 'num_first_image': index of first image used in
                          reconstruction (default 0)
                        * 'num_last_image': index of last image
                          (default nvue-1)
                        * 'number_length_varies': width index varies or not
                          (default: 'NO')
                        * 'length_of_numerical_part': width of image index
                          (default 4)
                        * 'file_postfix': extension of the image files
                          (default: '.edf')
                        * 'file_interval': downsample in angle (default 1)
                        * 'subtract_background': subtract dark file 'YES' or
                          not 'NO' ( default: corr )
                        * 'correct_flatfield': divide by flatfield image 'YES'
                          or not 'NO' (default: corr)
                        * 'take_logarithm': use -log 'Y' or 'N'
                          (default: 'YES')
                        * 'output_sinograms': output sinogram files or not
                          (default: 'NO')
                        * 'output_reconstruction': do the reconstruction or not
                          (default: 'YES')
                        * 'oversampling_factor': oversampling of projections
                          before backprojection (0 = linear interpolation,
                          1 = nearest pixel) ( default 4 )
                        * 'sinogram_megabytes': obsolete maximum memory in MB used for
                          reading the sinograms ( default 400 )
                        * 'cache_kilobytes': obsolete ( default 256 )
                        * 'display_graphics': obsolete NOT IMPLEMENTED IN PYHST
                          (default: 'NO')
                        * cor: center of rotation, given from [-image_width/2, image_width/2]
            :param hdf5_info: information regarding hdf5 if any created
        """
        assert isinstance(scan, TomwerScanBase)
        # add some missing values:
        recons_param["FT"]["FILE_PREFIX"] = os.path.basename(scan.path)
        # TODO: how can we obtain num of last image, NUM_IMAGE_1, NUM_IMAGE_2... ???
        recons_param["FT"]["NUM_LAST_IMAGE"] = len(scan.projections)
        recons_param["FT"]["NUM_IMAGE_1"] = scan.dim_1
        recons_param["FT"]["NUM_IMAGE_2"] = scan.dim_2
        scan_range = scan.scan_range
        recons_param["FT"]["IMAGE_PIXEL_SIZE_1"] = (
            (scan.pixel_size / metricsystem.micrometer.value)
            if scan.pixel_size is not None
            else None
        )
        # TODO: the next values should be deduced from some 'flow' recording or scan tag
        recons_param["FT"]["CORRECT_FLATFIELD"] = True
        recons_param["FT"]["FF_FILE_INTERVAL"] = scan.ff_interval

        # those values can't be set by options
        prefix = recons_param["FT"]["FILE_PREFIX"]
        nvue = recons_param["FT"]["NUM_LAST_IMAGE"]
        num_image_1 = recons_param["FT"]["NUM_IMAGE_1"]
        num_image_2 = recons_param["FT"]["NUM_IMAGE_2"]
        image_pixel_size = recons_param["FT"]["IMAGE_PIXEL_SIZE_1"]
        corr = "YES" if recons_param["FT"]["CORRECT_FLATFIELD"] else "NO"
        refon = recons_param["FT"]["FF_FILE_INTERVAL"]
        direc = dirname

        fileParameter = self._loadDefaultPar(
            recons_param=recons_param,
            out_base_file_name=out_base_file_name,
            direc=direc,
            image_pixel_size=image_pixel_size,
            corr=corr,
            nvue=nvue,
            refon=refon,
            num_image_1=num_image_1,
            num_image_2=num_image_2,
            slice=slice,
            scan_range=scan_range,
            convert_lbsram=convert_path,
            cor=cor,
        )
        # Dealing with options
        if options:
            for opt in options:
                fileParameter[opt] = options[opt]

        not_available = "N.A."

        FT = recons_param["FT"]
        PAG = recons_param["PAGANIN"]
        BG = recons_param["BEAMGEO"]
        paganin = PaganinMode.from_value(recons_param["PAGANIN"]["MODE"])

        length_of_numerical_part = FT["NUM_PART"]

        ###################################################
        ##### check and calculate dependent variables #####
        ###################################################
        if fileParameter["horaxis"]:
            # move center of rotation to the pyhst referrence [0, image_width]
            if cor is None:
                cor = num_image_2 / 2 if num_image_2 else None
            else:
                cor = num_image_2 / 2 + cor
            fileParameter["rotation_vertical"] = "NO"
            fileParameter["rotation_axis_position"] = cor
            fileParameter["end_voxel_12_limit "] = num_image_2
            fileParameter["end_voxel_3_limit"] = num_image_1
        else:
            # move center of rotation to the pyhst referrence [0, image_width]
            if cor is None:
                cor = num_image_1 / 2 if num_image_1 else None
            else:
                cor = num_image_1 / 2 + cor
            fileParameter["rotation_vertical"] = "YES"
            fileParameter["rotation_axis_position"] = cor
            fileParameter["end_voxel_12_limit"] = num_image_1
            fileParameter["end_voxel_3_limit"] = num_image_2

        # start_voxel should be > 0 ; end_voxel should be <= image dimension
        if fileParameter["start_voxel_1"] < 1:
            logger.warning("START_VOXEL_1 can not be zero or negative, forcing to 1")
            fileParameter["start_voxel_1"] = 1
        if fileParameter["start_voxel_2"] < 1:
            logger.warning("START_VOXEL_2 can not be zero or negative, forcing to 1")
            fileParameter["start_voxel_2"] = 1
        if fileParameter["start_voxel_3"] < 1:
            logger.warning("START_VOXEL_3 can not be zero or negative, forcing to 1")
            fileParameter["start_voxel_3"] = 1

        if fileParameter["half_acquisition"] == 0:
            if (fileParameter["end_voxel_1"] is not None) and (
                fileParameter["end_voxel_1"] > fileParameter["end_voxel_12_limit"]
            ):
                logger.warning(
                    "END_VOXEL_1 can not be larger than image dimension, forcing to maximum"
                )
                fileParameter["end_voxel_1"] = fileParameter["end_voxel_12_limit"]

            if (fileParameter["end_voxel_2"] is not None) and (
                fileParameter["end_voxel_2"] > fileParameter["end_voxel_12_limit"]
            ):
                logger.warning(
                    "END_VOXEL_2 can not be larger than image dimension, forcing to maximum"
                )
                fileParameter["end_voxel_2"] = fileParameter["end_voxel_12_limit"]

            fileParameter["avoidhalftomo"] = "Y"
        else:
            fileParameter["avoidhalftomo"] = "N"

        if "FORCE_HALF_ACQ" in recons_param["FT"].keys():
            if FT["FORCE_HALF_ACQ"] == 1 and fileParameter["half_acquisition"] != 0:
                fileParameter["avoidhalftomo"] = "-1"

        if (
            (fileParameter["end_voxel_3"] is not None)
            and (fileParameter["end_voxel_3_limit"] is not None)
            and (fileParameter["end_voxel_3"] > fileParameter["end_voxel_3_limit"])
        ):
            logger.warning(
                "END_VOXEL_3 can not be larger than image dimension, forcing to maximum\n"
            )
            fileParameter["end_voxel_3"] = fileParameter["end_voxel_3_limit"]

        # Remove directory head if necessary
        if convert_path:
            fileParameter["output_file"] = self._remove_lbs_head(
                fileParameter["output_file"]
            )

        if slice is None:
            if recons_param["FT"]["VOLOUTFILE"] == 1:
                output_file_ext = ".vol"
            else:
                output_file_ext = ".edf"
        else:
            output_file_ext = ""

        fileParameter["output_file"] = fileParameter["output_file"] + output_file_ext

        if paganin == PaganinMode.multi and fileParameter["multipag_extra_files"] == 1:

            # Remove directory head if necessary
            fileParameter["extra_output_file"] = self._remove_lbs_head(
                out_base_file_name
            )

            if fileParameter["multipag_keep_bone"] == 1:
                fileParameter["output_file_bone"] = (
                    fileParameter["extra_output_file"] + "_bone.vol"
                )

            if fileParameter["multipag_keep_soft"] == 1:
                fileParameter["output_file_soft"] = (
                    fileParameter["extra_output_file"] + "_soft.vol"
                )

            if fileParameter["multipag_keep_mask"] == 1:
                fileParameter["output_file_mask"] = (
                    fileParameter["extra_output_file"] + "_mask.vol"
                )

            if fileParameter["multipag_keep_abs"] == 1:
                fileParameter["output_file_abs"] = (
                    fileParameter["extra_output_file"] + "_abs.vol"
                )

            if fileParameter["multipag_keep_corr"] == 1:
                fileParameter["output_file_corr"] = (
                    fileParameter["extra_output_file"] + "_corr.vol"
                )

        if fileParameter["parfilename"][0] != os.path.sep:
            fileParameter["parfilename"] = os.path.join(
                direc, fileParameter["parfilename"]
            )

        if fileParameter["background_file"][0] != os.path.sep:
            fileParameter["background_file"] = os.path.join(
                direc, fileParameter["background_file"]
            )

        if fileParameter["ff_prefix"][0] != os.path.sep:
            fileParameter["ff_prefix"] = os.path.join(direc, fileParameter["ff_prefix"])

        #############################
        #####    angle offset   #####
        #############################
        if not ("ANGLE_OFFSET" in FT):
            fileParameter["angle_offset"] = 0.0

        #############################
        ##### correction spikes #####
        #############################
        if not ("CORRECT_SPIKES_THRESHOLD" in FT):
            fileParameter["correct_spikes_threshold"] = 0.0
        if not ("CCD_FILTER_PARA" in FT):
            fileParameter["ccd_filter_para"] = {}
        if not ("DO_CCD_FILTER" in FT):
            fileParameter["do_ccd_filter"] = "NO"

        if fileParameter["ccd_filter_para"] == "CCD_Filter":
            if "correct_spikes_threshold" not in fileParameter:
                fileParameter["do_ccd_filter_preference"] = "NO"
                fileParameter["ccd_filter_para"] = {
                    "threshold": fileParameter["correct_spikes_threshold_default"]
                }
            elif fileParameter["correct_spikes_threshold"].isinf():
                fileParameter["do_ccd_filter"] = "NO"
                fileParameter["ccd_filter_para"] = {
                    "threshold": fileParameter["correct_spikes_threshold_default"]
                }
            else:
                fileParameter["do_ccd_filter_preference"] = "YES"
                fileParameter["ccd_filter_para"] = {
                    "threshold": fileParameter["correct_spikes_threshold"]
                }
        else:
            fileParameter["do_ccd_filter_preference"] = "YES"

        if len(fileParameter["do_ccd_filter"]) == 0:
            fileParameter["do_ccd_filter"] = fileParameter["do_ccd_filter_preference"]

        # TODO for now we call several time the reconstructor but no dircet multiframe
        fileParameter["multiframe"] = 0

        ##########################
        ##### create parfile #####
        ##########################

        with open(par_file_path, "wb") as fidparfile:
            file_prefix = os.path.join(direc, prefix)
            if convert_path:
                file_prefix = PyHSTCaller._remove_lbs_head(file_prefix)

            if fileParameter["multiframe"]:
                file_prefix = file_prefix + ".edf"
            fileParameter["file_prefix"] = file_prefix

            # Remove directory head if necessary
            if convert_path:
                fileParameter["background_file"] = self._remove_lbs_head(
                    dirin=fileParameter["background_file"]
                )
                fileParameter["ff_prefix"] = self._remove_lbs_head(
                    dirin=fileParameter["ff_prefix"]
                )

            if "PAG_LENGTH" in recons_param["PAGANIN"]:
                fileParameter["pag_length"] = recons_param["PAGANIN"]["DB"]
            fidparfile.write(bytes("# pyHST_SLAVE PARAMETER FILE\n\n", "UTF-8"))
            fidparfile.write(
                bytes(
                    "# generated by tomwer - %s\n\n" % tomwer_version.version, "UTF-8"
                )
            )

            fidparfile.write(
                bytes("# Parameters defining the projection file series\n", "UTF-8")
            )
            fidparfile.write(
                bytes("MULTIFRAME = %d\n\n" % fileParameter["multiframe"], "UTF-8")
            )
            if hdf5_info is None:
                _file_prefix = fileParameter["file_prefix"]
            else:
                _file_prefix = os.path.relpath(hdf5_info.projections.file, scan.path)
            fidparfile.write(bytes("FILE_PREFIX = %s\n" % _file_prefix, "UTF-8"))
            if hdf5_info is not None:
                fidparfile.write(
                    bytes(
                        "PROJ_DS_NAME = %s\n" % hdf5_info.projections.dataset_path,
                        "UTF-8",
                    )
                )

            fidparfile.write(
                bytes(
                    "NUM_FIRST_IMAGE = %d # No. of first projection file\n"
                    % fileParameter["num_first_image"],
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes(
                    "NUM_LAST_IMAGE = %d # No. of last projection file\n"
                    % fileParameter["num_last_image"],
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes(
                    "NUMBER_LENGTH_VARIES = %s\n"
                    % fileParameter["number_length_varies"],
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes(
                    "LENGTH_OF_NUMERICAL_PART = %d # No. of characters\n"
                    % length_of_numerical_part,
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes("FILE_POSTFIX = %s\n" % fileParameter["file_postfix"], "UTF-8")
            )
            fidparfile.write(
                bytes(
                    "FILE_INTERVAL = %d # Interval between input files\n"
                    % fileParameter["file_interval"],
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes("\n# Parameters defining the projection file format\n", "UTF-8")
            )
            if num_image_1 is not None:
                fidparfile.write(
                    bytes(
                        "NUM_IMAGE_1 = %d # Number of pixels horizontally\n"
                        % num_image_1,
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "NUM_IMAGE_1 = ??? # Number of pixels horizontally\n", "UTF-8"
                    )
                )
            if num_image_2 is not None:
                fidparfile.write(
                    bytes(
                        "NUM_IMAGE_2 = %d # Number of pixels vertically\n"
                        % num_image_2,
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes("NUM_IMAGE_2 = ??? # Number of pixels vertically\n", "UTF-8")
                )
            if image_pixel_size is not None:
                fidparfile.write(
                    bytes(
                        "IMAGE_PIXEL_SIZE_1 = %f # Pixel size horizontally (microns)\n"
                        % image_pixel_size,
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "IMAGE_PIXEL_SIZE_1 = ??? # Pixel size horizontally (microns)\n",
                        "UTF-8",
                    )
                )
            if fileParameter["image_pixel_size_2"] is not None:
                fidparfile.write(
                    bytes(
                        "IMAGE_PIXEL_SIZE_2 = %f # Pixel size vertically\n"
                        % fileParameter["image_pixel_size_2"],
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes("IMAGE_PIXEL_SIZE_2 = ??? # Pixel size vertically\n", "UTF-8")
                )
            fidparfile.write(
                bytes("\n# Parameters defining background treatment\n", "UTF-8")
            )

            if fileParameter["correct"]:
                fidparfile.write(
                    bytes(
                        "SUBTRACT_BACKGROUND = %s # Subtract background from data\n"
                        % fileParameter["subtract_background"],
                        "UTF-8",
                    )
                )
                if hdf5_info is None:
                    fidparfile.write(
                        bytes(
                            "BACKGROUND_FILE = %s\n" % fileParameter["background_file"],
                            "UTF-8",
                        )
                    )
                elif hdf5_info.dark is not None:
                    fidparfile.write(
                        bytes(
                            "BACKGROUND_FILE = %s\n"
                            % os.path.relpath(hdf5_info.dark.file, scan.path),
                            "UTF-8",
                        )
                    )
                if hdf5_info is not None and hdf5_info.dark is not None:
                    fidparfile.write(
                        bytes(
                            "BACKGROUND_DS_NAME = %s\n" % hdf5_info.dark.dataset_path,
                            "UTF-8",
                        )
                    )
            else:
                fidparfile.write(
                    bytes(
                        "SUBTRACT_BACKGROUND = %s # No background subtraction\n"
                        % fileParameter["subtract_background"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes("BACKGROUND_FILE = %s\n" % not_available, "UTF-8")
                )

            fidparfile.write(
                bytes("\n# Parameters defining flat-field treatment\n", "UTF-8")
            )
            if fileParameter["correct"]:
                fidparfile.write(
                    bytes(
                        "CORRECT_FLATFIELD = %s # Divide by flat-field image\n"
                        % fileParameter["correct_flatfield"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes(
                        "FLATFIELD_CHANGING = %s # Series of flat-field files\n"
                        % fileParameter["flatfield_changing"],
                        "UTF-8",
                    )
                )
                if hdf5_info is None:
                    fidparfile.write(
                        bytes(
                            "FLATFIELD_FILE = %s\n"
                            % os.path.basename(fileParameter["flatfield_file"]),
                            "UTF-8",
                        )
                    )
                    fidparfile.write(
                        bytes("FF_PREFIX = %s\n" % fileParameter["ff_prefix"], "UTF-8")
                    )
                elif hdf5_info.flats is not None:
                    _ff_files = ", ".join(
                        [
                            '"{}"'.format(os.path.relpath(file_name, scan.path))
                            for file_name in hdf5_info.flats.files
                        ]
                    )
                    _ff_files = "[{}]".format(_ff_files)
                    fidparfile.write(bytes("FF_PREFIX = %s\n" % _ff_files, "UTF-8"))
                    fidparfile.write(
                        bytes(
                            "FF_DS_NAME = %s\n" % hdf5_info.flats.dataset_path, "UTF-8"
                        )
                    )

                fidparfile.write(
                    bytes(
                        "FF_NUM_FIRST_IMAGE = %d # No. of first flat-field file\n"
                        % fileParameter["ff_num_first_image"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes(
                        "FF_NUM_LAST_IMAGE = %d # No. of last flat-field file\n"
                        % fileParameter["ff_num_last_image"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes(
                        "FF_NUMBER_LENGTH_VARIES = %s\n"
                        % fileParameter["number_length_varies"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes(
                        "FF_LENGTH_OF_NUMERICAL_PART = %d # No. of characters\n"
                        % length_of_numerical_part,
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes("FF_POSTFIX = %s\n" % fileParameter["file_postfix"], "UTF-8")
                )
                if fileParameter["ff_file_interval"] is not None:
                    if hdf5_info is None:
                        fidparfile.write(
                            bytes(
                                "FF_FILE_INTERVAL = %d # Interval between flat-field files\n"
                                % fileParameter["ff_file_interval"],
                                "UTF-8",
                            )
                        )
                    elif hdf5_info.flats is not None:
                        # note: in the case of hdf5 we write at most 2 flat files
                        fidparfile.write(
                            bytes(
                                "FF_FILE_INTERVAL = %d # Interval between flat-field files\n"
                                % len(scan.projections),
                                "UTF-8",
                            )
                        )

                else:
                    fidparfile.write(
                        bytes(
                            "FF_FILE_INTERVAL = ??? # Interval between flat-field files\n",
                            "UTF-8",
                        )
                    )
            else:
                fidparfile.write(
                    bytes(
                        "CORRECT_FLATFIELD = %s # No flat-field correction\n"
                        % fileParameter["correct_flatfield"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes("FLATFIELD_CHANGING = %s\n" % not_available, "UTF-8")
                )
                fidparfile.write(
                    bytes("FLATFIELD_FILE = %s\n" % not_available, "UTF-8")
                )
                fidparfile.write(bytes("FF_PREFIX = %s\n" % not_available, "UTF-8"))
                fidparfile.write(
                    bytes("FF_NUM_FIRST_IMAGE = %s\n" % not_available, "UTF-8")
                )
                fidparfile.write(
                    bytes("FF_NUM_LAST_IMAGE = %s\n" % not_available, "UTF-8")
                )
                fidparfile.write(
                    bytes("FF_NUMBER_LENGTH_VARIES = %s\n" % not_available, "UTF-8")
                )
                fidparfile.write(
                    bytes("FF_LENGTH_OF_NUMERICAL_PART = %s\n" % not_available, "UTF-8")
                )
                fidparfile.write(bytes("FF_POSTFIX = %s\n" % not_available, "UTF-8"))
                fidparfile.write(
                    bytes("FF_FILE_INTERVAL = %s\n" % not_available, "UTF-8")
                )
            if recons_param["FT"]["DFFCORRECTION"]:
                fidparfile.write(
                    bytes(
                        "DOUBLEFFCORRECTION = 1 # Apply double flat field correction\n",
                        "UTF-8",
                    )
                )
                sigma_2 = recons_param["FT"]["DFF_SIGMA"]
                fidparfile.write(
                    bytes(
                        "FF2_SIGMA = %s # double flat field high-pass filter\n"
                        % sigma_2,
                        "UTF-8",
                    )
                )

            fidparfile.write(
                bytes(
                    "\nTAKE_LOGARITHM = %s # Take log of projection values\n"
                    % fileParameter["take_logarithm"],
                    "UTF-8",
                )
            )
            if not (fileParameter["doubleffcorrection"] == []):
                fidparfile.write(
                    bytes(
                        'DOUBLEFFCORRECTION = "filtered_mean.edf" # double flatfield\n',
                        "UTF-8",
                    )
                )

            fidparfile.write(bytes("\n# Parameters defining experiment\n", "UTF-8"))
            fidparfile.write(
                bytes(
                    "ANGLE_BETWEEN_PROJECTIONS = %f # Increment angle in degrees\n"
                    % fileParameter["angle_between_projections"],
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes(
                    "ROTATION_VERTICAL = %s\n" % fileParameter["rotation_vertical"],
                    "UTF-8",
                )
            )
            if fileParameter["rotation_axis_position"] is not None:
                fidparfile.write(
                    bytes(
                        "ROTATION_AXIS_POSITION = %f # Position in pixels\n"
                        % fileParameter["rotation_axis_position"],
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "ROTATION_AXIS_POSITION = ??? # Position in pixels\n", "UTF-8"
                    )
                )
            fidparfile.write(bytes("\n# Parameters defining reconstruction\n", "UTF-8"))
            fidparfile.write(
                bytes(
                    "OUTPUT_SINOGRAMS = %s # Output sinograms to files or not\n"
                    % fileParameter["output_sinograms"],
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes(
                    "OUTPUT_RECONSTRUCTION = %s # Reconstruct and save or not\n"
                    % fileParameter["output_reconstruction"],
                    "UTF-8",
                )
            )
            if fileParameter["start_voxel_1"] is not None:
                fidparfile.write(
                    bytes(
                        "START_VOXEL_1 =   %4d # X-start of reconstruction volume\n"
                        % fileParameter["start_voxel_1"],
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "START_VOXEL_1 =   ??? # X-start of reconstruction volume\n",
                        "UTF-8",
                    )
                )
            if fileParameter["start_voxel_2"] is not None:
                fidparfile.write(
                    bytes(
                        "START_VOXEL_2 =   %4d # Y-start of reconstruction volume\n"
                        % fileParameter["start_voxel_2"],
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "START_VOXEL_2 =   ??? # Y-start of reconstruction volume\n",
                        "UTF-8",
                    )
                )
            if fileParameter["start_voxel_3"] is not None:
                fidparfile.write(
                    bytes(
                        "START_VOXEL_3 =   %4d # Z-start of reconstruction volume\n"
                        % fileParameter["start_voxel_3"],
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "START_VOXEL_3 =   ??? # Z-start of reconstruction volume\n",
                        "UTF-8",
                    )
                )
            if fileParameter["end_voxel_1"] is not None:
                fidparfile.write(
                    bytes(
                        "END_VOXEL_1 =   %4d # X- of reconstruction volume\n"
                        % fileParameter["end_voxel_1"],
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "END_VOXEL_1 =   %4d # X- of reconstruction volume\n", "UTF-8"
                    )
                )
            if fileParameter["end_voxel_2"] is not None:
                fidparfile.write(
                    bytes(
                        "END_VOXEL_2 =   %4d # Y- of reconstruction volume\n"
                        % fileParameter["end_voxel_2"],
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "END_VOXEL_2 =   ??? # Y- of reconstruction volume\n", "UTF-8"
                    )
                )
            if fileParameter["end_voxel_3"] is not None:
                fidparfile.write(
                    bytes(
                        "END_VOXEL_3 =   %4d # Z- of reconstruction volume\n"
                        % fileParameter["end_voxel_3"],
                        "UTF-8",
                    )
                )
            else:
                fidparfile.write(
                    bytes(
                        "END_VOXEL_3 =   ??? # Z- of reconstruction volume\n", "UTF-8"
                    )
                )
            fidparfile.write(
                bytes(
                    "OVERSAMPLING_FACTOR = %d # 0 = Linear, 1 = Nearest pixel\n"
                    % fileParameter["oversampling_factor"],
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes(
                    "ANGLE_OFFSET = %f # Reconstruction rotation offset angle in degrees\n"
                    % recons_param["FT"]["ANGLE_OFFSET_VALUE"],
                    "UTF-8",
                )
            )

            # adding extra features for PyHST
            fidparfile.write(bytes("\n# Parameters extra features PyHST\n", "UTF-8"))
            fidparfile.write(
                bytes(
                    "DO_CCD_FILTER = %s # CCD filter (spikes)\n"
                    % fileParameter["do_ccd_filter"],
                    "UTF-8",
                )
            )
            fidparfile.write(
                bytes('CCD_FILTER = "%s"\n' % fileParameter["ccd_filter"], "UTF-8")
            )
            assert isinstance(fileParameter["ccd_filter_para"], dict)
            fidparfile.write(
                bytes(
                    "CCD_FILTER_PARA = %s\n" % fileParameter["ccd_filter_para"], "UTF-8"
                )
            )
            fidparfile.write(
                bytes(
                    "DO_SINO_FILTER = %s # Sinogram filter (rings)\n"
                    % fileParameter["do_sino_filter"],
                    "UTF-8",
                )
            )
            fidparfile.write(bytes('SINO_FILTER = "%s"\n' % "SINO_Filter", "UTF-8"))
            if num_image_1 is not None:
                fidparfile.write(
                    bytes("ar = Numeric.ones(%d,'f')\n" % num_image_1, "UTF-8")
                )
            fidparfile.write(bytes("ar[0]=0.0\n", "UTF-8"))

            if fileParameter["correct_rings_nb"] > 0:
                fidparfile.write(
                    bytes(
                        "ar[2:%d]=0.0\n" % 2 * (fileParameter["correct_rings_nb"] + 1),
                        "UTF-8",
                    )
                )

            fidparfile.write(bytes('SINO_FILTER_PARA = {"FILTER": ar }\n', "UTF-8"))

            # correct_file should include one correction per projection.
            # for now no relation with axis center of rotation

            # if correct_file is None:
            do_axis_correction = recons_param["FTAXIS"]["DO_AXIS_CORRECTION"]
            # WARNING: For now axis correction is not handled
            do_axis_correction = False
            if do_axis_correction in (True, "YES", 1, "1"):
                do_axis_correction = "YES"
            else:
                do_axis_correction = "NO"
            fidparfile.write(
                bytes(
                    "DO_AXIS_CORRECTION = {} # Axis correction\n"
                    "".format(do_axis_correction),
                    "UTF-8",
                )
            )
            correct_file = "correct.txt"
            if do_axis_correction and os.path.exists(
                os.path.join(scan.path, correct_file)
            ):
                fidparfile.write(
                    bytes("AXIS_CORRECTION_FILE = %s\n" % correct_file, "UTF-8")
                )

            fidparfile.write(
                bytes(
                    "OPTIONS= { 'padding':'%s', 'axis_to_the_center':'%s', "
                    "'avoidhalftomo':'%s'} # Padding and position axis\n"
                    ""
                    % (
                        fileParameter["padding"],
                        fileParameter["axis_to_the_center"],
                        fileParameter["avoidhalftomo"],
                    ),
                    "UTF-8",
                )
            )
            # fidparfile.write('NSLICESATONCE=200  # limiting the number of slices at once to not crash the memory \n')

            if paganin is not PaganinMode.off:
                fidparfile.write(
                    bytes("\n# Parameters for Paganin reconstruction\n", "UTF-8")
                )
                fidparfile.write(
                    bytes(
                        "# delta over beta ratio for Paganin phase retrieval = %1.2f \n"
                        % PAG["DB"],
                        "UTF-8",
                    )
                )
                fidparfile.write(bytes("DO_PAGANIN = 1 \n", "UTF-8"))
                fidparfile.write(
                    bytes("PAGANIN_Lmicron = %f \n" % float(PAG["DB"]), "UTF-8")
                )

                if fileParameter["start_voxel_3"] == fileParameter["end_voxel_3"]:
                    # disp('file for reconstruction of a single slice, I reduce the part of the picture taken into account for the phase retrieval for faster processing')
                    fidparfile.write(bytes("PAGANIN_MARGE = 50 \n", "UTF-8"))
                else:
                    # disp('preparation for a full reconstruction of the volume, the whole picture will be used for the phase retrieval process to ensure final quality and accuracy')
                    fidparfile.write(bytes("PAGANIN_MARGE = 200 \n", "UTF-8"))

                fidparfile.write(bytes("DO_OUTPUT_PAGANIN = 0 \n", "UTF-8"))
                fidparfile.write(bytes("OUTPUT_PAGANIN_FILE = paga_cufft \n", "UTF-8"))
                fidparfile.write(bytes("PAGANIN_TRY_CUFFT = 1 \n", "UTF-8"))
                fidparfile.write(bytes("PAGANIN_TRY_FFTW = 1 \n", "UTF-8"))

                if fileParameter["do_unsharp"] == 1:
                    fidparfile.write(
                        bytes(
                            "\n# Parameters for unsharp masking on the radiographs\n",
                            "UTF-8",
                        )
                    )
                    fidparfile.write(bytes("UNSHARP_LOG = 1 \n", "UTF-8"))
                    fidparfile.write(
                        bytes(
                            "PUS = %f \n" % recons_param["PAGANIN"]["UNSHARP_SIGMA"],
                            "UTF-8",
                        )
                    )
                    fidparfile.write(
                        bytes(
                            "PUC = %f \n" % recons_param["PAGANIN"]["UNSHARP_COEFF"],
                            "UTF-8",
                        )
                    )

            if paganin is PaganinMode.multi:
                fidparfile.write(bytes("\n# Multi_paganin\n", "UTF-8"))
                fidparfile.write(
                    bytes(
                        "# 2nd delta over beta ratio for multi Paganin phase retrieval = %1.2f \n"
                        % PAG["DB2"],
                        "UTF-8",
                    )
                )
                fidparfile.write(bytes("MULTI_PAGANIN_PARS={}\n", "UTF-8"))
                # TODO: check the paganin values
                # I don't know what lmicron is related to
                fidparfile.write(
                    bytes(
                        'MULTI_PAGANIN_PARS["BONE_Lmicron"]= %f \n' % PAG["DB2"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes(
                        'MULTI_PAGANIN_PARS["THRESHOLD"]= %1.3f\n' % PAG["THRESHOLD"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes(
                        'MULTI_PAGANIN_PARS["DILATE"]= %1.0f\n' % PAG["DILATE"], "UTF-8"
                    )
                )
                fidparfile.write(
                    bytes(
                        'MULTI_PAGANIN_PARS["MEDIANR"]= %1.0f\n'
                        % recons_param["PAGANIN"]["MEDIANR"],
                        "UTF-8",
                    )
                )

                if fileParameter["multipag_keep_bone"] == 1:
                    fidparfile.write(
                        bytes(
                            'MULTI_PAGANIN_PARS["PAGBONE_FILE"] = "%s"\n'
                            % fileParameter["output_file_bone"],
                            "UTF-8",
                        )
                    )
                if fileParameter["multipag_keep_mask"] == 1:
                    fidparfile.write(
                        bytes(
                            'MULTI_PAGANIN_PARS["MASKBONE_FILE"] = "%s"\n'
                            % fileParameter["output_file_mask"],
                            "UTF-8",
                        )
                    )
                if fileParameter["multipag_keep_abs"] == 1:
                    fidparfile.write(
                        bytes(
                            'MULTI_PAGANIN_PARS["ABSBONE_FILE"] = "%s"\n'
                            % fileParameter["output_file_abs"],
                            "UTF-8",
                        )
                    )
                if fileParameter["multipag_keep_corr"] == 1:
                    fidparfile.write(
                        bytes(
                            'MULTI_PAGANIN_PARS["CORRBONE_FILE"] = "%s"\n'
                            % fileParameter["output_file_corr"],
                            "UTF-8",
                        )
                    )
                if fileParameter["multipag_keep_soft"] == 1:
                    fidparfile.write(
                        bytes(
                            'MULTI_PAGANIN_PARS["CORRECTEDVOL_FILE"] = "%s"\n'
                            % fileParameter["output_file_soft"],
                            "UTF-8",
                        )
                    )

            if fileParameter["half_acquisition"] == 1:
                fidparfile.write(bytes("PENTEZONE=300\n", "UTF-8"))

            if FT["ZEROOFFMASK"] == 0:
                fidparfile.write(bytes("ZEROOFFMASK=0\n", "UTF-8"))

            ########################## addings for version 2 of Pyhst ################################

            fidparfile.write(
                bytes("TRYEDFCONSTANTHEADER=%d \n" % (1 - FT["FIXHD"]), "UTF-8")
            )

            ##########################################################################################

            if "zeroclipvalue" not in fileParameter:
                fidparfile.write(
                    bytes(
                        "ZEROCLIPVALUE = %g # Minimum value of radiographs after flat / before log\n"
                        % fileParameter["zeroclipvalue"],
                        "UTF-8",
                    )
                )

            if "oneclipvalue" not in fileParameter:
                fidparfile.write(
                    bytes(
                        "ONECLIPVALUE = %g # Maximum value of radiographs after flat / before log\n"
                        % fileParameter["oneclipvalue"],
                        "UTF-8",
                    )
                )

            if fileParameter["do_projection_median"] == "YES":
                fidparfile.write(
                    bytes(
                        "DO_PROJECTION_MEDIAN = %s # Calculate median of all projections\n"
                        % fileParameter["do_projection_median"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes(
                        'PROJECTION_MEDIAN_FILENAME = "%s" # Name output file median calculation\n'
                        % fileParameter["projection_median_filename"],
                        "UTF-8",
                    )
                )

            if fileParameter["do_projection_mean"] == "YES":
                fidparfile.write(
                    bytes(
                        "DO_PROJECTION_MEAN = %s # Calculate median of all projections\n"
                        % fileParameter["do_projection_mean"],
                        "UTF-8",
                    )
                )
                fidparfile.write(
                    bytes(
                        'PROJECTION_MEDIAN_FILENAME = "%s" # Name output file mean calculation\n'
                        % fileParameter["projection_mean_filename"],
                        "UTF-8",
                    )
                )

            fidparfile.write(
                bytes("\n# Parameters defining output file / format\n", "UTF-8")
            )
            fidparfile.write(
                bytes("OUTPUT_FILE = %s\n" % fileParameter["output_file"], "UTF-8")
            )

            fidparfile.write(bytes("\n# Reconstruction program options\n", "UTF-8"))
            # old legacy, not needed by pyhst2
            # fidparfile.write(
            #     bytes('DISPLAY_GRAPHICS = %s # No images\n' % fileParameter['display_graphics'],
            #           'UTF-8'))

            if fileParameter["ft_jp2"] == 1:
                fidparfile.write(bytes("\n#JP2000\n", "UTF-8"))
                fidparfile.write(bytes('JP2EDF_DIR = "/tmp/jp2/" \n', "UTF-8"))
                fidparfile.write(bytes("JP2EDF_REMOVE = 1 \n", "UTF-8"))

            ##########CONICAL AND FAN BEAM RECONSTRUCTION############################################

            if BG["TYPE"] == "c":
                fidparfile.write(
                    bytes("\n# Conical and Fan beam reconstruction\n", "UTF-8")
                )
                fidparfile.write(bytes("CONICITY = 1\n", "UTF-8"))
                fidparfile.write(bytes("CONICITY_FAN = 0\n", "UTF-8"))
                fidparfile.write(
                    bytes("SOURCE_X = %f\n" % fileParameter["source_x"], "UTF-8")
                )
                fidparfile.write(
                    bytes("SOURCE_Y = %f\n" % fileParameter["source_y"], "UTF-8")
                )
                fidparfile.write(
                    bytes(
                        "SOURCE_DISTANCE = %f\n" % fileParameter["source_distance"],
                        "UTF-8",
                    )
                )

            if BG["TYPE"] == "f":
                fidparfile.write(
                    bytes("\n# Conical and Fan beam reconstruction\n", "UTF-8")
                )
                fidparfile.write(bytes("CONICITY = 0\n", "UTF-8"))
                fidparfile.write(bytes("CONICITY_FAN = 1\n", "UTF-8"))
                fidparfile.write(
                    bytes("SOURCE_X = %f\n" % fileParameter["source_x"], "UTF-8")
                )
                fidparfile.write(
                    bytes("SOURCE_Y = %f\n" % fileParameter["source_y"], "UTF-8")
                )
                fidparfile.write(
                    bytes(
                        "SOURCE_DISTANCE = %f\n" % fileParameter["source_distance"],
                        "UTF-8",
                    )
                )

        return par_file_path

    @staticmethod
    def make_rec_file(rec_file, par_file, recons_params):
        """
        Function creating the .rec file

        :param rec_file: name of the output file
        :type: str
        :param recons_params: reconstruction parameters as dict
        :type: dict
        """

        def loadFileInfoFrmPar(filePath):
            info = "Reading %s to get reconstruction parameters"
            logger.info(info)
            ofile = open(filePath, "r")
            lines = ofile.readlines()
            outputFile = None
            filePrefix = None
            for line in lines:
                line_str = str(line)
                if "OUTPUT_FILE" in line_str:
                    splitLine = line_str.replace(" ", "").split("=")
                    outputFile = splitLine[1].rstrip("\n")
                    logger.info("Found OUTPUT_FILE: %s" % outputFile)

                if "FILE_PREFIX" in line_str:
                    splitLine = line_str.replace(" ", "").split("=")
                    filePrefix = splitLine[1].rstrip("\n")
                    logger.info("Found FILE_PREFIX: %s" % filePrefix)
            ofile.close()
            return outputFile, filePrefix

        test = recons_params["FT"]

        vol_output = test["VOLOUTFILE"]

        ### Get useful parameter
        if os.path.isfile(par_file):
            recFile, prefix = loadFileInfoFrmPar(par_file)
        else:
            err = "No %s file found. Can't deduce reconstruction parameters." % par_file
            raise ValueError(err)

        if recFile is None or prefix is None:
            raise IOError(
                "Failed to load parameters `OUTPUT_FILE` and/or "
                "`FILE_PREFIX` in the reconstruction parameters file"
            )

        ### Get the prefix for .rec name file
        ### prefix : only name of file without extension
        ### prefix_full : name and directory of file without extension
        basename1 = os.path.basename(prefix)
        logger.info("prefix is %s" % basename1)
        prefix_full = par_file[0:-4]
        logger.info("prefix is %s" % prefix_full)
        if prefix_full[-3:] == "pag":
            prefix = prefix_full[0:-3]
        else:
            prefix = prefix_full

        # Get parameter for writing the script
        # utilsMakeOAR = recons_params['PYHSTEXE']['MAKE_OAR_FILE']
        # For now hard coded
        utilsMakeOAR = settings.MAKE_OAR_PYST2_PATH

        logger.info(("Processing the file %s %s" % (prefix_full, prefix)))

        # Writing the script file
        with open(rec_file, "wb") as fidshell:
            fidshell.write(bytes("#!/bin/bash\n", "UTF-8"))
            fidshell.write(
                bytes('GET_OS="/csadmin/common/scripts/get_os.share"\n', "UTF-8")
            )
            fidshell.write(bytes("os=`$GET_OS`\n", "UTF-8"))
            fidshell.write(
                bytes(
                    "export PYHST="
                    + _getPyHSTDir()
                    + recons_params["PYHSTEXE"]["EXE"]
                    + "\n",
                    "UTF-8",
                )
            )
            fidshell.write(bytes('case "${os}" in\n', "UTF-8"))
            fidshell.write(bytes("    centos*)\n", "UTF-8"))
            if vol_output == 0:
                fidshell.write(
                    bytes("      mkdir " + os.path.dirname(recFile) + " \n", "UTF-8")
                )
                fidshell.write(
                    bytes(
                        "      chmod 775 " + os.path.dirname(recFile) + " \n", "UTF-8"
                    )
                )

            fidshell.write(
                bytes(
                    "        "
                    + str(utilsMakeOAR)
                    + " "
                    + os.path.basename(prefix_full)
                    + " 1\n",
                    "UTF-8",
                )
            )

            fidshell.write(
                bytes(
                    "        oarsub -q gpu  -S ./"
                    + os.path.basename(prefix_full)
                    + ".oar\n",
                    "UTF-8",
                )
            )

            fidshell.write(bytes("        ;;\n", "UTF-8"))
            fidshell.write(bytes("    debian*)\n", "UTF-8"))
            if vol_output == 0:
                fidshell.write(
                    bytes("      mkdir " + os.path.dirname(recFile) + " \n", "UTF-8")
                )

            fidshell.write(
                bytes(
                    "        "
                    + str(utilsMakeOAR)
                    + " "
                    + os.path.basename(prefix_full)
                    + " 1\n",
                    "UTF-8",
                )
            )
            fidshell.write(
                bytes(
                    "        oarsub -q gpu -S ./"
                    + os.path.basename(prefix_full)
                    + ".oar\n",
                    "UTF-8",
                )
            )

            fidshell.write(bytes("        ;;\n", "UTF-8"))
            fidshell.write(bytes("    *)\n", "UTF-8"))
            fidshell.write(bytes("esac\n", "UTF-8"))

        os.chmod(rec_file, 0o777)
        return

    @staticmethod
    def _loadDefaultPar(
        recons_param,
        out_base_file_name,
        direc,
        image_pixel_size,
        corr,
        nvue,
        refon,
        num_image_1,
        num_image_2,
        slice,
        convert_lbsram,
        cor,
        scan_range,
    ):
        assert type(recons_param) is dict
        assert out_base_file_name is not None
        # TODO: default params should not be necessary and should be removed
        defaultParams = {}
        FT = recons_param["FT"]
        PG = PAG = recons_param["PAGANIN"]
        BG = recons_param["BEAMGEO"]
        paganin = PaganinMode.from_value(PAG["MODE"])

        defaultParams["half_acquisition"] = FT["HALF_ACQ"]

        if PAG["UNSHARP_SIGMA"] != 0:
            defaultParams["do_unsharp"] = 1
        else:
            defaultParams["do_unsharp"] = 0

        defaultParams["correct_spikes_threshold_default"] = 0.04
        defaultParams["status"] = 1
        defaultParams["parfilename"] = out_base_file_name + ".par"

        defaultParams["num_first_image"] = 0
        defaultParams["num_last_image"] = recons_param["FT"]["NUM_LAST_IMAGE"] - 1
        defaultParams["angle_offset"] = 0

        defaultParams["number_length_varies"] = "NO"
        defaultParams["file_postfix"] = ".edf"
        defaultParams["image_pixel_size_1"] = defaultParams[
            "image_pixel_size_2"
        ] = image_pixel_size
        defaultParams["file_interval"] = 1
        defaultParams["subtract_background"] = defaultParams[
            "correct_flatfield"
        ] = corr  # = take_logarithm
        defaultParams["take_logarithm"] = "YES"
        defaultParams["correct"] = corr == "YES"
        defaultParams["background_file"] = os.path.join(direc, "dark.edf")
        defaultParams["ff_prefix"] = os.path.join(direc, "refHST")
        defaultParams["flatfield_file"] = defaultParams["ff_prefix"] + "0000.edf"
        defaultParams["ff_num_first_image"] = 0
        defaultParams["ff_num_last_image"] = nvue
        defaultParams["ff_file_interval"] = refon

        if defaultParams["ff_file_interval"] == 0:
            defaultParams["flatfield_changing"] = "NO"
        else:
            defaultParams["flatfield_changing"] = "YES"

        defaultParams["doubleffcorrection"] = []
        defaultParams["zeroclipvalue"] = 0.001
        defaultParams["oneclipvalue"] = []
        defaultParams["multiframe"] = 0
        defaultParams["angle_between_projections"] = (
            scan_range / nvue if nvue != 0 else 0
        )
        defaultParams["horaxis"] = 0
        defaultParams["output_sinograms"] = "NO"
        defaultParams["output_reconstruction"] = "YES"
        defaultParams["start_voxel_1"] = defaultParams["start_voxel_2"] = 1
        if slice is None:
            defaultParams["start_voxel_3"] = 1
        else:
            defaultParams["start_voxel_3"] = (
                slice + 1
            )  # VOXEL start at 1 in pyhst, 0 in tomwer
        defaultParams["end_voxel_1"] = defaultParams["end_voxel_2"] = num_image_1
        if recons_param["FT"]["HALF_ACQ"]:
            if cor is None:
                cor = num_image_1 // 2
            defaultParams["end_voxel_1"] = defaultParams[
                "end_voxel_2"
            ] = num_image_1 + abs(2.0 * cor)
        if slice is None:
            defaultParams["end_voxel_3"] = num_image_2
        else:
            defaultParams["end_voxel_3"] = (
                slice + 1
            )  # VOXEL start at 1 in pyhst, 0 in tomwer
        defaultParams["oversampling_factor"] = 4

        defaultParams["ccd_filter"] = "CCD_Filter"

        # correction rings
        if FT["RINGSCORRECTION"]:
            defaultParams["do_sino_filter"] = "YES"
        else:
            defaultParams["do_sino_filter"] = "NO"

        defaultParams[
            "correct_rings_nb"
        ] = 2  # number of elements (|f|>0) that will not be filtered from sinograms
        defaultParams["sino_filter"] = "SINO_Filter"

        # padding at edges 'E' edge values or '0'
        defaultParams["padding"] = "E"
        # move axis to the center 'Y' or not 'N'
        defaultParams["axis_to_the_center"] = "Y"
        defaultParams["do_projection_median"] = "NO"
        defaultParams["projection_median_filename"] = "median.edf"
        defaultParams["do_projection_mean"] = "NO"
        defaultParams["projection_mean_filename"] = "mean.edf"
        # defaultParams['display_graphics'] = 'NO'

        if (BG["TYPE"] == "c") or (BG["TYPE"] == "f"):
            defaultParams["source_x"] = BG["SX"]
            defaultParams["source_y"] = BG["SY"]
            defaultParams["source_distance"] = BG["DIST"]
        else:
            defaultParams["source_x"] = 0
            defaultParams["source_y"] = 0
            defaultParams["source_distance"] = 0

        valJP2 = FT["JP2"] if "JP2" in FT else 0
        defaultParams["ft_jp2"] = valJP2

        if FT["VOLOUTFILE"] == 1:
            output_file_ext = ".vol"
        else:
            output_file_ext = ".edf"
        if paganin is PaganinMode.off:
            defaultParams["output_file"] = os.path.join(direc, out_base_file_name)
        elif paganin in (PaganinMode.on, PaganinMode.both):
            # TODO: those are missing, I don't know how to compute them
            defaultParams["pag_length"] = 500.0
            defaultParams["output_file"] = os.path.join(direc, out_base_file_name)
        elif paganin is PaganinMode.multi:
            defaultParams["output_file"] = os.path.join(direc, out_base_file_name)
            defaultParams["ft_pag_db2"] = PG["DB2"]
            defaultParams["ft_pag_threshold"] = PG["THRESHOLD"]
            defaultParams["ft_pag_dilate"] = PG["DILATE"]
            defaultParams["ft_pag_medianr"] = PG["MEDIANR"]
            defaultParams["multipag_keep_bone"] = PG["MKEEP_BONE"]
            defaultParams["multipag_keep_soft"] = PG["MKEEP_SOFT"]
            defaultParams["multipag_keep_abs"] = PG["MKEEP_ABS"]
            defaultParams["multipag_keep_corr"] = PG["MKEEP_CORR"]
            defaultParams["multipag_keep_mask"] = PG["MKEEP_MASK"]
            # probleme a regler
            defaultParams["multipag_extra_files"] = (
                defaultParams["multipag_keep_bone"] == 1
                or defaultParams["multipag_keep_soft"] == 1
                or defaultParams["multipag_keep_mask"] == 1
                or defaultParams["multipag_keep_abs"] == 1
                or defaultParams["multipag_keep_corr"] == 1
            )
            defaultParams["output_file_bone"] = os.path.join(
                direc, out_base_file_name + "multipag_bone" + output_file_ext
            )
            defaultParams["output_file_soft"] = os.path.join(
                direc, out_base_file_name + "multipag_soft" + output_file_ext
            )
            defaultParams["output_file_abs"] = os.path.join(
                direc, out_base_file_name + "multipag_abs" + output_file_ext
            )
            defaultParams["output_file_corr"] = os.path.join(
                direc, out_base_file_name + "multipag_corr" + output_file_ext
            )
            defaultParams["output_file_mask"] = os.path.join(
                direc, out_base_file_name + "multipag_mask" + output_file_ext
            )
        else:
            raise ValueError("Paganin mode not recognized")

        # if necessary convert lbsram path to destination path
        keys_defining_path = (
            "output_file",
            "background_file",
            "ff_prefix",
            "flatfield_file",
            "output_file_bone",
            "output_file_soft",
            "output_file_abs",
            "output_file_corr",
            "output_file_mask",
        )
        if convert_lbsram:
            for key in keys_defining_path:
                if key in defaultParams:
                    value = defaultParams[key]
                    defaultParams[key] = PyHSTCaller._remove_lbs_head(dirin=value)

        return defaultParams

    @staticmethod
    def _remove_lbs_head(dirin):
        if dirin.startswith(get_lbsram_path()):
            return dirin.replace(get_lbsram_path(), get_dest_path(), 1)
        else:
            return dirin
