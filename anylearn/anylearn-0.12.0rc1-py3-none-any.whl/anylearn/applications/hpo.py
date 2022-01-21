from __future__ import annotations
import time
from typing import Dict, List,Optional, Union

from anylearn.applications.algorithm_manager import sync_algorithm
from anylearn.applications.hpo_experiment import HpoExperiment
from anylearn.applications.quickstart import (
    _get_or_create_dataset,
    _upload_dataset,
)
from anylearn.applications.utils import generate_random_name
from anylearn.interfaces import Project, ProjectVisibility
from anylearn.interfaces.resource import ResourceUploader
from anylearn.storage.db import DB
from anylearn.utils.errors import AnyLearnException


def run_hpo(hpo_search_space: dict,
            hpo_max_runs: int=10,
            hpo_max_duration: str="24h",
            hpo_tuner_name: str="TPE",
            hpo_mode: str="maximize",
            hpo_concurrency: int=1,
            project_name: Optional[str]=None,
            algorithm_id: Optional[str]=None,
            algorithm_name: Optional[str]=None,
            algorithm_dir: Optional[str]=None,
            algorithm_archive: Optional[str]=None,
            algorithm_entrypoint: Optional[str]=None,
            algorithm_output: Optional[str]=None,
            mirror_name: Optional[str]="QUICKSTART",
            dataset_id: Optional[str]=None,
            dataset_dir: Optional[str]=None,
            dataset_archive: Optional[str]=None,
            resource_uploader: Optional[ResourceUploader]=None,
            resource_polling: Union[float, int]=5,
            resource_timeout: Union[float, int]=120,
            dataset_hyperparam_name: str="dataset",
            gpu_num: int=1, # deprecated 0.11.1 - remove soon
            gpu_mem: int=0, # deprecated 0.11.1 - remove soon
            resource_request: Optional[List[Dict[str, Dict[str, int]]]]=None) -> HpoExperiment:
    """
    超参数自动调优接口。

    仅需提供调优配置参数和本地资源相关信息，
    即可在本地启动针对自定义算法/数据集的超参数自动调优，
    调优过程中使用Anylearn后端引擎进行多次训练，
    汇总到同一个训练项目中。

    目前接受的调优配置包括（详情参见本接口参数列表）：

    - 超参数搜索空间
    - 最大调优任务数（到量终止调优）
    - 最长调优总时间（到时终止调优）
    - 调优算法
    - 调优模式（最大化或最小化指标）
    - 端口绑定

    与本地快速训练类似，
    本接口封装了Anylearn从零启动训练的一些列流程。
    参见 :func:`~anylearn.applications.quickstart.quick_train` 。
    此外，自动调优的配置和构建过程也封装在接口内。

    Parameters
    ----------
    hpo_search_space : :obj:`dict`
        超参数搜索空间，格式详询 :obj:`NNI` 文档。
    hpo_max_runs : :obj:`int`, optional
        最大调优任务数，达成即终止实验。默认为 :obj:`10` 。
    hpo_max_duration : :obj:`str`, optional
        最长调优总时间，达成即终止实验。
        格式为 :obj:`数字 + s|m|h|d`，
        例如： 半天 :obj:`0.5d` ， 十分钟 :obj:`10m` 。
        默认为 :obj:`24h` 。
    hpo_tuner_name : :obj:`str`, optional
        调优算法名称。
        详见 `NNI内置调优算法 <https://nni.readthedocs.io/zh/stable/builtin_tuner.html>`_ 。
        默认为 :obj:`TPE` 。
    hpo_mode : :obj:`str`, optional
        调优模式，即，最大化或最小化指标。
        可选项： :obj:`maximize` 或 :obj:`minimize` 。
        默认为 :obj:`maximize` 。
    hpo_concurrency : :obj:`int`, optional
        调优期望并行度，即期望同时运行的任务数，实际并行度视后端资源调度情况而定。
        默认为 :obj:`1` 。
    project_name : :obj:`str`, optional
        将要创建的训练项目名称。如已传远程 :obj:`project_id` 则忽略。
    algorithm_id : :obj:`str`, optional
        已在Anylearn远程注册的算法ID。
    algorithm_name: :obj:`str`, optional
        指定的算法名称。
        注：同一用户的自定义算法的名称不可重复。
        如有重复，则复用已存在的同名算法，
        算法文件将被覆盖并提升版本。
        原有版本仍可追溯。
    algorithm_dir : :obj:`str`, optional
        本地算法目录路径。
    algorithm_archive : :obj:`str`, optional
        本地算法压缩包路径。
    algorithm_entrypoint : :obj:`str`, optional
        启动训练的入口命令。
    algorithm_output : :obj:`str`, optional
        训练输出模型的相对路径（相对于算法目录）。
    mirror_name : :obj:`str`, optional
        快速训练镜像名，默认为QUICKSTART。
    dataset_id : :obj:`str`, optional
        已在Anylearn远程注册的数据集ID。
    dataset_dir : :obj:`str`, optional
        本地数据集目录路径。
    dataset_archive : :obj:`str`, optional
        本地数据集压缩包路径。
    resource_uploader : :obj:`ResourceUploader`, optional
        资源上传实现。
        默认使用系统内置的同步上传器 :obj:`SyncResourceUploader` 。
    resource_polling : :obj:`float|int`, optional
        资源上传中轮询资源状态的时间间隔（单位：秒）。
        默认为5秒。
    resource_timeout : :obj:`float|int`, optional
        轮询状态的超时时长（单位：秒）。
        默认为120秒。
    dataset_hyperparam_name : :obj:`str`, optional
        启动训练时，数据集路径作为启动命令参数传入算法的参数名。
        需指定长参数名，如 :obj:`--data` ，并省略 :obj:`--` 部分传入。
        数据集路径由Anylearn后端引擎管理。
        默认为 :obj:`dataset` 。
    hyperparams : :obj:`dict`, optional
        训练超参数字典。
        超参数将作为训练启动命令的参数传入算法。
        超参数字典中的键应为长参数名，如 :obj:`--param` ，并省略 :obj:`--` 部分传入。
        默认为空字典。
    gpu_num : :obj:`int`, optional
        向Anylearn后端引擎请求的GPU数量，
        与 :obj:`gpu_mem` 参数互斥，
        同时设置时 :obj:`gpu_mem` 优先。
        默认为1。

        .. deprecated:: 0.11.1

            Use :obj:`resources_request` instead
            to specify QuotaGroup and resource request.

    gpu_mem : :obj:`int`, optional
        向Anylearn后端引擎请求的显存大小，
        与 :obj:`gpu_num` 参数互斥，
        同时设置时 :obj:`gpu_mem` 优先。
        默认为0。

        .. deprecated:: 0.11.1

            Use :obj:`resources_request` instead
            to specify QuotaGroup and resource request.

    resource_request : :obj:`List[Dict[str, Dict[str, int]]]`, optional
        单次训练所需计算资源的请求。
        如未填，则使用Anylearn后端的:obj:`default`资源组中的默认资源套餐。

    Returns
    -------
    HpoExperiment
        调参实验对象
    """
    # Algorithm
    algo = sync_algorithm(
        id=algorithm_id,
        name=algorithm_name,
        dir_path=algorithm_dir,
        archive_path=algorithm_archive,
        entrypoint_training=algorithm_entrypoint,
        output_training=algorithm_output,
        mirror_name=mirror_name,
        uploader=resource_uploader,
        polling=resource_polling,
    )

    # Dataset
    dset, dataset_archive, dataset_checksum = _get_or_create_dataset(
        id=dataset_id,
        dir_path=dataset_dir,
        archive_path=dataset_archive
    )
    if dataset_archive and dataset_checksum:
        # Local dataset registration
        _upload_dataset(dataset=dset,
                        dataset_archive=dataset_archive,
                        uploader=resource_uploader,
                        polling=resource_polling)
        DB().create_local_dataset(id=dset.id, checksum=dataset_checksum)

    # Project
    if not project_name:
        project_name = f"PROJ_{generate_random_name()}"
    project = Project(name=project_name,
                      description="SDK_HPO_EXPERIMENT",
                      visibility=ProjectVisibility.PRIVATE,
                      datasets=[dset.id])
    project.save()

    hpo = HpoExperiment(
        project_id=project.id,
        algorithm_id=algo.id,
        dataset_id=dset.id,
        hpo_search_space=hpo_search_space,
        hpo_max_runs=hpo_max_runs,
        hpo_max_duration=hpo_max_duration,
        hpo_tuner_name=hpo_tuner_name,
        hpo_mode=hpo_mode,
        hpo_concurrency=hpo_concurrency,
        dataset_hyperparam_name=dataset_hyperparam_name,
        resource_request=resource_request,
    )
    hpo.save()

    st = time.time()
    while not hpo.hpo_id:
        time.sleep(resource_polling)
        if time.time() > st + resource_timeout:
            raise AnyLearnException("调参实验启动超时")
        hpo.get_detail()

    return hpo
