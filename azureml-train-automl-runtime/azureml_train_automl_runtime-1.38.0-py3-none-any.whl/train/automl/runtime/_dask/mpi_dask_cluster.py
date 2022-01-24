# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import socket

from azureml.train.automl.runtime._dask.constants import Constants
from azureml.train.automl.runtime._dask.dask_processes import DaskScheduler, DaskWorker


class MpiDaskClsuter:
    """Handles Dask opeartions on an MPI cluster."""

    def __init__(self):
        self._client = None
        self._scheduler = None

    def start(self, start_woker_on_rank_0: bool = False) -> int:
        """Start up the Dask cluster."""
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()  # type: int

        # Rank 0 will be the scheduler node. Broadcast the scheduler IP to every node
        if rank == 0:
            # Start the Dask scheduler
            self._scheduler = DaskScheduler()
            self._scheduler.start()

            scheduler_ip = socket.gethostbyname(socket.gethostname())
            comm.bcast(scheduler_ip, root=0)

            if start_woker_on_rank_0:
                worker = DaskWorker()
                worker.start(scheduler_ip)

            from dask.distributed import Client
            self._client = Client('{}:{}'.format(scheduler_ip, Constants.SCHEDULER_PORT))
        else:
            scheduler_ip = comm.bcast(None, root=0)

            # Start a Dask worker
            worker = DaskWorker()
            worker.start(scheduler_ip)

            # Wait for the Dask worker process to end
            worker.wait()

        return rank

    def shutdown(self) -> None:
        """Shutdown the cluster."""
        if self._client:
            self._client.shutdown()
        if self._scheduler:
            self._scheduler.shutdown()
