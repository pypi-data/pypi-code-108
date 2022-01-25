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

"""contain the SADeltaBetaProcess. Half automatic best delta / beta finder
"""

__authors__ = [
    "H.Payno",
]
__license__ = "MIT"
__date__ = "28/10/2021"


from copy import copy
from tomwer.core.process.reconstruction.nabu.nabucommon import (
    ResultSlurmRun,
    ResultsLocalRun,
    ResultsWithStd,
)
from tomwer.core.scan.scanfactory import ScanFactory
from .params import SADeltaBetaParams
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.utils import logconfig
from tomwer.core.process.reconstruction.nabu.utils import check_sinogram_half
from processview.core.manager import ProcessManager, DatasetState
from processview.core.superviseprocess import SuperviseProcess
from tomwer.core.process.task import Task
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomoscan.io import HDF5File
from silx.io.utils import get_data
import tomwer.version
from tomwer.core.process.reconstruction.nabu.nabuslices import (
    run_single_slice_reconstruction,
)
from tomwer.core.process.reconstruction.nabu.nabucommon import ResultsRun
from tomwer.core.progress import Progress
from typing import Optional, Union
import os
import logging
import h5py
import numpy
from ..nabu import utils as nabu_utils
from tomwer.core.process.reconstruction.scores import compute_score
from tomwer.core.process.reconstruction.scores import ScoreMethod
from tomwer.core.process.reconstruction.scores import ComputedScore
from tomwer.core.process.reconstruction.scores import get_disk_mask_radius, apply_roi
from tomwer.core.process.reconstruction.nabu.nabuslices import SingleSliceRunner

_logger = logging.getLogger(__name__)


DEFAULT_RECONS_FOLDER = "sadeltabeta_results"


def one_slice_several_db(
    scan: TomwerScanBase,
    configuration: Union[dict, SADeltaBetaParams],
    process_id: Optional[int] = None,
) -> tuple:
    """
    Run a slice reconstruction using nabu per Center Of Rotation (cor) provided
    Then for each compute a score (quality) of the center of rotation

    :param TomwerScanBase scan:
    :param Union[dict,SADeltaBetaParams] configuration:
    :return: cor_reconstructions, outs, errs
             cor_reconstructions is a dictionary of cor as key and a tuple
             (url, score) as value
    :rtype: tuple
    """
    if isinstance(configuration, dict):
        configuration = SADeltaBetaParams.from_dict(configuration)
    elif not isinstance(configuration, SADeltaBetaParams):
        raise TypeError(
            "configuration should be a dictionary or an instance of SAAxisParams"
        )
    check_sinogram_half(scan)

    if scan.axis_params is None:
        from tomwer.core.process.reconstruction.axis import AxisRP

        scan.axis_params = AxisRP()

    configuration.check_configuration()
    slice_index = configuration.slice_indexes
    delta_beta_s = configuration.delta_beta_values
    output_dir = configuration.output_dir
    dry_run = configuration.dry_run
    cluster_config = configuration.cluster_config
    _logger.info(
        "launch reconstruction of slice {} and delta / beta: {}".format(
            slice_index, delta_beta_s
        )
    )
    if isinstance(slice_index, str):
        if not slice_index == "middle":
            raise ValueError("slice index {} not recognized".format(slice_index))
    elif not len(slice_index) == 1:
        raise ValueError("only manage one slice")
    else:
        slice_index = list(slice_index.values())[0]
    advancement = Progress("sa-delta-beta - slice {} of {}".format(slice_index, scan))

    config = configuration.nabu_params.copy()

    check_sinogram_half(scan)
    _logger.info("start reconstruction of {}".format(str(scan)))
    # if scan contains some center of position copy it to nabu
    if scan.axis_params is not None and scan.axis_params.relative_cor_value is not None:
        if "reconstruction" in config:
            # move the cor value to the nabu reference
            cor_nabu_ref = scan.axis_params.relative_cor_value + scan.dim_1 / 2.0
            config["reconstruction"]["rotation_axis_position"] = str(cor_nabu_ref)

    _logger.info("set nabu reconstruction parameters to {}".format(str(scan)))
    scan.nabu_recons_params = config

    db_reconstructions = {}
    # key is delta / beta, value is url
    stderrs = []
    stdouts = []
    all_succeed = True
    future_scans = {}
    # key is delta / beta, value is future
    if advancement is not None:
        advancement.setMaxAdvancement(len(delta_beta_s))
    for db in delta_beta_s:
        if "output" not in config:
            config["output"] = {}
        if output_dir is None:
            config["output"]["location"] = os.path.join(
                scan.path, DEFAULT_RECONS_FOLDER
            )
        else:
            config["output"]["location"] = output_dir
        # TODO: allow file format modifications
        config["output"]["file_format"] = "hdf5"
        if "phase" not in config:
            config["phase"] = {}
        config["phase"]["delta_beta"] = db
        config["phase"]["method"] = "Paganin"
        res = run_single_slice_reconstruction(
            nabu_config=config,
            scan=scan,
            slice_index=slice_index,
            dry_run=dry_run,
            ask_sinogram_registration=False,
            ask_sinogram_load=False,
            cluster_config=cluster_config,
            add_to_latest_reconstructions=False,
            process_id=process_id,
        )
        if isinstance(res, ResultsRun):
            all_succeed = all_succeed and res.success
        if isinstance(res, ResultSlurmRun):
            future_scans[db] = res.future_slurm_jobs
        if isinstance(res, ResultsWithStd):
            if slice_index is not None:
                stderrs.append(res.std_err)
                stdouts.append(res.std_out)
        if isinstance(res, ResultsLocalRun) and len(res.results_urls) > 0:
            assert len(res.results_urls) == 1, "only one slice expected"
            db_reconstructions[db] = res.results_urls[0]

        if advancement is not None:
            advancement.increaseAdvancement(1)

    pag = False
    if "phase" in config:
        if "method" in config["phase"] and config["phase"]["method"] != "":
            pag = True

    # treat future.
    for db, future_scan_list in future_scans.items():
        assert (
            len(future_scan_list) == 1
        ), "only one future should be created for one slice / db couple"
        future = future_scan_list[0]
        future.result()
        if future.cancelled() or future.exception():
            continue
        file_prefix = SingleSliceRunner.get_file_basename_reconstruction(
            scan=scan,
            slice_index=slice_index,
            pag=pag,
            db=int(db) if db is not None else None,
        )
        # retrieve url
        recons_url = nabu_utils.get_recons_urls(
            file_prefix=file_prefix,
            location=config["output"]["location"],
            file_format=config.get("file_format", "hdf5"),
            scan=scan,
            slice_index=None,
            start_z=None,
            end_z=None,
        )

        assert len(recons_url) <= 1, "only one slice expected"
        if len(recons_url) == 1:
            db_reconstructions[db] = recons_url[0]
        else:
            _logger.warning(
                f"something went wrong with reconstruction of {db} from {str(scan)}"
            )

    class PostProcessing:
        def run(self):
            datasets = self.load_datasets()

            mask_disk_radius = get_disk_mask_radius(datasets)
            scores = {}
            rois = {}
            for db, (url, data) in datasets.items():
                if data is None:
                    score = None
                else:
                    assert data.ndim == 2
                    data_roi = apply_roi(data=data, radius=mask_disk_radius, url=url)
                    rois[db] = data_roi

                    # move data_roi to [0-1] range
                    #  preprocessing: get percentile 0 and 99 from image and
                    #  "clean" highest and lowest pixels from it
                    min_p, max_p = numpy.percentile(data_roi, (1, 99))
                    data_roi_int = data_roi[...]
                    data_roi_int[data_roi_int < min_p] = min_p
                    data_roi_int[data_roi_int > max_p] = max_p
                    data_roi_int = (data_roi_int - min_p) / (max_p - min_p)

                    score = ComputedScore(
                        tv=compute_score(data=data_roi_int, method=ScoreMethod.TV),
                        std=compute_score(data=data_roi_int, method=ScoreMethod.STD),
                    )
                scores[db] = (url, score)
            return scores, rois

        def load_datasets(self):
            datasets_ = {}
            for db, url in db_reconstructions.items():
                try:
                    data = get_data(url=url)
                except Exception as e:
                    _logger.error(
                        "Fail to compute a score for {}. Reason is {}"
                        "".format(url.path(), str(e))
                    )
                    datasets_[db] = (url, None)
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

                    datasets_[db] = (url, data)
            return datasets_

    post_processing = PostProcessing()
    scores, rois = post_processing.run()
    return scores, stdouts, stderrs, rois


class SADeltaBetaProcess(
    Task, SuperviseProcess, input_names=("data",), output_names=("data",)
):
    """
    Main process to launch several reconstruction of a single slice with
    several Center Of Rotation (cor) values
    """

    def __init__(self, process_id=None, varinfo=None, inputs=None, label=None):
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=label)
        SuperviseProcess.__init__(self, process_id=process_id)
        self._dry_run = inputs.get("dry_run", False)
        self._dump_process = inputs.get("dump_process", True)
        self._dump_roi = inputs.get("dump_roi", False)
        self._sa_delta_beta_params = inputs.get("sa_delta_beta_params", None)
        if self._sa_delta_beta_params is not None:
            self.set_configuration(self._sa_delta_beta_params)
        self._std_outs = tuple()
        self._std_errs = tuple()

    @property
    def dump_roi(self):
        return self._dump_roi

    @dump_roi.setter
    def dump_roi(self, dump):
        self._dump_roi = dump

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

    def set_configuration(self, configuration: dict) -> None:
        if isinstance(configuration, SADeltaBetaParams):
            self._settings = configuration.to_dict()
        elif isinstance(configuration, dict):
            self._settings = configuration
        else:
            raise TypeError(
                "configuration should be an instance of dict or " "SAAxisParams"
            )

    @staticmethod
    def autofocus(scan):
        scores = scan.sa_delta_beta_params.scores
        if scores is None:
            return
        score_method = scan.sa_delta_beta_params.score_method
        best_db, best_score = None, 0
        for cor, (_, score_cls) in scores.items():
            score = score_cls.get(score_method)
            if score is None:
                continue
            if score > best_score:
                best_db, best_score = cor, score
        scan.sa_delta_beta_params.autofocus = best_db
        scan.sa_delta_beta_params.value = best_db

    def run(self):
        scan = self.inputs.data
        if scan is None:
            self.outputs.data = scan
            return
        if isinstance(scan, TomwerScanBase):
            scan = scan
        elif isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            raise ValueError(
                "input type of {}: {} is not managed" "".format(scan, type(scan))
            )
        # insure scan contains some parameter regarding sa delta / beta
        if scan.sa_delta_beta_params is None:
            scan.sa_delta_beta_params = SADeltaBetaParams()

        # create dir if does not exists
        config = copy(self.get_configuration())
        params = SADeltaBetaParams.from_dict(config)
        if params.output_dir in (None, ""):
            params.output_dir = os.path.join(scan.path, DEFAULT_RECONS_FOLDER)
            if not os.path.exists(params.output_dir):
                os.makedirs(params.output_dir)
        db_res, self._std_outs, self._std_errs, rois = one_slice_several_db(
            scan=scan,
            configuration=params.to_dict(),
            process_id=self.process_id,
        )
        scan.sa_delta_beta_params.scores = db_res
        self.autofocus(scan=scan)
        self._process_end(scan=scan, db_res=db_res, score_rois=rois)
        self.outputs.data = scan

    def _process_end(self, scan, db_res, score_rois):
        assert isinstance(scan, TomwerScanBase)
        try:
            extra = {
                logconfig.DOC_TITLE: self._scheme_title,
                logconfig.SCAN_ID: str(scan),
            }
            slice_index = self.get_configuration().get("slice_index", None)

            if db_res is None:
                info = (
                    "fail to compute delta/beta scores of slice {} for scan {}."
                    "".format(slice_index, scan)
                )
                _logger.processFailed(info, extra=extra)
                ProcessManager().notify_dataset_state(
                    dataset=scan, process=self, state=DatasetState.FAILED, details=info
                )
            else:
                info = "delta/beta scores of slice {} for scan {} computed." "".format(
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
                process_idx = SADeltaBetaProcess.process_to_tomwer_processes(
                    scan=scan,
                )
                if self.dump_roi and process_idx is not None:
                    self.dump_rois(
                        scan, score_rois=score_rois, process_index=process_idx
                    )

    @staticmethod
    def dump_rois(scan, score_rois: dict, process_index: int):
        if score_rois is None or len(score_rois) == 0:
            return
        if not isinstance(score_rois, dict):
            raise TypeError("score_rois is expected to be a dict")
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
                for db, roi in score_rois.items():
                    score_roi_grp[str(db)] = roi
                    score_roi_grp[str(db)].attrs["interpretation"] = "image"

    @staticmethod
    def program_name():
        """Name of the program used for this processing"""
        return "semi-automatic delta/beta finder"

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

            db = None
            if scan.sa_delta_beta_params is not None:
                db = scan.sa_delta_beta_params.selected_delta_beta_value

            process_index = scan.pop_process_index()
            try:
                with scan.acquire_process_file_lock():
                    Task._register_process(
                        process_file=scan.process_file,
                        entry=entry,
                        results={"delta_beta": db if db is not None else "-"},
                        configuration=scan.sa_delta_beta_params.to_dict(),
                        process_index=process_index,
                        overwrite=True,
                        process=SADeltaBetaProcess,
                    )
                    SADeltaBetaProcess._extends_results(
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

        if scan.sa_delta_beta_params.scores in (None, {}):
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
                for cor, (url, score) in scan.sa_delta_beta_params.scores.items():
                    results_db = results.require_group(str(cor))
                    for method in ScoreMethod:
                        if method is ScoreMethod.TOMO_CONSISTENCY:
                            continue
                        results_db[method.value] = score.get(method)

                    link_path = os.path.relpath(
                        url.file_path(),
                        os.path.dirname(process_file),
                    )
                    results_db["reconstructed_slice"] = h5py.ExternalLink(
                        link_path, url.data_path()
                    )
