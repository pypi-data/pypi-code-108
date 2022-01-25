# coding: utf-8
###########################################################################
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
#############################################################################

"""contain the SAAxisProcess. Half automatic center of rotation calculation
"""

__authors__ = [
    "H.Payno",
]
__license__ = "MIT"
__date__ = "10/02/2021"


from silx.io.url import DataUrl
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.process.reconstruction.nabu.nabuslices import (
    interpret_tomwer_configuration,
)
from typing import Iterable, Optional

from tomwer.core.utils.slurm import is_slurm_available
from tomwer.io.utils.utils import get_slice_data
from ..nabu import utils
from tomwer.core.process.reconstruction.scores.params import ScoreMethod
from .params import ReconstructionMode
from .params import SAAxisParams
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.utils import logconfig
from tomwer.core.process.reconstruction.nabu.utils import check_sinogram_half
from processview.core.manager import ProcessManager, DatasetState
from processview.core.superviseprocess import SuperviseProcess
from tomwer.core.process.task import Task
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomoscan.io import HDF5File
import tomwer.version
import numpy
from tomwer.core.progress import Progress
from tomwer.core.process.reconstruction.axis import AxisRP
import os
import logging
import copy
import h5py
from tomwer.core.process.reconstruction.scores import compute_score
from tomwer.core.process.reconstruction.scores import ComputedScore
from tomwer.core.process.reconstruction.scores import get_disk_mask_radius, apply_roi
from tomwer.core.process.reconstruction.nabu.nabuscores import (
    run_nabu_one_slice_several_config,
)


_logger = logging.getLogger(__name__)


DEFAULT_RECONS_FOLDER = "saaxis_results"


def one_slice_several_cor(
    scan, configuration: dict, process_id: Optional[int] = None
) -> tuple:
    """
    Run a slice reconstruction using nabu per Center Of Rotation (cor) provided
    Then for each compute a score (quality) of the center of rotation

    .. warning:: if target if the slurm cluster this will wait for the processing to be done to return the result.
                 as this function is returning the result of the score process on reconstructed slices

    :param TomwerScanBase scan:
    :param dict configuration: nabu reconstruction parameters (can include 'slurm-cluster' key defining the slurm configuration)
    :param int process_id: process id
    :return: cor_reconstructions, outs, errs
             cor_reconstructions is a dictionary of cor as key and a tuple
             (url, score) as value
    :rtype: tuple
    """
    if isinstance(configuration, dict):
        configuration = SAAxisParams.from_dict(configuration)
    elif not isinstance(configuration, SAAxisParams):
        raise TypeError(
            "configuration should be a dictionary or an instance of SAAxisParams"
        )
    check_sinogram_half(scan)

    configuration.check_configuration()
    mode = ReconstructionMode.from_value(configuration.mode)
    slice_index = configuration.slice_indexes
    cors = configuration.cors
    nabu_config = configuration.nabu_params
    output_dir = configuration.output_dir
    dry_run = configuration.dry_run
    nabu_output_config = nabu_config.get("output", {})
    file_format = nabu_output_config.get("file_format", "hdf5")
    cluster_config = configuration.cluster_config
    _logger.info(
        "launch reconstruction of slice {} and cors {}".format(slice_index, cors)
    )
    if mode is ReconstructionMode.VERTICAL:
        if isinstance(slice_index, str):
            if not slice_index == "middle":
                raise ValueError("slice index {} not recognized".format(slice_index))
        elif not len(slice_index) == 1:
            raise ValueError("{} mode only manage one slice".format(mode.value))
        else:
            slice_index = list(slice_index.values())[0]
        advancement = Progress("saaxis - slice {} of {}".format(slice_index, scan))

        _, cor_reconstructions, outs, errs, future_scans = run_slice_reconstruction(
            scan=scan,
            slice_index=slice_index,
            cor_positions=cors,
            config=nabu_config,
            output_dir=output_dir,
            dry_run=dry_run,
            file_format=file_format,
            advancement=advancement,
            cluster_config=cluster_config,
            process_id=process_id,
        )
    else:
        raise ValueError("{} is not handled for now".format(mode))

    # treat future
    if output_dir is None:
        output_dir = os.path.join(scan.path, DEFAULT_RECONS_FOLDER)

    for _, future_scan in future_scans.items():
        future_scan.results()

    class PostProcessing:
        def run(self, slice_index):
            datasets = self.load_datasets()

            mask_disk_radius = get_disk_mask_radius(datasets)
            scores = {}
            rois = {}
            for cor, (url, data) in datasets.items():
                if data is None:
                    score = None
                else:
                    assert data.ndim == 2
                    data_roi = apply_roi(data=data, radius=mask_disk_radius, url=url)
                    rois[cor] = data_roi

                    # move data_roi to [0-1] range
                    #  preprocessing: get percentile 0 and 99 from image and
                    #  "clean" highest and lowest pixels from it
                    min_p, max_p = numpy.percentile(data_roi, (1, 99))
                    data_roi_int = data_roi[...]
                    data_roi_int[data_roi_int < min_p] = min_p
                    data_roi_int[data_roi_int > max_p] = max_p
                    data_roi_int = (data_roi_int - min_p) / (max_p - min_p)

                    if isinstance(scan, EDFTomoScan):
                        _logger.info("tomo consistency is not handled for EDF scan")
                        tomo_consistency_score = None
                    else:
                        try:
                            projections_with_angle = scan.projections_with_angle()
                            angles_ = [
                                frame_angle
                                for frame_angle, frame in projections_with_angle.items()
                            ]
                            angles = []
                            for angle in angles_:
                                if not isinstance(angle, str):
                                    angles.append(angle)
                            if slice_index == "middle":
                                if scan.dim_2 is not None:
                                    slice_index = scan.dim_2 // 2
                                else:
                                    _logger.warning(
                                        "scan.dim_2 returns None, unable to deduce middle "
                                        "pick 1024"
                                    )
                                    slice_index = 1024
                            tomo_consistency_score = compute_score(
                                data=data,
                                method=ScoreMethod.TOMO_CONSISTENCY,
                                angles=angles,
                                original_sinogram=scan.get_sinogram(slice_index),
                                detector_width=scan.dim_1,
                                original_axis_position=cor + scan.dim_1 / 2.0,
                            )
                        except Exception as e:
                            _logger.error(e)
                            tomo_consistency_score = None
                    score = ComputedScore(
                        tv=compute_score(data=data_roi_int, method=ScoreMethod.TV),
                        std=compute_score(data=data_roi_int, method=ScoreMethod.STD),
                        tomo_consistency=tomo_consistency_score,
                    )
                scores[cor] = (url, score)
            return scores, rois

        def load_datasets(self):
            datasets_ = {}
            for cor, urls in cor_reconstructions.items():
                if len(urls) == 0:
                    # in the case failed to load the url
                    continue
                elif len(urls) > 1:
                    raise ValueError("only one slice reconstructed expected per cor")
                url = urls[0]
                if not isinstance(url, (DataUrl, str)):
                    raise TypeError(
                        f"url is expected to be a str or DataUrl not {type(url)}"
                    )

                try:
                    data = get_slice_data(url=url)
                except Exception as e:
                    _logger.error(
                        "Fail to compute a score for {}. Reason is {}"
                        "".format(url.path(), str(e))
                    )
                    datasets_[cor] = (url, None)
                else:
                    if data.ndim == 3:
                        if data.shape[0] == 1:
                            data = data.reshape(data.shape[1], data.shape[2])
                        elif data.shape[2] == 1:
                            data = data.reshape(data.shape[0], data.shape[1])
                        else:
                            raise ValueError(
                                "Data is expected to be 2D. Not {}".format(data.ndim)
                            )
                    elif data.ndim == 2:
                        pass
                    else:
                        raise ValueError(
                            "Data is expected to be 2D. Not {}".format(data.ndim)
                        )

                    datasets_[cor] = (url, data)
            return datasets_

    post_processing = PostProcessing()
    scores, rois = post_processing.run(slice_index=slice_index)
    return scores, outs, errs, rois


def run_slice_reconstruction(
    scan: TomwerScanBase,
    cor_positions: Iterable,
    slice_index: int,
    config: dict,
    output_dir=None,
    dry_run: bool = False,
    file_format: str = "hdf5",
    advancement=None,
    cluster_config=None,
    process_id: Optional[int] = None,
) -> tuple:
    """
    call nabu for a reconstruction on scan with the given configuration

    :param TomwerScanBase scan: scan to reconstruct
    :param tuple: cor_positions cor position to used for reconstruction
    :param dict config: configuration to run the reconstruction
    :param Union[None,str]: output dir folder. If None then this will be store
                            under the acquisition folder/saaxis_results
    :param bool dry_run: do we want to run dry
    :param bool local: do we want to run a local reconstruction
    :param advancement: optional Progress class to display advancement

    :return: success: bool, cor_results: dict, outs: list, errs: list, future_scan
             recons_urls is a dict with cor value as key (float) and reconstructed slice url
             as value
    :rtype: dict
    """
    nabu_configurations = interpret_tomwer_configuration(config, scan=None)
    if len(nabu_configurations) == 0:
        raise RuntimeWarning(
            "Unable to get a valid nabu configuration for " "reconstruction."
        )
    elif len(nabu_configurations) > 1:
        _logger.warning(
            "Several configuration found for nabu (you probably "
            "ask for several delta/beta value or several slices). "
            "Picking the first one."
        )

    # work on file name...
    if output_dir is None:
        output_dir = os.path.join(scan.path, DEFAULT_RECONS_FOLDER)
    if scan.process_file is not None:
        steps_file_basename, _ = os.path.splitext(scan.process_file)
        steps_file_basename = "_".join(
            ("steps_file_basename", "nabu", "sinogram", "save", "step")
        )
        steps_file_basename = steps_file_basename + ".hdf5"
        steps_file = os.path.join(output_dir, steps_file_basename)
    else:
        steps_file = ""

    base_config = nabu_configurations[0][0]
    if cluster_config == {}:
        cluster_config = None
    is_cluster_job = cluster_config is not None
    if is_cluster_job and not is_slurm_available():
        raise ValueError(
            "job on cluster requested but no access to slurm cluster found"
        )
    configs = {}

    for i_cor, cor in enumerate(cor_positions):
        nabu_configuration = copy.deepcopy(base_config)
        nabu_configuration["pipeline"] = {
            "save_steps": "sinogram" if i_cor == 0 else "",
            "resume_from_step": "sinogram",
            "steps_file": steps_file,
        }
        # convert cor from tomwer ref to nabu ref
        if scan.dim_1 is not None:
            cor_nabu_ref = cor + scan.dim_1 / 2.0
        else:
            _logger.warning("enable to get image half width. Set it to 1024")
            cor_nabu_ref = cor + 1024
        # handle reconstruction section
        if "reconstruction" not in nabu_configuration:
            nabu_configuration["reconstruction"] = {}
        nabu_configuration["reconstruction"]["rotation_axis_position"] = str(
            cor_nabu_ref
        )
        # handle output section
        if "output" not in nabu_configuration:
            nabu_configuration["output"] = {}
        nabu_configuration["output"]["location"] = output_dir
        nabu_configuration["output"]["file_format"] = file_format
        # handle resources section
        nabu_configuration["resources"] = utils.get_nabu_resources_desc(
            scan=scan, workers=1, method="local"
        )
        configs[cor] = nabu_configuration
    return run_nabu_one_slice_several_config(
        nabu_configs=configs,
        scan=scan,
        slice_index=slice_index,
        dry_run=dry_run,
        file_format=file_format,
        advancement=advancement,
        cluster_config=cluster_config.to_dict() if cluster_config is not None else None,
        process_id=process_id,
    )


class SAAxisProcess(
    Task, SuperviseProcess, input_names=("data",), output_names=("data",)
):
    """
    Main process to launch several reconstruction of a single slice with
    several Center Of Rotation (cor) values
    """

    def __init__(self, process_id=None, inputs=None, varinfo=None):
        Task.__init__(self, varinfo=varinfo, inputs=inputs)
        SuperviseProcess.__init__(self, process_id=process_id)
        self._dry_run = inputs.get("dry_run", False)
        self._dump_process = inputs.get("dump_info", True)
        self._dump_roi = inputs.get("dump_roi", False)
        self._std_outs = tuple()
        self._std_errs = tuple()
        if "sa_axis_params" in inputs:
            self.set_configuration(inputs["sa_axis_params"])

    @property
    def std_outs(self):
        return self._std_outs

    @property
    def std_errs(self):
        return self._std_errs

    def set_dry_run(self, dry_run):
        self._dry_run = dry_run

    @property
    def dry_run(self):
        return self._dry_run

    @property
    def dump_roi(self):
        return self._dump_roi

    @dump_roi.setter
    def dump_roi(self, dump):
        self._dump_roi = dump

    def set_configuration(self, configuration: dict) -> None:
        if isinstance(configuration, SAAxisParams):
            self._settings = configuration.to_dict()
        elif isinstance(configuration, dict):
            self._settings = configuration
        else:
            raise TypeError(
                "configuration should be an instance of dict or " "SAAxisParams"
            )

    @staticmethod
    def autofocus(scan):
        scores = scan.saaxis_params.scores
        if scores is None:
            return
        score_method = scan.saaxis_params.score_method
        best_cor, best_score = None, 0
        for cor, (_, score_cls) in scores.items():
            score = score_cls.get(score_method)
            if score is None:
                continue
            if score > best_score:
                best_cor, best_score = cor, score
        scan.saaxis_params.autofocus = best_cor
        if scan.axis_params is None:
            scan.axis_params = AxisRP()
        scan.axis_params.frame_width = scan.dim_1
        scan.axis_params.set_relative_value(best_cor)

    def run(self):
        scan = self.inputs.data
        if scan is None:
            self.outputs.data = None
            return
        if isinstance(scan, TomwerScanBase):
            scan = scan
        elif isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            raise ValueError(
                "input type of {}: {} is not managed" "".format(scan, type(scan))
            )
        # TODO: look and update if there is some nabu reconstruction
        # or axis information to be used back
        configuration = self.get_configuration()
        params = SAAxisParams.from_dict(configuration)
        # insure output dir is created
        if params.output_dir in (None, ""):
            params.output_dir = os.path.join(scan.path, "saaxis_results")
            if not os.path.exists(params.output_dir):
                os.makedirs(params.output_dir)
        # try to find an estimated cor
        #  from a previously computed cor
        if params.estimated_cor is None and scan.axis_params is not None:
            relative_cor = scan.axis_params.relative_cor_value
            if relative_cor is not None and numpy.issubdtype(
                type(relative_cor), numpy.number
            ):
                params.estimated_cor = relative_cor
                _logger.info(
                    "{}: set estimated cor from previously computed cor ({})".format(
                        str(scan), params.estimated_cor
                    )
                )
        #  from scan.estimated_cor_position
        if params.estimated_cor is None and scan.estimated_cor_frm_motor is not None:
            params.estimated_cor = scan.estimated_cor_frm_motor
            _logger.info(
                "{}: set estimated cor from motor position ({})".format(
                    str(scan), params.estimated_cor
                )
            )
        if scan.dim_1 is not None:
            params.image_width = scan.dim_1
        scan.saaxis_params = params
        cors_res, self._std_outs, self._std_errs, rois = one_slice_several_cor(
            scan=scan,
            configuration=self.get_configuration(),
            process_id=self.process_id,
        )
        scan.saaxis_params.scores = cors_res
        self.autofocus(scan=scan)
        self._process_end(scan=scan, cors_res=cors_res, score_rois=rois)
        self.outputs.data = scan

    def _process_end(self, scan, cors_res, score_rois):
        assert isinstance(scan, TomwerScanBase)
        try:
            extra = {
                logconfig.DOC_TITLE: self._scheme_title,
                logconfig.SCAN_ID: str(scan),
            }
            slice_index = self.get_configuration().get("slice_index", None)

            if cors_res is None:
                info = "fail to compute cor scores of slice {} for scan {}." "".format(
                    slice_index, scan
                )
                _logger.processFailed(info, extra=extra)
                ProcessManager().notify_dataset_state(
                    dataset=scan, process=self, state=DatasetState.FAILED, details=info
                )
            else:
                info = "cor scores of slice {} for scan {} computed." "".format(
                    slice_index, scan
                )
                _logger.processSucceed(info, extra=extra)
                ProcessManager().notify_dataset_state(
                    dataset=scan,
                    process=self,
                    state=DatasetState.WAIT_USER_VALIDATION,
                    details=info,
                )
        except Exception as e:
            _logger.error(e)
        else:
            if self._dump_process:
                process_idx = SAAxisProcess.process_to_tomwer_processes(
                    scan=scan,
                )
                if self.dump_roi and process_idx is not None:
                    self.dump_rois(
                        scan, score_rois=score_rois, process_index=process_idx
                    )

    @staticmethod
    def dump_rois(scan, score_rois, process_index):
        process_file = scan.process_file
        process_name = "tomwer_process_" + str(process_index)

        if scan.saaxis_params.scores in (None, {}):
            return

        def get_process_path():
            return "/".join((scan.entry or "entry", process_name))

        # save it to the file
        with Task._get_lock(process_file):
            # needs an extra lock for multiprocessing

            with HDF5File(process_file, mode="a") as h5f:
                nx_process = h5f.require_group(get_process_path())
                score_roi_grp = nx_process.require_group("score_roi")
                for cor, roi in score_rois.items():
                    score_roi_grp[str(cor)] = roi
                    score_roi_grp[str(cor)].attrs["interpretation"] = "image"

    @staticmethod
    def program_name():
        """Name of the program used for this processing"""
        return "semi-automatic axis"

    @staticmethod
    def program_version():
        """version of the program used for this processing"""
        return tomwer.version.version

    @staticmethod
    def definition():
        """definition of the process"""
        return "Semi automatic center of rotation / axis calculation"

    @staticmethod
    def process_to_tomwer_processes(scan):
        if scan.process_file is not None:
            entry = "entry"
            if isinstance(scan, HDF5TomoScan):
                entry = scan.entry

            cor = None
            if hasattr(scan, "axis_params"):
                cor = scan.axis_params.relative_cor_value

            process_index = scan.pop_process_index()
            try:
                with scan.acquire_process_file_lock():
                    Task._register_process(
                        process_file=scan.process_file,
                        entry=entry,
                        results={"center_of_rotation": cor if cor is not None else "-"},
                        configuration=scan.saaxis_params.to_dict(),
                        process_index=process_index,
                        overwrite=True,
                        process=SAAxisProcess,
                    )
                    SAAxisProcess._extends_results(
                        scan=scan, entry=entry, process_index=process_index
                    )
            except Exception as e:
                _logger.warning(
                    f"Fail to register process of with index {process_index}. Reason is {e}"
                )
            return process_index

    @staticmethod
    def _extends_results(scan, entry, process_index):
        process_file = scan.process_file
        process_name = "tomwer_process_" + str(process_index)

        if scan.saaxis_params.scores in (None, {}):
            return

        def get_process_path():
            return "/".join((entry or "entry", process_name))

        # save it to the file
        with Task._get_lock(process_file):
            # needs an extra lock for multiprocessing

            with HDF5File(process_file, mode="a") as h5f:
                nx_process = h5f.require_group(get_process_path())
                if "NX_class" not in nx_process.attrs:
                    nx_process.attrs["NX_class"] = "NXprocess"

                results = nx_process.require_group("results")
                for cor, (url, score) in scan.saaxis_params.scores.items():
                    results_cor = results.require_group(str(cor))
                    for method in ScoreMethod:
                        method_score = score.get(method)
                        if method_score is None:
                            results_cor[method.value] = "None"
                        else:
                            results_cor[method.value] = method_score

                    link_path = os.path.relpath(
                        url.file_path(),
                        os.path.dirname(process_file),
                    )
                    results_cor["reconstructed_slice"] = h5py.ExternalLink(
                        link_path, url.data_path()
                    )
