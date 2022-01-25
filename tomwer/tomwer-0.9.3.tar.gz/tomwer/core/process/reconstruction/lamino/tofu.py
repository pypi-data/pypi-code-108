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
__date__ = "01/06/2018"


import glob
import os
import subprocess
import sys
import enum
from collections import OrderedDict
import tempfile
import shutil
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.process.task import Task
from tomwer.core.process.reconstruction.darkref.settings import (
    DARKHST_PREFIX,
    REFHST_PREFIX,
)
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.utils import getDim1Dim2
from tomwer.core.utils.char import PSI_CHAR
import tomwer.version

import logging

logger = logging.getLogger(__name__)


@enum.unique
class FFCWhen(enum.Enum):
    on_the_fly = 0
    preprocessing = 1


SLICE_STACK_TYPE = "slice stack"
ROTATION_CENTER_TYPE = "rotation center"
LAMINO_ANGLE_TYPE = "lamino angle"
PSI_ANGLE_TYPE = " ".join((PSI_CHAR, "angle"))

SCAN_TYPES = OrderedDict(
    (
        (SLICE_STACK_TYPE, "z"),
        (ROTATION_CENTER_TYPE, "center-position-x"),
        (LAMINO_ANGLE_TYPE, "axis-angle-x"),
        (PSI_ANGLE_TYPE, "axis-angle-y"),
    )
)

SCAN_TYPES_I = {}
for s_type, value in SCAN_TYPES.items():
    SCAN_TYPES_I[value] = s_type


def _retrieve_opts_recons_cmd(scan_id, recons_param, additional_opts, pre_proc_ffc):
    """Return the options command under the style '--name optValue' from the
    ToFuReconstructionParam and a string of additional options

    :param bool pre_proc_ffc: should we apply flat field correction on the fly
                              or is it already done.
    """
    assert isinstance(recons_param, dict)
    options = [""]
    # deal with option that will can be None
    for opt in (
        "retry-timeout",
        "retries",
        "reduction-mode",
        "dark-scale",
        "darks",
        "slices-per-device",
        "slice-memory-coeff",
        "number",
        "volume-angle-x",
        "volume-angle-y",
        "volume-angle-z",
        "output",
        "center-position-x",
        "center-position-z",
        "axis-angle-x",
        "axis-angle-y",
        "z-parameter",
        "retrieval-method",
        "energy",
        "pixel-size",
        "propagation-distance",
        "regularization-rate",
        "thresholding-rate",
        "flats",
        "flats2",
        "z",
    ):
        if recons_param[opt] is not None:
            # special case for option that can contain Unix filename pattern matching (*)
            if opt in ("darks", "flats", "flats2", "dark-scale"):
                if pre_proc_ffc is True:
                    # in this case flat field correction has already been run
                    pass
                else:
                    options = options + [
                        " ".join([opt, '"' + str(recons_param[opt]) + '"'])
                    ]
            else:
                options = options + [" ".join([opt, str(recons_param[opt])])]

    # deal with specific case of the scan
    if "projections" in recons_param:
        options = options + [recons_param["projections"]]
    elif scan_id is not None:
        concert_radio_path = os.path.join(scan_id, "radios")
        proj_file_fn = concert_radio_path + os.sep + "frame_*.tif"
        if os.path.exists(concert_radio_path) and len(glob.glob(proj_file_fn)) > 0:
            options = options + ['projections "' + proj_file_fn + '"']
        else:
            options = options + [
                'projections "'
                + scan_id
                + os.sep
                + os.path.basename(scan_id)
                + '*.edf"'
            ]

    # deal with region
    assert "region" in recons_param
    if recons_param["region"] is not None:
        assert type(recons_param["region"]) in (list, tuple)
        assert len(recons_param["region"]) == 3
        options = options + ["region=%s,%s,%s" % recons_param["region"]]

    # deal with overallangle wich need a '-' for avoid staring by a numerical
    assert type(recons_param["overall-angle"]) is float
    options = options + ["overall-angle " + str(-1.0 * recons_param["overall-angle"])]

    # deal with x and y region
    for region in ("x-region", "y-region"):
        value = recons_param[region]
        if value is not None:
            value = str(value).replace(" ", "")
            value = value.lstrip("(").rstrip(")")
            options = options + ["=".join((region, value))]

    # deal with option that will be defined only if set to true
    for opt in ("verbose", "dry-run", "absorptivity"):
        assert opt in recons_param
        if recons_param[opt] is True:
            options.append(opt)

    return " --".join(options) + " " + additional_opts


# TODO: additional opts should be specific to flat field correction.
# reconstruction and ffc additional options should be separated
def _retrieve_opts_ffc_cmd(scan, recons_param, additional_opts, output):
    """Return the options command under the style '--name optValue' from the
    ToFuReconstructionParam and a string of additional options

    :param str output: output directory
    """
    assert isinstance(scan, TomwerScanBase)
    options = [""]

    options = options + [" ".join(["output", output])]

    # deal with option that will can be None
    for opt in (
        "retry-timeout",
        "retries",
        "reduction-mode",
        "dark-scale",
        "darks",
        "number",
        "center-position-x",
        "center-position-z",
        "axis-angle-x",
        "retrieval-method",
        "energy",
        "pixel-size",
        "propagation-distance",
        "regularization-rate",
        "thresholding-rate",
        "flats",
        "flats2",
    ):
        if recons_param[opt] is not None:
            # special case for option that can contain Unix filename pattern matching (*)
            if opt in ("darks", "flats", "flats2"):
                options = options + [
                    " ".join([opt, '"' + str(recons_param[opt] + '"')])
                ]
            else:
                options = options + [" ".join([opt, str(recons_param[opt])])]

    # deal with specific case of the scanID
    if scan.path is not None:
        options = options + [_get_projection_file_pattern(scan_path=scan.path)]

    # deal with option that will be defined only if set to true
    for opt in ("verbose", "dry-run", "absorptivity"):
        assert opt in recons_param
        # absorptivity should only be done in reconstruction
        if opt == "absorptivity":
            continue
        if recons_param[opt] is True:
            options.append(opt)

    return " --".join(options) + " " + additional_opts


def _get_projection_file_pattern(scan_path, ffc_folder=None):
    """

    :param scan_path: original scan path
    :param ffc_folder: folder containing the preprocessed flat field corrected
                       image
    :return: projection + name of the scan path
    """
    assert type(scan_path) is str
    if ffc_folder is None:
        root_folder = scan_path
    else:
        root_folder = ffc_folder
    assert root_folder is not None
    concert_radio_path = os.path.join(root_folder, "radios")
    proj_file_fn = concert_radio_path + os.sep + "frame_*.tif"
    if os.path.exists(concert_radio_path) and len(glob.glob(proj_file_fn)) > 0:
        return 'projections "' + proj_file_fn + '"'
    else:
        return (
            'projections "'
            + root_folder
            + os.sep
            + os.path.basename(scan_path)
            + '*.edf"'
        )


def _tofu_lamino_reconstruction(
    scan_id,
    recons_param,
    additional_options,
    delete_existing,
    exec_cmd=True,
    pre_proc_ffc=True,
):
    """Process a reconstruction for lamino using tofu

    :param str scan_id: path of the scan to reconstruct
    :param dict recons_param: parameters for the reconstruction
    :param str additional_options: additional options to be add at the tofu reco
                                  call.
    :param bool delete_existing: if True then remove output dir if given
    :param bool exec_cmd: if True, will run reconstruction, otherwise will only
                          display the reconstruction parameters.
    :param bool pre_proc_ffc: should we apply flat field correction on the fly
                              or is it already done. If flat field correction
                              has been preprocessed, also deal with half
                              acquisition case
    """
    assert "output" in recons_param
    outputdir = recons_param["output"]

    if exec_cmd is True:
        if has_tofu() is False:
            logger.error(
                "Cannot launch tofu reconstruction because " "tofu is not installed."
            )
            return
    if delete_existing is True and "output" in recons_param:
        logger.info("remove output dir: %s" % recons_param["output"])
        if exec_cmd:
            for _file in glob.glob(outputdir + "*.tif"):
                try:
                    os.remove(_file)
                except Exception as e:
                    logger.error(e)
        else:
            logger.info(("will remove all files" + outputdir + "*.tif"))

    options = _retrieve_opts_recons_cmd(
        scan_id=scan_id,
        recons_param=recons_param,
        additional_opts=additional_options,
        pre_proc_ffc=pre_proc_ffc,
    )

    try:
        logger.info("launch command : " + "tofu reco" + options)
        if exec_cmd is True:
            subprocess.call(
                "tofu reco " + options, shell=True, stderr=sys.stderr, stdout=sys.stdout
            )
    except OSError:
        return False
    else:
        return True


def _preprocess_ffc(scan, recons_param, additional_options, output, exec_cmd=True):
    """Process a flat field reconstruction for given scan using tofu

    :param TomwerScanBase scan: path of the scan to reconstruct
    :param dict recons_param: parameters for the reconstruction
    :param str additional_options: additional options to be add at the tofu reco
                                  call.
    :param bool exec_cmd: if True, will run reconstruction, otherwise will only
                          display the reconstruction parameters.
    """
    assert isinstance(scan, TomwerScanBase)
    if exec_cmd is True:
        if has_tofu() is False:
            logger.error(
                "Cannot launch tofu reconstruction because " "tofu is not installed."
            )
            return

    output_folder = os.path.join(output, "fc")
    if exec_cmd is True and os.path.exists(output_folder):
        logger.info("removing" + output_folder)
        shutil.rmtree(output_folder)
    output = output_folder + "-%04i.tif"
    options = _retrieve_opts_ffc_cmd(
        scan=scan,
        recons_param=recons_param,
        additional_opts=additional_options,
        output=output,
    )
    if output is not None:
        logger.info(
            "flat field correction preprocessing result will be store in " + output
        )
    logger.info("launch command : " + "tofu preprocess" + options)
    if exec_cmd is True:
        subprocess.call(
            "tofu preprocess " + options,
            shell=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
    return True


def _preprocess_stitching(
    shift, blend, adjust_mean, fc_folder, fc1_folder, fc2_folder, dry_run
):
    """
    move half acquisition dataset to full within flips

    :param float shift: How much is second image shifted with respect to the
                        first one. For example, shift 0 means that both images
                        overlap perfectly and the stitching doesn’t actually
                        broaden the image. Shift corresponding to image width
                        makes for a stitched image with twice the width of the
                        respective images.
    :param bool blend: Linearly interpolate between the two images in the
                       overlapping region.
    :param bool adjust_mean: Compute the mean of the overlapping region in the
                             two images and adjust the second image to match
                             the mean of the first one.
    :param str fc_folder: original folder of the sinogram
    :param str fc1_folder:
    :param str fc2_folder:
    :param bool dry_run:
    """
    assert shift is not None
    assert blend is not None
    if dry_run is False:
        if os.path.exists(fc1_folder):
            logger.info("removing" + fc1_folder)
            shutil.rmtree(fc1_folder)
        os.makedirs(fc1_folder)
        if os.path.exists(fc2_folder):
            logger.info("removing" + fc2_folder)
            shutil.rmtree(fc2_folder)
        os.makedirs(fc2_folder)

    def move_tiff():
        n_file = len(os.listdir(fc_folder))
        if n_file % 2 != 0:
            logger.error("even number of projection file, unable to apply stitching")
            return False
        order_list_dir = os.listdir(fc_folder)
        order_list_dir.sort()
        for i_file, file_ in enumerate(list(order_list_dir)):
            if i_file < n_file / 2:
                dest = fc1_folder
            else:
                dest = fc2_folder
            file_path = os.path.join(fc_folder, file_)
            shutil.move(src=file_path, dst=dest)
        # now fc should be empty of any tif file
        return True

    def stitching(shift, blend, adjust_mean):
        work = "[read path=%s, read path=%s ! flip direction=horizontal]" % (
            fc1_folder,
            fc2_folder,
        )
        work = work + " ! stitch shift=%s " % shift
        work += "blend=%s " % str(int(blend))
        work += "adjust-mean=%s " % str(int(adjust_mean))
        work += "! write filename=%s" % os.path.join(fc_folder, "fc-%04i.tif")
        try:
            logger.info("launch command : " + "ufo-launch " + work)
            if not dry_run:
                subprocess.call(
                    "ufo-launch " + work,
                    shell=True,
                    stderr=sys.stderr,
                    stdout=sys.stdout,
                )
        except OSError:
            return False
        else:
            return True

    if not dry_run:
        move_res = move_tiff()
    else:
        logger.info("move tiff file from fc to fc1, fc2")
        move_res = True
    if move_res is True:
        stitching(shift, blend=blend, adjust_mean=adjust_mean)
    return fc_folder


def has_tofu():
    """

    :return: true if the os knows the tofu command
    """
    if not sys.platform.startswith("linux"):
        return False
    try:
        subprocess.call(
            ["tofu", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except Exception:
        return False


class LaminoReconstruction(Task, input_names=("data",), output_names=("data",)):
    """
    Process to launch the lamino reconstruction

    TODO: setting parameters should be group with the gui/lamino/tofu/xxx files
    But this binding is probably overkilled as we should use the tofu python
    binding for it. But no python3 version at the moment.
    """

    DEFAULT_RECONSTRUCTION_PARAMETERS_VALS = {
        "region": None,
        "retry-timeout": None,
        "retries": None,
        "reduction-mode": None,
        "dark-scale": None,
        "darks": None,
        "slices-per-device": None,
        "slice-memory-coeff": 0.8,
        "number": None,
        "volume-angle-x": None,
        "volume-angle-y": None,
        "volume-angle-z": None,
        "output": None,
        "center-position-x": None,
        "center-position-z": None,
        "axis-angle-x": None,
        "axis-angle-y": None,
        "z-parameter": None,
        "retrieval-method": None,
        "energy": None,
        "pixel-size": None,
        "propagation-distance": None,
        "regularization-rate": None,
        "thresholding-rate": None,
        "flats": None,
        "flats2": None,
        "overall-angle": 360.0,
        "x-region": None,
        "y-region": None,
        "verbose": False,
        "dry-run": False,
        "absorptivity": False,
        "half-acquisition": False,
        "z": None,
    }

    def __init__(self, varinfo=None, inputs=None, name=None):
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=name)
        if "recons_params" in inputs:
            raise KeyError(
                "Do not use recons_params but `lamino_recons_params` instead"
            )

        self._reconsparams = self.DEFAULT_RECONSTRUCTION_PARAMETERS_VALS
        recons_params = inputs.get("lamino_params", {})
        self._reconsparams.update(recons_params)
        self._additional_reco_options = ""
        self._additional_preprocess_options = ""
        self._delete_existing = False
        self._dry_run = False
        self.__ffc_has_been_preprocessed = False
        self.__ffc_tmp_dir = None
        self.__prepare_ffc_dir()
        # top level directory to make the stitching and flat field preprocessing

        self.__latest_ffc_prerecons = (None, None, None, None, None, self._dry_run)
        # Store the current existing flat field reconstruction as the 'ffc key'
        # (scan, x center, method, dark, ff, dry_run) because this should be
        # executed only if x center change or scan path and we want to keep the same
        # behavior with or without the dry-run option
        self.__latest_stitching = None, None

    def __del__(self):
        self.__remove_ffc_dir()

    def __remove_ffc_dir(self):
        if self.__ffc_tmp_dir is not None and os.path.exists(self.__ffc_tmp_dir):
            shutil.rmtree(self.__ffc_tmp_dir)

    def __prepare_ffc_dir(self):
        self.__remove_ffc_dir()
        self.__ffc_tmp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.__ffc_tmp_dir, "fc"))

    @property
    def reconstruction_parameters(self):
        return self._reconsparams

    @reconstruction_parameters.setter
    def reconstruction_parameters(self, params):
        self._reconsparams = params
        if "output" in self._reconsparams:
            self.dry_run = self._reconsparams["output"] in (None, "")

    @property
    def additional_reco_options(self):
        return self._additional_reco_options

    @additional_reco_options.setter
    def additional_reco_options(self, opts):
        self._additional_reco_options = opts
        if "delete-existing" in self.additional_reco_options:
            self.delete_existing = self.additional_reco_options["delete-existing"]

    @property
    def additional_preprocess_options(self):
        return self._additional_preprocess_options

    @additional_preprocess_options.setter
    def additional_preprocess_options(self, opts):
        self._additional_preprocess_options = opts

    @property
    def delete_existing(self):
        return self._delete_existing

    @delete_existing.setter
    def delete_existing(self, _delete):
        assert type(_delete) is bool
        self._delete_existing = _delete

    @property
    def dry_run(self):
        return self._dry_run

    @dry_run.setter
    def dry_run(self, dryrun):
        assert type(dryrun) is bool
        self._dry_run = dryrun

    def preprocess_ff(self, scan):
        """preprocess flat field corrcetion on the given scan.
        Result will be stored in `__ffc_tmp_dir` and the tuple
        (scan, center-position-x) will be stored as a key to avoid repeating
        this preprocessing flat field if already process.

        :return: path of the flat field corrected file or None if cannot process
        """
        assert isinstance(scan, TomwerScanBase)
        if scan is None:
            return None

        def get_val_or_none(key):
            if key in self._reconsparams:
                return self._reconsparams[key]
            else:
                return None

        x_center = get_val_or_none("center-position-x")

        if "output" not in self._reconsparams:
            logger.error(
                "no output define, requested for pre processing the "
                "flat field correction in pre processing."
            )
            return None
        elif x_center is None:
            logger.error(
                "x center position not defined, unable to process flat "
                "field correction"
            )
            return None

        output_folder = self._reconsparams["output"]
        output_folder = self._get_fc_folder_frm_output_folder(output_folder)
        fc_folder = os.path.join(output_folder, "fc")
        # TODO: should not integrate xySlice ...

        # case data is already stored in ffc_preprocess_dir
        darks = get_val_or_none("darks")
        flats = get_val_or_none("flat")
        flats2 = get_val_or_none("flats2")
        method = get_val_or_none("reduction-mode")
        if (
            scan,
            x_center,
            method,
            darks,
            [flats, flats2],
            self._dry_run,
        ) == self.__latest_ffc_prerecons:
            logger.info("flat field correction already process, skip correction")
            return fc_folder

        recons_params = self.reconstruction_parameters
        recons_params["projections"] = _get_projection_file_pattern(scan_path=scan.path)
        _preprocess_ffc(
            scan=scan,
            recons_param=recons_params,
            additional_options=self.additional_preprocess_options,
            exec_cmd=(not self.dry_run),
            output=fc_folder,
        )
        recons_params["projections"] = os.path.join(fc_folder, "*.tif")
        self.__latest_ffc_prerecons = (
            scan,
            x_center,
            method,
            darks,
            [flats, flats2],
            self._dry_run,
        )
        return fc_folder

    def _get_fc_folder_frm_output_folder(self, output_folder):
        if output_folder is None:
            return "/ghost_folder"
        else:
            return os.path.dirname(output_folder)

    def is_ffc_has_been_preprocessed(self, scan, x_center, method, darks, ff):
        return (
            scan,
            x_center,
            method,
            darks,
            ff,
            self._dry_run,
        ) == self.__latest_ffc_prerecons

    def stitching_requested(self):
        """

        :return: True if stitching is requested
        """
        return (
            "half-acquisition" in self._reconsparams
            and self._reconsparams["half-acquisition"] is True
        )

    def need_reprocessing_stitching(
        self, shift, blend, adjust_mean, fc_folder, fc1_folder, fc2_folder, dry_run
    ):
        """

        :param float shift:
        :param bool blend:
        :param bool adjust_mean:
        :param str fc_folder:
        :param str fc1_folder:
        :param str fc2_folder:
        :param bool dry_run:
        :return: True if stitching need to be reprocess
        """
        return self.__latest_stitching != (
            self.__latest_ffc_prerecons,
            (shift, blend, adjust_mean, fc_folder, fc1_folder, fc2_folder, dry_run),
        )

    def preprocessing_requested(self):
        """

        :return: True if some preprocessing is require
        """
        return (
            "ffc-when" in self._reconsparams
            and self._reconsparams["ffc-when"] is FFCWhen.preprocessing
        )

    def need_reprocessing_ffc(self, scan, x_center, method, darks, ff, dry_run):
        """

        :param :class:`.TomoBase` scan: scan to process
        :param float x_center: x center
        :param str method: can be 'median' or 'average'
        :param str darks:
        :param list ff:
        :param bool dry_run:
        :return: True if flat field need to be reprocess
        """
        assert isinstance(scan, TomwerScanBase)
        return self.__latest_ffc_prerecons != (
            scan.path,
            x_center,
            method,
            darks,
            ff,
            dry_run,
        )

    def run(self):
        scan = self.inputs.data
        if scan is None:
            self.outputs.data = None
            return
        if type(scan) is dict:
            _scan = ScanFactory.create_scan_object_frm_dict(scan)
        elif type(scan) is str:
            _scan = ScanFactory.create_scan_object(scan_path=scan)
        else:
            _scan = scan
        if not isinstance(_scan, TomwerScanBase):
            raise TypeError(
                "input data is expected to be dict, str or "
                "TomwerScanBase not {}".format(type(_scan))
            )

        # if need some preprocessing
        if self.preprocessing_requested():
            print("------------------------")
            print("request preprocessing ffc")
            self._ff_has_been_reprocess = False
            # if need to reprocess flat field
            ffc_key = {
                "scan": _scan,
                "x_center": self._reconsparams["center-position-x"],
                "method": self._reconsparams["reduction-mode"],
                "darks": self._reconsparams["darks"],
                "ff": [self._reconsparams["flats"], self._reconsparams["flats2"]],
                "dry_run": self._dry_run,
            }
            if self.need_reprocessing_ffc(**ffc_key):
                ffc_folder = self.preprocess_ff(scan=_scan)
                if ffc_folder is None:
                    logger.error("Fail to process the flat field correction")
                    return None
                self._reconsparams["projections"] = _get_projection_file_pattern(
                    scan_path=scan.path, ffc_folder=ffc_folder
                )
                self._ff_has_been_reprocess = True

            if self.stitching_requested():
                output_folder = self._reconsparams["output"]
                output_folder = self._get_fc_folder_frm_output_folder(output_folder)
                fc_folder = os.path.join(output_folder, "fc")
                fc1_folder = os.path.join(output_folder, "fc1")
                fc2_folder = os.path.join(output_folder, "fc2")
                shift = self._reconsparams["center-position-x"]
                blend = self._reconsparams["blend"]
                adjust_mean = self._reconsparams["adjust-mean"]
                if self.need_reprocessing_stitching(
                    shift=shift,
                    fc_folder=fc_folder,
                    fc1_folder=fc1_folder,
                    fc2_folder=fc2_folder,
                    dry_run=self.dry_run,
                    blend=blend,
                    adjust_mean=adjust_mean,
                ):

                    print("------------------------")
                    print("run stitching")
                    image_width = getDim1Dim2(scan.path)[0]
                    if image_width is None:
                        logger.warning(
                            "failed to find image width, set to " "2048 by default"
                        )
                        image_width = 2048
                    shift = 2.0 * self._reconsparams["center-position-x"] - image_width
                    _preprocess_stitching(
                        shift=shift,
                        fc_folder=fc_folder,
                        fc1_folder=fc1_folder,
                        fc2_folder=fc2_folder,
                        dry_run=self.dry_run,
                        blend=blend,
                        adjust_mean=adjust_mean,
                    )

                    self.__latest_stitching = (
                        self.__latest_ffc_prerecons,
                        (
                            shift,
                            blend,
                            adjust_mean,
                            fc_folder,
                            fc1_folder,
                            fc2_folder,
                            self.dry_run,
                        ),
                    )
                else:
                    logger.info("data already stitch from previous process")
                fc_folder = os.path.join(output_folder, "fc")
                # stitching reduce the number of projections by a factor of 2
                self._reconsparams["number"] = int(self._reconsparams["number"] / 2)
                self._reconsparams["overall-angle"] = (
                    self._reconsparams["overall-angle"] / 2.0
                )
            else:
                # TODO: remove, ffc folder is fc folder
                fc_folder = ffc_folder
            self._reconsparams["projections"] = 'projections "' + os.path.join(
                fc_folder, '*.tif"'
            )

        res = _tofu_lamino_reconstruction(
            scan_id=_scan.path,
            recons_param=self._reconsparams,
            additional_options=self.additional_reco_options,
            delete_existing=self.delete_existing,
            exec_cmd=(not self.dry_run),
            pre_proc_ffc=self.preprocessing_requested(),
        )
        if not self.dry_run:
            entry = "entry"
            if isinstance(scan, HDF5TomoScan):
                entry = scan.entry
            with scan.acquire_process_file_lock():
                self.register_process(
                    process_file=scan.process_file,
                    entry=entry,
                    configuration=self._reconsparams,
                    results={},
                    process_index=scan.pop_process_index(),
                    overwrite=True,
                )

        if res is False:
            logger.error("Reconstruction of", _scan.path, "failed")
        if self._return_dict:
            self.outputs.data = _scan.to_dict()
        else:
            self.outputs.data = _scan

    def set_configuration(self, configuration):
        assert isinstance(configuration, (tuple, list))
        self.additional_preprocess_options, self.additional_reco_options = configuration

    @staticmethod
    def program_name():
        return "lamino"

    @staticmethod
    def program_version():
        """version of the program used for this processing"""
        return tomwer.version.version


def getDark(scan):
    """Return darks as a string for tofu from the scan path"""
    concert_projection_files = os.path.join(scan, "radios")
    concert_darks_path = os.path.join(scan, "darks")
    if (
        os.path.exists(concert_darks_path)
        and os.path.exists(concert_projection_files)
        and len(glob.glob(concert_darks_path + os.sep + "frame_*.tif")) > 0
    ):
        return concert_darks_path + os.sep + "frame_*.tif"
    else:
        files = os.listdir(scan)
        for thFile in (
            DARKHST_PREFIX,
            "dark.edf",
            "darkend0000.edf",
            "darkend000.edf",
            "darkHST.edf",
        ):
            if thFile in files:
                return os.path.join(scan, thFile)
        return None


def getFlats(scan):
    """
    Return flats as a string for tofu from the scan path

    :return: tuple (flats, secondFlats)
    """

    def treatRawRef(rawRefFiles):
        ns = set()
        for _file in rawRefFiles:
            name = _file.rstrip(".edf")
            ns.add(name.split("_")[-1])
        ns = sorted(ns)
        if len(ns) == 0:
            return None, None
        elif len(ns) == 1:
            return os.path.join(scan, "ref*_" + ns[0] + ".edf")
        else:
            return (
                os.path.join(scan, "ref*_" + ns[0] + ".edf"),
                os.path.join(scan, "ref*_" + ns[-1] + ".edf"),
            )

    # deal with concert files
    concert_projection_files = os.path.join(scan, "radios")
    concert_flats_path = os.path.join(scan, "flats")
    if os.path.exists(concert_flats_path) and os.path.exists(concert_projection_files):
        flats = None
        flats2 = None
        if len(glob.glob(concert_flats_path + os.sep + "frame_*.tif")) > 0:
            flats = concert_flats_path + os.sep + "frame_*.tif"
        concert_flats2_path = os.path.join(scan, "flats_2")
        if len(glob.glob(concert_flats2_path + os.sep + "frame_*.tif")) > 0:
            flats2 = concert_flats2_path + os.sep + "frame_*.tif"
        if flats is not None or flats2 is not None:
            return flats, flats2

    # deal with classical files
    files = os.listdir(scan)
    refHSTFiles = []  # files starting with refHST (treated by darkRef)
    rawRefFiles = []  # files starting with ref only (raw ref files)
    for _file in files:
        if _file.startswith("ref") and _file.endswith(".edf"):
            if _file.startswith(REFHST_PREFIX):
                refHSTFiles.append(_file)
            else:
                rawRefFiles.append(_file)

    refHSTFiles = sorted(refHSTFiles)
    if len(refHSTFiles) == 0:
        return treatRawRef(rawRefFiles)
    elif len(refHSTFiles) == 1:
        return os.path.join(scan, refHSTFiles[0]), None
    else:
        logger.warning("Found more than two refHST files")
        return (os.path.join(scan, refHSTFiles[0]), os.path.join(scan, refHSTFiles[-1]))
