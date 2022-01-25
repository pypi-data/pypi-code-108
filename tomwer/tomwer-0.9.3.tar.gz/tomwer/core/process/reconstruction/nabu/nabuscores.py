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

"""contain utils for score process
"""

__authors__ = [
    "H.Payno",
]
__license__ = "MIT"
__date__ = "28/10/2021"


try:
    from nabu.pipeline.fullfield.local_reconstruction import (  # noqa F401
        ChunkedReconstructor,
    )
except (ImportError, OSError):
    # import of cufft library can bring an OSError if cuda not install
    has_nabu = False
else:
    has_nabu = True
from typing import Iterable, Optional, Union

from processview.core.manager.manager import ProcessManager
from tomwer.core.process.reconstruction.nabu.target import Target
from tomwer.core.progress import Progress
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.scan.futurescan import FutureTomwerScan
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.utils.slurm import is_slurm_available
from tomwer.utils import docstring
from ..nabu import settings as nabu_settings
from tomwer.core.process.reconstruction.nabu.nabuslices import (
    SingleSliceRunner,
    generate_nabu_configfile,
    _NabuBaseReconstructor,
)
from nabu.pipeline.fullfield.nabu_config import (
    nabu_config as nabu_fullfield_default_config,
)
from .nabucommon import ResultSlurmRun, ResultsLocalRun, ResultsWithStd
from . import utils
import logging
import os

_logger = logging.getLogger(__name__)


def run_nabu_one_slice_several_config(
    scan: TomwerScanBase,
    nabu_configs: Union[list, tuple],
    cluster_config: Optional[dict],
    dry_run: bool,
    slice_index: Union[int, str],
    file_format: str,
    advancement: Optional[Progress] = None,
    process_id: Optional[int] = None,
) -> tuple:
    """
    Run several reconstruction of a specific slice.

    :param scan: dataset
    :param Iterable nabu_configs: set of nabu configurations to be run
    :param bool dry_run:
    :param int slice_index: slice index to reconstruct or "middle"
    :param Progress advancement: optional class to display advancement
    :param Optional[int] process_id: id of the process requesting this computation
    :param Optional[dict] cluster_config: cluster configuration if
    :return: success, recons_urls (list of output urls), tuple of outs, tuples of errs, dict future_scans (key is cor, value is future_scan)
    :rtype: tuple
    """
    if cluster_config in (None, {}):
        target = Target.LOCAL
    elif isinstance(cluster_config, dict):
        if not is_slurm_available():
            raise RuntimeError("Slurm computation requested but unvailable")
        target = Target.SLURM
    else:
        raise TypeError(
            f"cluster_config should be None or a dict not {type(cluster_config)}"
        )

    if process_id is not None:
        try:
            process_name = ProcessManager().get_process(process_id=process_id).name
        except KeyError:
            process_name = "unknow"
    else:
        process_name = ""

    reconstructor = _Reconstructor(
        scan=scan,
        nabu_configs=nabu_configs,
        advancement=advancement,
        slice_index=slice_index,
        target=target,
        dry_run=dry_run,
        file_format=file_format,
        cluster_config=cluster_config,
        process_name=process_name,
    )
    try:
        results = reconstructor.run()
    except TimeoutError as e:
        _logger.error(e)
        return None
    else:
        assert isinstance(
            results, dict
        ), "results should be a dictionary with cor as key and urls as value"
        success = True
        recons_urls = {}
        std_outs = []
        std_errs = []
        future_scans = {}
        for cor, res in results.items():
            success = success and res.success
            if isinstance(res, ResultsWithStd):
                std_outs.append(res.std_out)
                std_errs.append(res.std_err)
            if isinstance(res, ResultsLocalRun):
                recons_urls[cor] = res.results_urls
            if isinstance(res, ResultSlurmRun):
                future_scan = FutureTomwerScan(
                    scan=scan,
                    process_requester_id=process_id,
                    clients=(res.client,),
                    futures=res.future_slurm_jobs,
                )
                future_scans[cor] = future_scan
        return success, recons_urls, std_outs, std_errs, future_scans


class _Reconstructor(_NabuBaseReconstructor):
    def __init__(
        self,
        scan: TomwerScanBase,
        nabu_configs: Iterable,
        advancement: Optional[Progress],
        slice_index: Union[int, str],
        target: Target,
        dry_run: bool,
        file_format: str,
        cluster_config: Optional[dict],
        process_name: str,
    ) -> None:
        super().__init__(
            scan=scan,
            dry_run=dry_run,
            target=target,
            cluster_config=cluster_config,
            process_name=process_name,
        )
        if not isinstance(slice_index, (int, str)):
            raise TypeError(
                f"slice_index should be an int or a string not {type(slice_index)}"
            )

        self.advancement = advancement
        self.slice_index = slice_index
        self.nabu_configs = nabu_configs
        self.file_format = file_format

    @docstring(_NabuBaseReconstructor)
    def run(self) -> Iterable:
        if self.slice_index == "middle":
            if self.scan.dim_2 is not None:
                self.slice_index = self.scan.dim_2 // 2
            else:
                _logger.warning(
                    "scan.dim_2 returns None, unable to deduce middle " "pick 1024"
                )
                self.slice_index = 1024

        results = {}
        if self.advancement:
            self.advancement.setMaxAdvancement(len(self.nabu_configs))
        for cor, config in self.nabu_configs.items():
            config, conf_file = self.preprocess_config(config, cor)

            # add some tomwer metadata and save the configuration
            # note: for now the section is ignored by nabu but shouldn't stay that way
            with utils.TomwerInfo(config) as config_to_dump:
                generate_nabu_configfile(
                    conf_file,
                    nabu_fullfield_default_config,
                    config=config_to_dump,
                    options_level="advanced",
                )

            results[cor] = self._process_config(
                config_to_dump=config_to_dump,
                config_file=conf_file,
                file_format=self.file_format,
                start_z=None,
                end_z=None,
                info="nabu slice reconstruction",
                process_name=self.process_name,
            )
            # specific treatment for cor: rename output files
            if self.advancement:
                self.advancement.increaseAdvancement(1)
        return results

    def treateOutputConfig(self, _config, cor):
        """
        - add or overwrite some parameters of the dictionary
        - create the output directory if does not exist
        """
        pag = False
        db = None
        if "phase" in _config:
            if "method" in _config["phase"] and _config["phase"]["method"] not in (
                "",
                utils._NabuPhaseMethod.NONE.value,
            ):
                pag = True
                if "delta_beta" in _config["phase"]:
                    db = round(float(_config["phase"]["delta_beta"]))
        if "output" in _config:
            _file_name = SingleSliceRunner.get_file_basename_reconstruction(
                scan=self.scan, slice_index=self.slice_index, pag=pag, db=db
            )
            _config["output"]["file_prefix"] = "cor_{}_{}".format(_file_name, cor)
            if _config["output"]["location"] not in ("", None):
                # if user specify the location
                if not os.path.isdir(_config["output"]["location"]):
                    os.makedirs(_config["output"]["location"])
            else:
                # otherwise default location will be the data root level
                _config["output"]["location"] = os.sep.join(
                    self.scan.path, "saaxis_results"
                )
        if "reconstruction" not in _config:
            _config["reconstruction"] = {}
        _config["reconstruction"]["start_z"] = self.slice_index
        _config["reconstruction"]["end_z"] = self.slice_index
        return _config

    def preprocess_config(self, config, cor: float):
        dataset_params = self.scan.get_nabu_dataset_info()
        if "dataset" in config:
            dataset_params.update(config["dataset"])
        config["dataset"] = dataset_params

        config["resources"] = utils.get_nabu_resources_desc(
            scan=self.scan, workers=1, method="local"
        )
        # force overwrite results
        if "output" not in config:
            config["output"] = {}
        config["output"].update({"overwrite_results": 1})

        config = self.treateOutputConfig(config, cor=cor)
        # the policy is to save nabu .cfg file at the same location as the
        # force overwrite results

        cfg_folder = os.path.join(
            config["output"]["location"],
            nabu_settings.NABU_CFG_FILE_FOLDER,
        )
        if not os.path.exists(cfg_folder):
            os.makedirs(cfg_folder)

        name = (
            config["output"]["file_prefix"] + nabu_settings.NABU_CONFIG_FILE_EXTENSION
        )
        if not isinstance(self.scan, EDFTomoScan):
            name = "_".join((self.scan.entry, name))
        conf_file = os.path.join(cfg_folder, "cor_{}_{}".format(cor, name))
        return config, conf_file
