'''
this file is to initialize the compute platform, make sure to run this file before run the algorithm
'''
from .compute import Config_ini
from .compute.Config_ini import amend
from .compute.db import init_db
from .compute.gpu import run_detect_gpu

from .compute.file import init_work_dir_on_all_workers


def start_compute_platform():
    init_db()
    from .compute.redis import RedisLog
    RedisLog.run_dispatch_service()
    init_work_dir_on_all_workers()
    run_detect_gpu()


def run(alg_list, train_list, gpu_info_list):
    amend(alg_list, train_list, gpu_info_list)
    start_compute_platform()


