"""
This file is obsolete. Don't rely on it.
"""

from math import ceil
from socket import gethostname
from multiprocessing import cpu_count

from distributed import Client, get_worker, worker_client, LocalCluster, Nanny, SpecCluster, Scheduler

from ..utils import check_supported
from ..resources.computations import estimate_chunk_size
from ..resources.processconfig import ProcessConfig
from ..resources.gpu import pick_gpus
from ..resources.utils import get_memory_per_node, get_threads_per_node
from ..cuda.utils import collect_cuda_gpus
from ..opencl.utils import collect_opencl_gpus, collect_opencl_cpus, pick_opencl_cpu_platform
from ..app.logger import Logger, LoggerOrPrint
from ..app.process import WorkerProcess


def get_dataset(dataset_name, client=None):
    if client is None:
        with worker_client() as client:
            res = client.datasets[dataset_name]
    else:
        res = client.datasets[dataset_name]
    return res


def get_dask_worker():
    try:
        w = get_worker()
    except Exception as exc:
        w = None
    return w


def get_worker_resources(try_cuda=True, try_opencl=True):
    current_worker = get_worker()
    vm = virtual_memory()
    resources = {
        "worker_name": current_worker.name,
        "worker_addr": current_worker.address,
        "host": gethostname(),
        "mem_total_GB": vm.total / 1e9,
        "mem_avail_GB": vm.available / 1e9,
        "cpu_cores": cpu_count(),
        "cuda_gpus": {},
        "opencl_gpus": {},
    }
    if try_cuda:
        resources["cuda_gpus"] = collect_cuda_gpus()
    if try_opencl:
        resources["opencl_gpus"] = collect_opencl_gpus()
    return resources


def get_workers_resources(client, try_cuda=True, try_opencl=True):
    workers = list(client.has_what().keys())
    resources = {}
    for worker_addr in workers:
        f = client.submit(
            get_worker_resources, try_cuda=try_cuda, try_opencl=try_opencl,
            workers=[worker_addr], pure=False
        )
        resources[worker_addr] = f.result()
    return resources


def get_gpu_workers(workers_resources, max_gpu_per_worker=1):
    """
    Get the workers that can use a GPU.

    Parameters
    ----------
    workers_resources: dict
        Dictionary of workers resources obtained with `get_workers_resources`
    max_gpu_per_worker: int, optional
        Maximum GPUs allower per worker. If a worker can "see" more than
        `max_gpu_per_worker`, it will raise an error.
    Returns
    -------
    gpu_workers: dict
        Dictionary of workers that can use a GPU, along with the usable GPUs.
    nongpu_workers: list
        List of workers that cannot use a GPU
    """
    gpu_workers = {}
    nongpu_workers = []
    for worker_name, resources in workers_resources.items():
        w_gpus = {"cuda_gpus": {}, "opencl_gpus": {}}
        for gpu_type in ["cuda_gpus", "opencl_gpus"]:
            if gpu_type not in resources:
                continue
            gpus = resources[gpu_type] or {}
            if len(gpus) > max_gpu_per_worker:
                raise ValueError(
                    "Expected at most %d GPUs, got %d"
                    % (max_gpu_per_worker, len(gpus))
                )
            if len(gpus) == 0:
                continue
            w_gpus[gpu_type] = gpus
        if len(w_gpus["opencl_gpus"]) == 0 and len(w_gpus["cuda_gpus"]) == 0:
            nongpu_workers.append(worker_name)
        else:
            gpu_workers[worker_name] = w_gpus
    return gpu_workers, nongpu_workers




# TODO callbacks ? Several options:
#  - one callback after processing a chunk (i.e after this function)
#    either the worker or the client can do the callback (although data is on the worker side)
#  - one callback after each individual sub-processing (i.e phase retrieval, etc)
#    in this case, this should be registered in processing_options.
#    The callback is done on the worker side.
def worker_process_chunk(
    sub_region, chunk_size, chunk_id,
    logfile=None, loglevel="debug", extra_options=None,
    destroy_workerprocess_class=True,
):
    """
    Entry point for a `dask.distributed` `Worker`.

    Parameters
    -----------
    sub_region: tuple
        Tuple describing the region to process in the data volume, in the form
        `(start_x, end_x, start_z, end_z)`.
    chunk_size: int
        Size of the chunk ("delta z")
    chunk_id: int
        Index of the current chunk.
    logfile: str, optional
        Name of the log file.
    extra_options: dict
        Dictionary of extra options for `WorkerProcess`.
    """
    worker = get_worker()

    worker_conf = worker.client.datasets[worker.name]
    process_config = worker.client.datasets["process_config"]

    logname = "nabu-%s" % worker.name
    if logfile is None:
        logfile = logname + ".log"
    logger = Logger(logname, level=loglevel, logfile=logfile)

    ##
    extra_options = extra_options or {}
    extra_options["clear_gpu_memory_after_buildsino"] = True
    ##

    logger.debug("%s: spawning WorkerProcess" % worker.name)
    W = WorkerProcess(
        process_config, sub_region, chunk_size=chunk_size,
        use_cuda=worker_conf["use_cuda"], use_opencl=worker_conf["use_opencl"],
        logger=logger, extra_options=extra_options
    )
    logger.debug("%s: start processing chunk" % worker.name)
    W.process_chunk()
    # DEBUG
    if destroy_workerprocess_class:
        W._destroy_gpu_context()
        del W
        import gc
        gc.collect()
    #







def actor_process_chunk(sub_region, chunk_id):
    w = get_worker()
    worker_process = w.actors[list(w.actors.keys())[0]]
    worker_process.logger.info("Will process subregion %s" % str(sub_region))
    worker_process.process_chunk(sub_region=sub_region)










def _get_n_cpu_workers(n_cpu_workers, n_gpu_workers):
    if n_cpu_workers < 0:
        # (Poor) convention: total number of CPU workers
        return -n_cpu_workers
    # "X cpus workers by gpu worker
    return n_cpu_workers * n_gpu_workers




class WorkersManager:
    """
    A class for managing "Nabu workers". It has several purposes:
      - Get the requested computing resources from user-provided configuration
      - Get the available computing resources
      - Spwan the workers (either local or distributed)
      - Distribute the work to be done among workers (here chunks or images)
    """

    def __init__(self, process_config, logger=None, extra_options=None):
        """
        Initialize a WorkersManager.

        Parameters
        ----------
        process_config: `nabu.resources.processing.ProcessConfig`
            Structure describing the user parameters and dataset.
        logger: `logging.logger` or `nabu.app.logger.Logger`, optional
            Logging object.
        extra_options: dict, optional
            Dictionary of advanced options. Current options are:
               - gpu_pick_method: "cuda" or "auto"
               - chunk_size_method: "same" or "cpugpu"
               - max_chunk_size: int
        """
        self.process_config = process_config
        self.logger = LoggerOrPrint(logger)
        self._set_extra_options(extra_options)
        self._get_requested_resources()


    def _set_extra_options(self, extra_options):
        if extra_options is None:
            extra_options = {}
        advanced_options = {
            "gpu_pick_method": "cuda",
            "chunk_size_method": "same",
            "max_chunk_size": None,
        }
        advanced_options.update(extra_options)
        self.extra_options = advanced_options
        self._max_chunk_size = self.extra_options["max_chunk_size"]


    def _get_requested_resources(self):
        resources_cfg = self.process_config.nabu_config["resources"]
        self.distribution_method = resources_cfg["method"]
        #
        if self.distribution_method == "slurm":
            raise NotImplementedError()
        #
        gpu_ids = resources_cfg["gpu_id"]
        n_gpu_workers = resources_cfg["gpus"]
        n_cpu_workers = _get_n_cpu_workers(resources_cfg["cpu_workers"], n_gpu_workers)
        if (n_cpu_workers == 0) and (n_gpu_workers == 0):
            raise ValueError("Got 0 CPU workers and 0 GPU workers. Need at least one worker.")
        self.n_gpu_workers = n_gpu_workers
        self.n_cpu_workers = n_cpu_workers


    def _configure_chunk_size_same(self):
        """
        Configure the chunk size used by workers.
        In this approach, the same chunk size is used for all workers.
           Pros: simpler, especially when it comes to distribute work with client.submit()
           Cons: if max_available_chunk_size differs too much between workers, might be inefficient
        """
        chunk_sizes = []
        for worker_name, worker_desc in self.workers.items():
            chunk_sizes.append(worker_desc["chunk_size"])
        self._common_chunk_size = min(chunk_sizes)
        if self._max_chunk_size is not None:
            self._common_chunk_size = min(self._max_chunk_size, chunk_sizes)
        self._chunk_sizes = dict.fromkeys(self.workers.keys(), self._common_chunk_size)


    def _configure_chunk_size_cpu_gpu(self, gpu_cpu_ratio=2):
        """
        Configure the chunk size used by workers.
        In this approach, we use a different chunk size for GPU workers and CPU
        workers. The rationale is that GPU workers are likely to process their
        chunk much faster, so we decrease the chunk size of CPU worker by a certain
        factor in order to re-equilibrate workload.
        """
        res = {}
        for worker_name, worker_desc in self.workers.items():
            chunk_size = worker_desc["chunk_size"]
            if worker_desc["type"] == "CPU":
                chunk_size = chunk_size / gpu_cpu_ratio
            res[worker_name] = chunk_size
        self._chunk_sizes = res


    def _configure_chunk_size(self):
        method = self.extra_options["chunk_size_method"]
        if method == "same":
            self._configure_chunk_size_same()
        elif method == "cpugpu":
            self._configure_chunk_size_cpu_gpu()
        else:
            raise ValueError("Unknown chunk size method")



class LocalWorkersManager(WorkersManager):

    def __init__(self, process_config, logger=None, extra_options=None, scheduler_kwargs=None):
        """
        Initialize a LocalWorkersManager.

        Parameters
        ----------
        process_config: `nabu.resources.processing.ProcessConfig`
            Structure describing the user parameters and dataset.
        logger: `logging.logger` or `nabu.app.logger.Logger`, optional
            Logging object.
        extra_options: dict, optional
            Dictionary of advanced options. Current options are:
               - gpu_pick_method: "cuda" or "auto"
        scheduler_kwargs: dict, optional
            Extra options to pass to `distributed.Scheduler`.
        """
        super().__init__(process_config, logger=logger, extra_options=extra_options)
        self.scheduler_kwargs = scheduler_kwargs or {}
        self._configure_worker_resources()
        self._spawn_workers()
        self._estimate_workers_chunk_size()
        self._configure_workers_options()
        self._create_tasks()
        self._spawn_workers_pipelines()


    def _configure_worker_resources(self):
        resources_cfg = self.process_config.nabu_config["resources"]
        # Get memory per worker
        mem_per_node = resources_cfg["memory_per_node"]
        memory = get_memory_per_node(mem_per_node[0], is_percentage=mem_per_node[1]) * 1e9
        # Get threads per node
        threads_per_node = resources_cfg["threads_per_node"]
        threads = get_threads_per_node(threads_per_node[0], is_percentage=threads_per_node[1])
        # Pick GPUs
        self.gpus = pick_gpus(
            self.extra_options["gpu_pick_method"],
            collect_cuda_gpus(),
            collect_opencl_gpus(),
            self.n_gpu_workers
        )
        # Pick CPU
        self.cpu = None
        if self.n_cpu_workers > 0:
            self.cpu = pick_opencl_cpu_platform(collect_opencl_cpus())
        # GPU workers specification
        n_workers = self.n_cpu_workers + self.n_gpu_workers
        gpu_workers_spec = {}
        workers = {}
        mem_used_by_gpu_workers = 0
        for i in range(self.n_gpu_workers):
            mem_limit = min(memory/n_workers, self.gpus[i]["memory_GB"] * 1e9 * 2)
            mem_used_by_gpu_workers += mem_limit
            worker_name = "GPU-worker-%02d" % i
            gpu_workers_spec[i] = {
                "cls": Nanny,
                "options": {
                    "nthreads": 1, #2,
                    "name": worker_name,
                    "memory_limit": mem_limit,
                },
            }
            workers[worker_name] = {
                "name": worker_name,
                "CPU_memory_GB": mem_limit / 1e9,
                "GPU": self.gpus[i],
            }
        # CPU workers specification
        cpu_workers_spec = {}
        for i in range(self.n_cpu_workers):
            mem_limit = (memory - mem_used_by_gpu_workers)/n_workers
            worker_name = "CPU-worker-%02d" % i
            cpu_workers_spec[self.n_gpu_workers + i] = {
                "cls": Nanny,
                "options": {
                    "nthreads": int((threads - 2*self.n_gpu_workers)/self.n_cpu_workers),
                    "name": worker_name,
                    "memory_limit": mem_limit,
                },
            }
            workers[worker_name] = {
                "name": worker_name,
                "CPU_memory_GB": mem_limit / 1e9
            }
        self.workers = workers
        self._gpu_workers_spec = gpu_workers_spec
        self._cpu_workers_spec = cpu_workers_spec
        self._workers_spec = {}
        self._workers_spec.update(self._gpu_workers_spec)
        self._workers_spec.update(self._cpu_workers_spec)


    def _spawn_workers(self):
        self.logger.debug("Creating SpecCluster()")
        self.scheduler_spec = {
            "cls": Scheduler,
            "options": self.scheduler_kwargs
        }
        self.cluster = SpecCluster(
            scheduler=self.scheduler_spec,
            workers=self._workers_spec
         )
        self.client = Client(self.cluster.scheduler_address)
        self._get_workers_addresses()


    def _get_workers_addresses(self):
        def get_worker_name_type():
             curr_worker = get_worker()
             worker_type = "GPU" if "GPU" in curr_worker.name else "CPU"
             return curr_worker.name, worker_type
        for worker_addr in self.client.has_what().keys():
            f = self.client.submit(get_worker_name_type, workers=[worker_addr], pure=False)
            w_name, w_type = f.result()
            self.workers[w_name].update({"type": w_type, "address": worker_addr})


    def _estimate_workers_chunk_size(self):
        self.logger.debug("Estimating workers chunk size")
        chunks = {}
        for worker_name in self.workers.keys():
            worker_resources = self.workers[worker_name]
            mem = worker_resources["CPU_memory_GB"]
            if self.workers[worker_name]["type"] == "GPU":
                mem = min(mem, worker_resources["GPU"]["memory_GB"]*0.95)
            self.workers[worker_name]["chunk_size"] = estimate_chunk_size(
                mem, self.process_config, chunk_step=20
            )


    def _configure_workers_options(self):
        self.client.datasets.clear() # not mandatory
        workers_conf = {"process_config": self.process_config}
        # Enable/Disable cuda for GPU/CPU workers
        for worker_name, worker_desc in self.workers.items():
            workers_conf[worker_name] = {}
            use_cuda = (worker_desc["type"] == "GPU")
            use_opencl = not(use_cuda) #
            workers_conf[worker_name]["use_cuda"] = use_cuda
            workers_conf[worker_name]["use_opencl"] = use_opencl
            self.workers[worker_name]["use_cuda"] = use_cuda
            self.workers[worker_name]["use_opencl"] = use_opencl
        # Broadcast
        self.client.datasets.update(workers_conf)


    def _create_tasks(self):
        cfg = self.process_config.nabu_config
        start_z = cfg["reconstruction"]["start_z"]
        end_z = cfg["reconstruction"]["end_z"]
        self._configure_chunk_size()
        tasks = []
        # method == "same"
        # TODO implement other methods
        chunk_size = self._common_chunk_size
        n_chunks = ceil((end_z - start_z)/chunk_size)
        for chunk_id in range(n_chunks):
            sub_region = (
                None, None,
                start_z + chunk_id * chunk_size,
                min(end_z, start_z + (chunk_id + 1) * chunk_size)
            )
            # ~ tasks.append((sub_region, chunk_size, chunk_id))
            tasks.append((sub_region, chunk_id))
        self._tasks = tasks


    def _spawn_workers_pipelines(self):
        actors = {}
        for worker_name, worker_conf in self.workers.items():
            fut = self.client.submit(
                WorkerProcess,
                self.process_config,
                (None, None, 0, worker_conf["chunk_size"]), # placeholder !
                chunk_size=worker_conf["chunk_size"],
                use_cuda=worker_conf["use_cuda"],
                use_opencl=worker_conf["use_opencl"],
                logger=None, # TODO
                extra_options={"clear_gpu_memory_when_possible": True},
                workers=[worker_conf["address"]],
                actor=True
            )
            actors[worker_name] = fut.result()
        self._actors = actors


    def get_workers_type(self, worker_type):
        """
        Return the address of a type of worker.

        Parameters
        -----------
        worker_type: str
            Type of worker. Can be "CPU" or "GPU".
        """
        return list(filter(lambda x: x["type"] == worker_type, self.workers.values()))


    # WIP !
    def reconstruct_volume(self):
        futures = []
        for task in self._tasks:
            f = self.client.submit(
                # ~ worker_process_chunk,
                actor_process_chunk,
                *task
            )
            futures.append(f)
        self.futures = futures



'''

    LOCAL
    -------
    memory needed
        gpu worker: 2.5*gpu mem
        cpu worker: avail_mem / n_cpu_workers

    limit:
        upper_tot = min(sys_avail_mem, user_requested_mem["memory_per_node"])
        upper_worker = upper_tot/n_workers


    DISTRIBUTED
    -----------
    one gpu worker comes with its cpu companion
    we assume there are 2 gpus per node, so we take sys_avail_mem/2 at most




'''
