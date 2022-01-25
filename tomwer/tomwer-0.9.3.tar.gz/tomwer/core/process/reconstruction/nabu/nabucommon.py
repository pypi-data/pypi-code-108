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
__date__ = "27/10/2021"


from distributed import client
from tomwer.core.cluster.cluster import (
    SlurmClusterConfiguration,
    patch_worker_info_to_worker,
)
from tomwer.core.process.reconstruction.nabu.target import Target
from tomwer.core.process.reconstruction.nabu.utils import _NabuPhaseMethod
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.utils.slurm import is_slurm_available
from silx.utils.enum import Enum as _Enum
from .slurm import _exec_nabu_on_slurm
from typing import Iterable, Optional
from typing import Union
import logging
import subprocess
from . import settings
from . import utils
from time import sleep
import os

_logger = logging.getLogger(__name__)
try:
    from nabu.pipeline.fullfield.local_reconstruction import (  # noqa F401
        ChunkedReconstructor,
    )
except (ImportError, OSError) as e:
    # import of cufft library can bring an OSError if cuda not install
    _logger.error(e)
    has_nabu = False
else:
    has_nabu = True


class NabuOutputFileFormat(_Enum):
    # NPY = 'npy'
    # NPZ = 'npz'
    TIFF = "tiff"
    HDF5 = "hdf5"
    JP2K = "jp2k"
    EDF = "edf"

    @classmethod
    def from_value(cls, value):
        if isinstance(value, str):
            value = value.lstrip(".")
        return super().from_value(value)


def get_file_format(file_str):
    extension = os.path.splitext(file_str.lower())[-1]
    extension = extension.lstrip(".")
    if extension in ("tiff", "tif"):
        return NabuOutputFileFormat.TIFF
    elif extension in ("hdf5", "hdf", "h5"):
        return NabuOutputFileFormat.HDF5
    elif extension in ("jp2k", "jpg2k"):
        return NabuOutputFileFormat.JP2K
    elif extension in ("edf",):
        return NabuOutputFileFormat.EDF
    else:
        raise ValueError(f"Unrecognized file extension {extension} from {file_str}")


class ResultsRun:
    """
    Base class of results for nabu
    """

    def __init__(self, success, config) -> None:
        self.__success = success
        self.__config = config

    @property
    def success(self) -> bool:
        return self.__success

    @property
    def config(self) -> dict:
        return self.__config

    def __str__(self) -> str:
        return f"result from nabu run: {'succeed' if self.success else 'failed'} with \n - config:{self.config} \n"


class ResultsWithStd(ResultsRun):
    """Nabu result with std"""

    def __init__(self, std_out, std_err, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__std_err = std_err
        self.__std_out = std_out

    @property
    def std_out(self) -> str:
        return self.__std_out

    @property
    def std_err(self) -> str:
        return self.__std_err

    def __str__(self) -> str:
        res = super().__str__()
        res += f"\n {self.std_out} \n {self.std_err}"
        return res


class ResultsLocalRun(ResultsWithStd):
    """Nabu result when run locally.
    If this is the case we should be able to retrieve directly the results urls"""

    def __init__(
        self,
        results_urls: tuple,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if not isinstance(results_urls, Iterable):
            raise TypeError(
                f"results_urls is expected to be an Iterable not {type(results_urls)}"
            )
        self.__results_urls = results_urls

    @property
    def results_urls(self) -> tuple:
        return self.__results_urls

    def __str__(self) -> str:
        res = super().__str__()
        res += f"\n - result urls: {self.results_urls}"
        return res


class ResultSlurmRun(ResultsWithStd):
    """Nabu result when run on slurm. on this case we expect to get a future and a distributed client"""

    def __init__(
        self,
        future_slurm_jobs: tuple,
        client,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__future_slurm_jobs = future_slurm_jobs
        self.client = client

    @property
    def future_slurm_jobs(self):
        return self.__future_slurm_jobs

    def __str__(self) -> str:
        res = super().__str__()
        res += f"\n - future job slurms: {self.future_slurm_jobs} \n - client: {client}"
        return res


class _NabuBaseReconstructor:
    """
    Base class to submit a job to nabu
    """

    TIMEOUT_SLURM_JOB_SUBMISSION = 30
    """Timeout when submit a job to slurm cluster. In second"""

    def __init__(
        self,
        scan: TomwerScanBase,
        dry_run: bool,
        target: Target,
        cluster_config: Optional[Union[dict, SlurmClusterConfiguration]],
        process_name: str,
    ) -> None:
        self._scan = scan
        self._target = Target.from_value(target)
        self._dry_run = dry_run
        self._process_name = process_name
        if isinstance(cluster_config, SlurmClusterConfiguration):
            self._cluster_config = cluster_config
        elif isinstance(cluster_config, dict):
            self._cluster_config = SlurmClusterConfiguration.from_dict(cluster_config)
        elif cluster_config is None:
            self._cluster_config = None
        else:
            raise TypeError(
                f"cluster config is expected to be a dict or an instance of {SlurmClusterConfiguration}. Not {type(cluster_config)}"
            )

    @property
    def scan(self):
        return self._scan

    @property
    def target(self):
        return self._target

    @property
    def cluster_config(self):
        return self._cluster_config

    @property
    def dry_run(self):
        return self._dry_run

    @property
    def process_name(self):
        return self._process_name

    def only_create_config_file(self):
        """Should we run the reconstruction or only create the configuration file"""
        return False

    def run(self) -> Iterable:
        """
        run the requested slices.

        :return: Iterable of ResultsRun.
        """
        raise NotImplementedError("Base class")

    def _process_config(
        self,
        config_to_dump: dict,
        config_file: str,
        file_format: str,
        start_z: Optional[int],
        end_z: Optional[int],
        info: Optional[str],
        process_name: str,
    ):
        """
        process provided configuration

        :param str info:
        """
        if self.dry_run is True or self.only_create_config_file():
            return ResultsRun(
                success=True,
                config=config_to_dump,
            )
        elif self.target is Target.LOCAL:
            _logger.info(f"run {info} for {self.scan} with {config_to_dump}")
            return self._run_nabu_locally(
                conf_file=config_file,
                file_format=file_format,
                config_to_dump=config_to_dump,
                start_z=start_z,
                end_z=end_z,
            )
        elif self.target is Target.SLURM:
            _logger.info(
                f"run {info} on slurm for {self.scan.path} with {config_to_dump}"
            )
            return self._run_nabu_on_slurm(
                conf_file=config_file,
                config_to_dump=config_to_dump,
                cluster_config=self.cluster_config.to_dict(),
                start_z=start_z,
                end_z=end_z,
                process_name=process_name,
                info=info,
            )
        else:
            raise ValueError(f"{self.target} is not recognized as a valid target")

    def _run_nabu_locally(
        self,
        conf_file: str,
        file_format: str,
        config_to_dump: dict,
        start_z: int,
        end_z: int,
    ) -> ResultsLocalRun:
        """
        run locally nabu for a single configuration file.

        :param str conf_file: path to the nabu .cfg file
        :param str file_format: format of the generated file
        :param dict config_to_dump: configuration saved in the .cfg as a dictionary
        :return: results of the local run
        :rtype: ResultsLocalRun
        """
        if not has_nabu:
            raise ImportError("Fail to import nabu")
        command = " ".join(
            ("python", "-m", settings.NABU_FULL_FIELD_APP_PATH, conf_file)
        )
        _logger.info('call nabu from "{}"'.format(command))
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=self.scan.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        outs, errs = process.communicate()

        recons_urls = utils.get_recons_urls(
            file_prefix=config_to_dump["output"]["file_prefix"],
            location=config_to_dump["output"]["location"],
            slice_index=None,
            scan=self.scan,
            file_format=file_format,
            start_z=start_z,
            end_z=end_z,
        )
        return ResultsLocalRun(
            success=len(recons_urls) > 0,
            results_urls=recons_urls,
            std_out=outs,
            std_err=errs,
            config=config_to_dump,  # config_slices,
        )

    def _run_nabu_on_slurm(
        self,
        conf_file: str,
        config_to_dump: dict,
        cluster_config: dict,
        start_z: int,
        end_z: int,
        process_name: str,
        info: str,
    ) -> ResultSlurmRun:
        """
        Run a nabu reconstruction on slurm of a single configuration

        :return: results of the slurm run
        :rtype: ResultSlurmRun
        """
        if not isinstance(conf_file, str):
            raise TypeError(f"conf_file is expected to be a strg not {type(conf_file)}")
        if not isinstance(config_to_dump, dict):
            raise TypeError(
                f"config_to_dump is expected to be a strg not {type(config_to_dump)}"
            )
        if not is_slurm_available():
            raise RuntimeError("slurm not available")
        if not isinstance(cluster_config, dict):
            raise ValueError(
                f"cluster config is expected to be a dict not {type(cluster_config)}"
            )
        from distributed import Client
        from tomwer.core.cluster import SlurmClusterManager

        # create slurm cluster
        project_name = cluster_config.get(
            "project_name", "tomwer_{scan}_-_{process}_-_{info}"
        )
        project_name = project_name.format(
            scan=str(self.scan), process=process_name, info=info
        )
        # project name should not contain any spaces as it will be integrated in a script and interpreted.
        project_name = project_name.replace(" ", "_")

        cluster = SlurmClusterManager().get_cluster(
            cluster_config,
            project_name=project_name,
        )
        client = Client(cluster)

        # do not rely on "cluster.workers", as it reports status=='running' when it's not actually ready
        timeout = self.TIMEOUT_SLURM_JOB_SUBMISSION
        loop_duration = 0.5
        while len(client.has_what()) != int(cluster_config["n_workers"]):
            timeout -= loop_duration
            if timeout == 0:
                raise TimeoutError(
                    f"unable to submit job to {cluster}. No workers spawn after {self.TIMEOUT_SLURM_JOB_SUBMISSION} seconds"
                )
            sleep(loop_duration)

        patch_worker_info_to_worker(client)
        # submit job
        future_slurm_job = client.submit(
            _exec_nabu_on_slurm,
            conf_file,
            self.scan.path,
        )

        callbacks = self._get_futures_slurm_callback(config_to_dump)
        assert isinstance(
            callbacks, tuple
        ), f"callbacks is expected to an instance of tuple and not {type(callbacks)}"
        for callback in callbacks:
            future_slurm_job.add_done_callback(callback.process)

        return ResultSlurmRun(
            success=True,
            config=config_to_dump,
            future_slurm_jobs=(future_slurm_job,),
            std_out=None,
            std_err=None,
            client=client,
        )

    def _get_futures_slurm_callback(self, config_to_dump) -> tuple:
        """Return a tuple a potential callback to be launch once the future is done"""
        return tuple()

    def _treateOutputSliceConfig(self, config):
        """
        - add or overwrite some parameters of the dictionary
        - create the output directory if does not exist
        """
        pag = False
        db = None
        if "phase" in config:
            if (
                "method" in config["phase"]
                and config["phase"]["method"] == _NabuPhaseMethod.PAGANIN.value
            ):
                pag = True
                if "delta_beta" in config["phase"]:
                    db = round(float(config["phase"]["delta_beta"]))
        if "output" in config:
            _file_name = self._get_file_basename_reconstruction(pag=pag, db=db)
            config["output"]["file_prefix"] = _file_name
            location = config["output"].get("location", None)
            if location not in ("", None):
                location = self.format_output_location(location, scan=self.scan)
                # if user specify the location
                if not os.path.isdir(config["output"]["location"]):
                    os.makedirs(location)
            else:
                # otherwise default location will be the data root level
                location = self.scan.path
            config["output"]["location"] = location
        return config

    def _get_file_basename_reconstruction(self, pag, db):
        """return created file base name"""
        raise NotImplementedError("Base class")

    @staticmethod
    def format_output_location(location, scan: TomwerScanBase):
        """
        format possible keys from the location like {scan_dir} or {scan_path}

        :param location:
        :param scan:
        :return:
        """
        if scan is None:
            _logger.warning("scan is !none, enable to format the nabu output location")

        keywords = {
            "scan_dir_name": scan.scan_dir_name(),
            "scan_basename": scan.scan_basename(),
            "scan_parent_dir_basename": scan.scan_parent_dir_basename(),
        }
        for keyword, value in keywords.items():
            if value is None:
                continue
            try:
                location = location.format(**{keyword: value})
            except KeyError:
                # then this mean scan_dir has not been provided
                pass
        return location
