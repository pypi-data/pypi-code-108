# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
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
__date__ = "26/10/2021"


import logging
from typing import Iterable, Optional
from processview.core.manager.manager import ProcessManager
from tomwer.core.cluster.cluster import SlurmClusterConfiguration
from tomwer.core.scan.futurescan import FutureTomwerScan
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.process.reconstruction.nabu.utils import check_sinogram_half
from . import utils
from . import settings
from nabu.pipeline.config import generate_nabu_configfile
from nabu.pipeline.fullfield.nabu_config import (
    nabu_config as nabu_fullfield_default_config,
)
from nabu import version as nabu_version
from tomwer.core.scan.edfscan import EDFTomoScan
import copy
import os
from tomwer.core.process.task import Task
from tomwer.io.utils.h5pyutils import EntryReader
from silx.io.utils import h5py_read_dataset
from .target import Target
import functools
from tomwer.utils import docstring
from .nabucommon import (
    _NabuBaseReconstructor,
    ResultsLocalRun,
    ResultSlurmRun,
)

_logger = logging.getLogger(__name__)


def run_volume_reconstruction(
    scan: TomwerScanBase,
    config: dict,
    dry_run: bool,
    process_id: Optional[int] = None,
) -> tuple:
    """
    Run a volume reconstruction. Scan need to have reconstruction parameters for nabu.

    Behavior: will clear link to the last volume reconstructed

    :param int process_id: optional process id

    :return: succeed, stdouts, stderrs, configs, future_scan
    :rtype: tuple
    """

    if scan.nabu_recons_params in ({}, None):
        raise ValueError(
            "no configuration provided. You should run a "
            "reconstruction from nabuslices first."
        )
    check_sinogram_half(scan)
    cluster_config = config.pop("cluster_config", None)
    if cluster_config == {}:
        cluster_config = None
    elif isinstance(cluster_config, SlurmClusterConfiguration):
        cluster_config = cluster_config.to_dict()

    if cluster_config is None:
        target = Target.LOCAL
    else:
        target = Target.SLURM

    config_volume = copy.copy(config)
    config_nabu_slices = copy.deepcopy(scan.nabu_recons_params)
    if "tomwer_slices" in config_nabu_slices:
        del config_nabu_slices["tomwer_slices"]

    if "phase" in config_nabu_slices and "delta_beta" in config_nabu_slices["phase"]:
        pag_dbs = utils.retrieve_lst_of_value_from_str(
            config_nabu_slices["phase"]["delta_beta"], type_=float
        )
        if len(pag_dbs) > 1:
            raise ValueError(
                "Several value of delta / beta found for volume reconstruction"
            )
    scan.clear_latest_vol_reconstructions()

    if process_id is not None:
        try:
            process_name = ProcessManager().get_process(process_id=process_id).name
        except KeyError:
            process_name = "unknow"
    else:
        process_name = ""

    volume_reconstructor = VolumeRunner(
        scan=scan,
        config_volume=config_volume,
        config_slices=config_nabu_slices,
        cluster_config=cluster_config,
        dry_run=dry_run,
        target=target,
        process_name=process_name,
    )
    try:
        results = volume_reconstructor.run()
    except TimeoutError as e:
        _logger.error(e)
        return None
    else:
        assert len(results) == 1, "only one volume should be reconstructed"
        res = results[0]
        # tag latest reconstructions
        if isinstance(res, ResultsLocalRun) and res.results_urls is not None:
            scan.set_latest_vol_reconstructions(res.results_urls)
        # create future if needed
        if isinstance(res, ResultSlurmRun):
            future_scan = FutureTomwerScan(
                scan=scan,
                futures=tuple(res.future_slurm_jobs),
                clients=[
                    res.client,
                ],
                process_requester_id=process_id,
            )

        else:
            future_scan = None
        succeed = res.success
        stdouts = (
            [
                res.std_out,
            ]
            if hasattr(res, "std_out")
            else []
        )
        stderrs = (
            [
                res.std_err,
            ]
            if hasattr(res, "std_err")
            else []
        )
        configs = (
            [
                res.config,
            ]
            if res is not None
            else []
        )
        return succeed, stdouts, stderrs, configs, future_scan


class VolumeRunner(_NabuBaseReconstructor):
    """
    Class used to reconstruct a full volume with Nabu.
    Locally or on a cluster.
    """

    def __init__(
        self,
        scan: TomwerScanBase,
        config_volume: dict,
        config_slices: dict,
        cluster_config: Optional[dict],
        dry_run: bool,
        target: Target,
        process_name: str,
    ) -> None:
        super().__init__(
            scan=scan,
            dry_run=dry_run,
            target=target,
            cluster_config=cluster_config,
            process_name=process_name,
        )
        self._config_volume = config_volume
        self._config_slices = config_slices

    @property
    def config_volume(self):
        return self._config_volume

    @property
    def config_slices(self):
        return self._config_slices

    @docstring(_NabuBaseReconstructor)
    def run(self) -> Iterable:
        dataset_params = self.scan.get_nabu_dataset_info()
        if "dataset" in self._config_slices:
            dataset_params.update(self._config_slices["dataset"])
        self._config_slices["dataset"] = dataset_params
        self._config_slices["resources"] = utils.get_nabu_resources_desc(
            scan=self.scan, workers=1, method="local"
        )

        # force overwrite results
        if "output" not in self.config_slices:
            self._config_slices["output"] = {}
        config_slices, extra_opts = self._treateOutputConfig(
            self.config_slices, self.config_volume
        )
        config_slices["output"].update({"overwrite_results": 1})

        cfg_folder = os.path.join(
            config_slices["output"]["location"], settings.NABU_CFG_FILE_FOLDER
        )
        if not os.path.exists(cfg_folder):
            os.makedirs(cfg_folder)

        name = (
            config_slices["output"]["file_prefix"] + settings.NABU_CONFIG_FILE_EXTENSION
        )
        if not isinstance(self.scan, EDFTomoScan):
            name = "_".join((self.scan.entry, name))
        conf_file = os.path.join(cfg_folder, name)
        _logger.info("{}: create {}".format(self.scan, conf_file))

        # add some tomwer metadata and save the configuration
        # note: for now the section is ignored by nabu but shouldn't stay that way
        with utils.TomwerInfo(config_slices) as config_to_dump:
            generate_nabu_configfile(
                conf_file,
                nabu_fullfield_default_config,
                config=config_to_dump,
                options_level="advanced",
            )

        return tuple(
            [
                self._process_config(
                    config_to_dump=config_to_dump,
                    config_file=conf_file,
                    start_z=config_to_dump["reconstruction"]["start_z"],
                    end_z=config_to_dump["reconstruction"]["end_z"],
                    info="nabu volume reconstruction",
                    file_format=config_slices["output"]["file_format"],
                    process_name=self.process_name,
                ),
            ]
        )

    @docstring(_NabuBaseReconstructor)
    def _get_futures_slurm_callback(self, config_to_dump) -> tuple:
        # add callback to set slices reconstructed urls
        class CallBack:
            # we cannot create a future directly because distributed enforce
            # the callback to have a function signature with only the future
            # as single parameter.
            def __init__(self, f_partial, scan) -> None:
                self.f_partial = f_partial
                self.scan = scan

            def process(self, fn):
                if fn.done() and not (fn.cancelled() or fn.exception()):
                    # update reconstruction urls only if processing succeed.
                    recons_urls = self.f_partial()
                    self.scan.add_latest_vol_reconstructions(recons_urls)

        file_format = config_to_dump["output"]["file_format"]
        callback = functools.partial(
            utils.get_recons_urls,
            file_prefix=config_to_dump["output"]["file_prefix"],
            location=config_to_dump["output"]["location"],
            file_format=file_format,
            scan=self.scan,
            slice_index=None,
            start_z=config_to_dump["reconstruction"]["start_z"],
            end_z=config_to_dump["reconstruction"]["end_z"],
        )

        return (CallBack(callback, self.scan),)

    def _treateOutputConfig(self, config_s, config_v) -> tuple:
        """

        :return: (nabu config dict, nabu extra options)
        """
        config_s = copy.deepcopy(config_s)
        config_s = super()._treateOutputSliceConfig(config_s)
        # adapt config_s to specific volume treatment
        if "postproc" in config_v:
            config_s["postproc"] = config_v["postproc"]

        extra_opts = config_v
        if "start_z" in extra_opts:
            config_s["reconstruction"]["start_z"] = extra_opts["start_z"]
            del extra_opts["start_z"]
        if "end_z" in extra_opts:
            config_s["reconstruction"]["end_z"] = extra_opts["end_z"]
            del extra_opts["end_z"]

        return config_s, extra_opts

    @docstring(_NabuBaseReconstructor)
    def _get_file_basename_reconstruction(self, pag, db):
        """

        :param TomwerScanBase scan: scan reconstructed
        :param Union[None, int] slice_index: index of the slice reconstructed.
                                            if None, we want to reconstruct the
                                            entire volume
        :param bool pag: is it a paganin reconstruction
        :param int db: delta / beta parameter
        :return: basename of the file reconstructed (without any extension)
        """
        assert type(db) in (int, type(None))
        if isinstance(self.scan, HDF5TomoScan):
            basename, _ = os.path.splitext(self.scan.master_file)
            basename = os.path.basename(basename)
        else:
            basename = os.path.basename(self.scan.path)
        if pag:
            return "_".join((basename + "pag", "db" + str(db).zfill(4), "vol"))
        else:
            return "_".join((basename, "vol"))


class NabuVolume(
    Task,
    input_names=("data", "nabu_params"),
    optional_input_names=("nabu_volume_params",),
    output_names=("data",),
):
    def __init__(self, varinfo=None, inputs=None, label=None):
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=label)
        self._dry_run = inputs.get("dry_run", False)

    def run(self):
        scan = self.inputs.data
        if self.inputs.nabu_params is None:
            raise ValueError("nabu params should be provided")
        if scan is None:
            self.outputs.data = None
            return
        if isinstance(scan, TomwerScanBase):
            scan = scan
        elif isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            raise ValueError("input type {} is not managed".format(scan))

        if scan.nabu_recons_params is None:
            raise ValueError(
                "scan need to have reconstruction parameters "
                'registered. Did you process "Nabu slices" '
                "already ?"
            )

        run_volume_reconstruction(
            scan=scan,
            config=self.get_configuration() or {},
            dry_run=self.dry_run,
        )
        # register result
        entry = "entry"
        if isinstance(scan, HDF5TomoScan):
            entry = scan.entry
        with scan.acquire_process_file_lock():
            self.register_process(
                process_file=scan.process_file,
                entry=entry,
                configuration=self.get_configuration(),
                results={},
                process_index=scan.pop_process_index(),
                overwrite=True,
            )
        self.outputs.data = scan

    def set_configuration(self, configuration: dict) -> None:
        Task.set_configuration(self, configuration=configuration)
        if "dry_run" in configuration:
            self.set_dry_run(bool(configuration["dry_run"]))

    @staticmethod
    def program_name():
        return "nabu-volume"

    @staticmethod
    def program_version():
        return nabu_version

    def set_dry_run(self, dry_run):
        self._dry_run = dry_run

    @property
    def dry_run(self):
        return self._dry_run

    def pathReceived(self, scan):
        return self.process(scan=scan)

    @staticmethod
    def retrieve_last_relative_cor(scan):
        with EntryReader(scan.process_file_url) as h5f:
            latest_nabu_node = Task.get_most_recent_process(h5f, NabuVolume)
            path = "configuration/reconstruction/rotation_axis_position"
            if path in latest_nabu_node:
                return h5py_read_dataset(latest_nabu_node[path])
