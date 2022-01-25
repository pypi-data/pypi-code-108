# coding: utf-8
# /*##########################################################################
# Copyright (C) 2017-2021 European Synchrotron Radiation Facility
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
Contains processing relative to a `Slurmcluster`
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "12/10/2021"


from distributed.client import Client
from tomwer.core.utils.Singleton import singleton as _singleton
from tomwer.core.settings import SlurmSettings as _SlurmSettings
from dask_jobqueue import SLURMCluster as _SLURMCluster
import os


class SlurmClusterConfiguration:
    """Object shipping the configuration of a slurm cluster"""

    def __init__(
        self,
        n_cores=_SlurmSettings.N_CORES_PER_WORKER,
        n_workers=_SlurmSettings.N_WORKERS,
        memory=_SlurmSettings.MEMORY_PER_WORKER,
        queue=_SlurmSettings.QUEUE,
        n_gpus=_SlurmSettings.N_GPUS_PER_WORKER,
        project_name=_SlurmSettings.PROJECT_NAME,
        walltime=_SlurmSettings.DEFAULT_WALLTIME,
        python_venv=_SlurmSettings.PYTHON_VENV,
        port_range=_SlurmSettings.PORT_RANGE,
        dashboard_port=_SlurmSettings.DASHBOARD_PORT,
    ) -> None:
        self._n_cores = n_cores
        self._n_workers = n_workers
        self._memory = memory
        self._queue = queue
        self._n_gpus = n_gpus
        self._project_name = project_name
        self._walltime = walltime
        self._python_venv = python_venv
        self._port_range = port_range
        self._dashboard_port = dashboard_port

    @property
    def n_cores(self):
        return self._n_cores

    @property
    def n_workers(self):
        return self._n_workers

    @property
    def memory(self):
        return self._memory

    @property
    def queue(self):
        return self._queue

    @property
    def n_gpus(self):
        return self._n_gpus

    @property
    def project_name(self):
        return self._project_name

    @property
    def walltime(self):
        return self._walltime

    @property
    def python_venv(self):
        return self._python_venv

    @property
    def port_range(self) -> tuple:
        """port range as (start:int, strop:int, step: int)"""
        return self._port_range

    @property
    def dashboard_port(self):
        return self._dashboard_port

    def to_dict(self) -> dict:
        return {
            "cores": self.n_cores,
            "n_workers": self.n_workers,
            "memory": self.memory,
            "queue": self.queue,
            "n_gpus": self.n_gpus,
            "project_name": self.project_name,
            "walltime": self.walltime,
            "python_venv": self.python_venv,
            "port_range": self.port_range,
            "dashboard_port": self.dashboard_port,
        }

    @staticmethod
    def from_dict(dict_: dict):
        return SlurmClusterConfiguration().load_from_dict(dict_=dict_)

    def load_from_dict(self, dict_: dict):
        if "cores" in dict_:
            self._n_cores = dict_["cores"]
        if "n_workers" in dict_:
            self._n_workers = dict_["n_workers"]
        if "memory" in dict_:
            self._memory = dict_["memory"]
        if "queue" in dict_:
            self._queue = dict_["queue"]
        if "n_gpus" in dict_:
            self._n_gpus = dict_["n_gpus"]
        if "project_name" in dict_:
            self._project_name = dict_["project_name"]
        if "walltime" in dict_:
            self._walltime = dict_["walltime"]
        if "python_venv" in dict_:
            self._python_venv = dict_["python_venv"]
        if "port_range" in dict_:
            self._port_range = dict_["port_range"]
        if "dashboard_port" in dict_:
            self._dashboard_port = dict_["dashboard_port"]
        return self


@_singleton
class SlurmClusterManager:
    def __init__(self) -> None:
        self._clusters = {}
        # associate at each cluster configuration a SLURMCluster

    def _config_dict_to_tuple(self, config: dict):
        return (
            config["cores"],
            config["n_workers"],
            config["memory"],
            config["n_gpus"],
            config["queue"],
            config["port_range"],
            config["dashboard_port"],
        )

    def get_cluster(self, config: dict, project_name: str) -> _SLURMCluster:
        n_gpus = config.get("n_gpus", None)
        job_extra = []
        if n_gpus not in (0, None):
            job_extra = ["--gres=gpu:{}".format(n_gpus)]

        import socket
        from contextlib import closing

        # from stackoverflow: https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
        def find_free_port():
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(("", 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return s.getsockname()[1]

        def dict_to_SLURMClusterParams(dict_):
            """convert a dict to valid parameter input"""
            python_venv = dict_.get("python_venv", None)
            host_port = find_free_port()
            dashboard_port = host_port
            while dashboard_port == host_port:
                dashboard_port = find_free_port()

            res = {
                "memory": f"{dict_['memory']}GB",
                "cores": dict_["cores"],
                "project": project_name,
                "queue": dict_["queue"],
                "job_extra": job_extra,
                "processes": 1,
                "scheduler_options": {
                    "host": "0.0.0.0:" + str(host_port),
                    "dashboard_address": "0.0.0.0:" + str(dashboard_port),
                },
                "walltime": dict_["walltime"],
            }
            if python_venv not in (None, ""):
                # warning: we need to provide both the executable and the
                # activation script because we will call some subprocess with python -m
                # anyway this is a better practice to have a 'logical' context.
                python_exe = os.path.join(python_venv, "bin", "python")
                python_activate = os.path.join(python_venv, "bin", "activate")
                res.update(
                    {
                        "python": python_exe,
                        "env_extra": ["source {}".format(python_activate)],
                    }
                )
            return res

        cluster_constructor_params = dict_to_SLURMClusterParams(config)
        new_cluster = _SLURMCluster(**cluster_constructor_params)
        new_cluster.scale(config["n_workers"])

        return new_cluster


def patch_worker_info_to_worker(client: Client):
    """simple function to patch the client with some extra information
    like the job_id
    """

    def get_job_id():
        return int(os.environ.get("SLURM_JOB_ID", -1))

    job_ids = {}
    for worker in client.has_what().keys():
        fut = client.submit(get_job_id, workers=[worker])
        job_ids[worker] = fut.result()

    client.job_ids = job_ids
