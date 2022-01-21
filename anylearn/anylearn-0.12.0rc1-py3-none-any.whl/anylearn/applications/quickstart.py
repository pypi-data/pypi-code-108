import copy
import json
from pathlib import Path
from threading import Thread
import time
from typing import Dict, List, Optional, Union

from anylearn.utils.func import generate_primary_key
from anylearn.applications.train_profile import TrainProfile
from .algorithm_manager import sync_algorithm
from .utils import (
    _check_resource_input,
    _get_archive_checksum,
    _get_or_create_resource_archive,
    generate_random_name,
    make_name_by_path,
)
from ..interfaces import (
    EvaluateSubTask,
    EvaluateTask,
    Project,
    ProjectVisibility,
    QuotaGroup,
    TrainTask,
)
from ..interfaces.resource import (
    Algorithm,
    Dataset,
    Model,
    Resource,
    ResourceState,
    ResourceUploader,
    ResourceVisibility,
    SyncResourceUploader,
)
from ..storage.db import DB
from ..utils import logger
from ..utils.errors import (
    AnyLearnException,
    AnyLearnMissingParamException,
    AnylearnRequiredLocalCommitException,
)


def _get_or_create_dataset(id: Optional[str]=None,
                           dir_path: Optional[Union[str, Path]]=None,
                           archive_path: Optional[str]=None):
    if not any([id, dir_path, archive_path]):
        return None, None, None
    try:
        dset = Dataset(id=id, load_detail=True)
        return dset, None, None
    except:
        if not any([dir_path, archive_path]):
            raise AnyLearnMissingParamException((
                "ID provided does not exist and none of "
                "['dir_path', 'archive_path'] "
                "is specified."
            ))
        name = make_name_by_path(dir_path or archive_path)
        archive_path = _get_or_create_resource_archive(
            name=name,
            dir_path=dir_path,
            archive_path=archive_path
        )
        checksum = _get_archive_checksum(archive_path)
        local_id = DB().find_local_dataset_by_checksum(checksum=checksum)
        if local_id:
            try:
                return Dataset(id=local_id, load_detail=True), None, None
            except:
                logger.warning(
                    f"Local dataset ({local_id}) "
                    "has been deleted remotely, "
                    "forced to re-registering dataset."
                )
                DB().delete_local_dataset(id=local_id)
        dset = Dataset(name=name, description="SDK_QUICKSTART",
                       visibility=ResourceVisibility.PRIVATE,
                       filename=f"{name}.zip",
                       is_zipfile=True)
        dset.save()
        return dset, archive_path, checksum


def _get_or_create_model(id: Optional[str]=None,
                         dir_path: Optional[Union[str,Path]]=None,
                         archive_path: Optional[str]=None,
                         algorithm: Optional[Algorithm]=None):
    _check_resource_input(id, dir_path, archive_path)
    try:
        model = Model(id=id, load_detail=True)
        return model, None, None
    except:
        if not any([dir_path, archive_path]):
            raise AnyLearnMissingParamException((
                "ID provided does not exist and none of "
                "['dir_path', 'archive_path'] "
                "is specified."
            ))
        if not algorithm or not algorithm.id:
            raise AnyLearnMissingParamException(
                "Parameter 'algorithm' should be specified "
                "when using local models."
            )
        name = make_name_by_path(dir_path or archive_path)
        archive_path = _get_or_create_resource_archive(
            name=name,
            dir_path=dir_path,
            archive_path=archive_path
        )
        checksum = _get_archive_checksum(archive_path)
        local_id = DB().find_local_model_by_checksum(checksum=checksum)
        if local_id:
            try:
                # Fetch remote model and update (eventually) related algo
                model = Model(id=local_id, load_detail=True)
                model.algorithm_id = algorithm.id
                model.save()
                return model, None, None
            except:
                logger.warning(
                    f"Local model ({local_id}) "
                    "has been deleted remotely, "
                    "forced to re-registering model."
                )
                DB().delete_local_model(id=local_id)
        model = Model(name=name, description="SDK_QUICKSTART",
                      visibility=ResourceVisibility.PRIVATE,
                      filename=f"{name}.zip",
                      is_zipfile=True,
                      algorithm_id=algorithm.id)
        model.save()
        return model, archive_path, checksum


def _upload_dataset(dataset: Dataset,
                    dataset_archive: str,
                    uploader: Optional[ResourceUploader]=None,
                    polling: Union[float, int]=5):
    if not uploader:
        uploader = SyncResourceUploader()
    t_dataset = Thread(target=Resource.upload_file,
                    kwargs={
                        'resource_id': dataset.id,
                        'file_path': dataset_archive,
                        'uploader': uploader,
                    })
    logger.info(f"Uploading dataset {dataset.name}...")
    t_dataset.start()
    t_dataset.join()
    finished = [ResourceState.ERROR, ResourceState.READY]
    while dataset.state not in finished:
        time.sleep(polling)
        dataset.get_detail()
    if dataset.state == ResourceState.ERROR:
        raise AnyLearnException("Error occured when uploading dataset")
    logger.info("Successfully uploaded dataset")


def _upload_model(model: Model,
                  model_archive: str,
                  uploader: Optional[ResourceUploader]=None,
                  polling: Union[float, int]=5):
    if not uploader:
        uploader = SyncResourceUploader()
    t_model = Thread(target=Resource.upload_file,
                    kwargs={
                        'resource_id': model.id,
                        'file_path': model_archive,
                        'uploader': uploader,
                    })
    logger.info(f"Uploading dataset {model.name}...")
    t_model.start()
    t_model.join()
    finished = [ResourceState.ERROR, ResourceState.READY]
    while model.state not in finished:
        time.sleep(polling)
        model.get_detail()
    if model.state == ResourceState.ERROR:
        raise AnyLearnException("Error occured when uploading model")
    logger.info("Successfully uploaded model")


def _get_or_create_default_project():
    try:
        return Project.get_my_default_project()
    except:
        return Project.create_my_default_project()


def _get_or_create_project(project_id: Optional[str]=None,
                           project_name: Optional[str]=None):
    try:
        return Project(id=project_id, load_detail=True)
    except:
        name = project_name or f"PROJ_{generate_random_name()}"
        description = project_name or "SDK_QUICKSTART"
        project = Project(name=name, description=description,
                          visibility=ProjectVisibility.PRIVATE)
        project.save()
        return project


def _format_resource_request(resource_request: List[Dict[str, Dict[str, int]]]):
    if not resource_request:
        return None
    # Resource group by ID or name
    for i, req in enumerate(copy.deepcopy(resource_request)):
        for key, val in req.items():
            if key in ['default', 'besteffort'] or key.startswith('QGRP'):
                # Already ID
                continue
            try:
                qid = QuotaGroup(name=key, load_detail=True).id
            except AnyLearnException:
                raise AnyLearnException(f"Failed to find QuotaGroup: {key}")
            resource_request[i][qid] = val
            del resource_request[i][key]
    return resource_request


def _create_train_task(name: str,
                       algorithm: Algorithm,
                       project: Project,
                       hyperparams: dict,
                       mounts: Optional[Dict[str, Resource]]=None,
                       algorithm_git_ref: Optional[str]=None,
                       resource_request: Optional[List[Dict[str, Dict[str, int]]]]=None,
                       description: Optional[str]=None):
    files = [v.id for v in mounts.values()]
    train_params = dict(
        {k: f"${v.id}" for k, v in mounts.items()},
        **hyperparams,
    )
    train_task = TrainTask(
        name=name,
        project_id=project.id,
        algorithm_id=algorithm.id,
        algorithm_git_ref=algorithm_git_ref,
        files=files,
        train_params=json.dumps(train_params),
        resource_request=resource_request,
        description=description,
    )
    train_task.save()
    train_task.get_detail()
    return train_task


def _create_eval_task(name: str,
                      model: Model,
                      dataset: Dataset,
                      model_hyperparam_name: str, 
                      dataset_hyperparam_name: str,
                      hyperparams: dict,
                      gpu_num: int=1):
    eval_params = dict({
                           model_hyperparam_name: f"${model.id}",
                           dataset_hyperparam_name: f"${dataset.id}",
                       },
                       **hyperparams)
    eval_task = EvaluateTask(name=name,
                             sub_tasks=[
                                 EvaluateSubTask(model_id=model.id,
                                                 files=[dataset.id],
                                                 evaluate_params=eval_params,
                                                 gpu_num=gpu_num)
                             ])
    eval_task.save()
    eval_task.get_detail()
    return eval_task


def quick_train(algorithm_id: Optional[str]=None,
                algorithm_name: Optional[str]=None,
                algorithm_dir: Optional[Union[str, Path]]=None,
                algorithm_archive: Optional[str]=None, # deprecated in 0.11.11, remove in 0.12.3
                algorithm_force_update: bool=False,
                algorithm_git_ref: Optional[str]=None,
                dataset_hyperparam_name: str="dataset",
                dataset_id: Optional[str]=None,
                dataset_dir: Optional[Union[str, Path]]=None,
                dataset_archive: Optional[str]=None,
                model_hyperparam_name: str="model",
                model_id: Optional[str]=None,
                pretrain_hyperparam_name: str="pretrain",
                pretrain_task_id: Optional[str]=None,
                project_id: Optional[str]=None,
                project_name: Optional[str]=None,
                entrypoint: Optional[str]=None,
                output: Optional[str]=None,
                mirror_name: Optional[str]="QUICKSTART",
                resource_uploader: Optional[ResourceUploader]=None,
                resource_polling: Union[float, int]=5,
                hyperparams: dict={},
                resource_request: Optional[List[Dict[str, Dict[str, int]]]]=None,
                task_description: Optional[str]=None):
    """
    本地算法快速训练接口。

    仅需提供本地资源和训练相关的信息，
    即可在Anylearn后端引擎启动自定义算法/数据集的训练：
    
    - 算法路径（文件目录或压缩包）
    - 数据集路径（文件目录或压缩包）
    - 训练启动命令
    - 训练输出路径
    - 训练超参数

    本接口封装了Anylearn从零启动训练的一系列流程：

    - 算法注册、上传
    - 数据集注册、上传
    - 训练项目创建
    - 训练任务创建

    本地资源初次在Anylearn注册和上传时，
    会在本地记录资源的校验信息。
    下一次调用快速训练或快速验证接口时，
    如果提供了相同的资源信息，
    则不再重复注册和上传资源，
    自动复用远程资源。

    如有需要，也可向本接口传入已在Anylearn远程注册的算法或数据集的ID，
    省略资源创建的过程。

    Parameters
    ----------
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

        .. deprecated:: 0.12.0

            Not supported anymore.

    algorithm_git_ref : :obj:`str`, optional
        算法Gitea代码仓库的版本号（可以是commit号、分支名、tag名）。
        使用本地算法时，如未提供此参数，则取本地算法当前分支名。
    algorithm_force_update : :obj:`bool`, optional
        在同步算法的过程中是否强制更新算法，如为True，Anylearn会对未提交的本地代码变更进行自动提交。默认为False。
    dataset_hyperparam_name : :obj:`str`, optional
        启动训练时，数据集路径作为启动命令参数传入算法的参数名。
        需指定长参数名，如 :obj:`--data` ，并省略 :obj:`--` 部分传入。
        数据集路径由Anylearn后端引擎管理。
        默认为 :obj:`dataset` 。
    dataset_id : :obj:`str`, optional
        已在Anylearn远程注册的数据集ID。
    dataset_dir : :obj:`str`, optional
        本地数据集目录路径。
    dataset_archive : :obj:`str`, optional
        本地数据集压缩包路径。
    model_hyperparam_name : :obj:`str`, optional
        启动训练时，模型路径作为启动命令参数传入算法的参数名。
        需指定长参数名，如 :obj:`--model` ，并省略 :obj:`--` 部分传入。
        模型路径由Anylearn后端引擎管理。
        默认为 :obj:`model` 。
    model_id : :obj:`str`, optional
        已在Anylearn远程注册/转存的模型ID。
    pretrain_hyperparam_name: :obj:`str`, optional
        启动训练时，前置训练结果（间接抽象为“预训练”，即"pretrain"）路径作为启动命令参数传入算法的参数名。
        需指定长参数名，如 :obj:`--pretrain` ，并省略 :obj:`--` 部分传入。
        预训练结果路径由Anylearn后端引擎管理。
        默认为 :obj:`pretrain` 。
    pretrain_task_id: :obj:`str`, optional
        在Anylearn进行过的训练的ID，一般为前缀TRAI的32位字符串。
        Anylearn会对指定的训练进行结果抽取并挂载到新一次的训练中。
    project_id : :obj:`str`, optional
        已在Anylearn远程创建的训练项目ID。
    entrypoint : :obj:`str`, optional
        启动训练的入口命令。
    output : :obj:`str`, optional
        训练输出模型的相对路径（相对于算法目录）。
    resource_uploader : :obj:`ResourceUploader`, optional
        资源上传实现。
        默认使用系统内置的同步上传器 :obj:`SyncResourceUploader` 。
    resource_polling : :obj:`float|int`, optional
        资源上传中轮询资源状态的时间间隔（单位：秒）。
        默认为5秒。
    hyperparams : :obj:`dict`, optional
        训练超参数字典。
        超参数将作为训练启动命令的参数传入算法。
        超参数字典中的键应为长参数名，如 :obj:`--param` ，并省略 :obj:`--` 部分传入。
        如需要标识类参数（flag），可将参数的值设为空字符串，如 :obj:`{'my-flag': ''}` ，等价于 :obj:`--my-flag` 传入训练命令。
        默认为空字典。
    resource_request : :obj:`List[Dict[str, Dict[str, int]]]`, optional
        训练所需计算资源的请求。
        如未填，则使用Anylearn后端的:obj:`default`资源组中的默认资源套餐。
    task_description : :obj:`str`, optional
        训练任务详细描述。

    Returns
    -------
    TrainTask
        创建的训练任务对象
    Algorithm
        在快速训练过程中创建或获取的算法对象
    Dataset
        在快速训练过程中创建或获取的数据集对象
    Project
        创建的训练项目对象
    """
    # Resource request
    resource_request = _format_resource_request(resource_request)

    # Remote odel
    model = Model(id=model_id, load_detail=True) if model_id else None

    # Remote pretrain task results
    pretrain_task = (
        TrainTask(id=pretrain_task_id, load_detail=True)
        if pretrain_task_id
        else None
    )

    # Algorithm
    try:
        algo, current_sha = sync_algorithm(
            id=algorithm_id,
            name=algorithm_name,
            dir_path=algorithm_dir,
            entrypoint_training=entrypoint,
            output_training=output,
            mirror_name=mirror_name,
            uploader=resource_uploader,
            polling=resource_polling,
            force=algorithm_force_update,
        )
    except AnylearnRequiredLocalCommitException:
        # Notify possible usage of algorithm_force_update=True
        raise AnylearnRequiredLocalCommitException(
            f"Algorithm dir {algorithm_dir} is not clean. "
            "Please commit your changes or "
            "specify `algorithm_force_update=True` "
            "to let Anylearn make an auto-commit."
    )

    # Dataset
    dset, dataset_archive, dataset_checksum = _get_or_create_dataset(
        id=dataset_id,
        dir_path=dataset_dir,
        archive_path=dataset_archive
    )
    if dataset_archive:
        # Local dataset registration
        _upload_dataset(dataset=dset,
                        dataset_archive=dataset_archive,
                        uploader=resource_uploader,
                        polling=resource_polling)
        DB().create_local_dataset(id=dset.id, checksum=dataset_checksum)

    mounts = {}
    if dset and dataset_hyperparam_name:
        mounts[dataset_hyperparam_name] = dset
    if model and model_hyperparam_name:
        mounts[model_hyperparam_name] = model
    if pretrain_task and pretrain_hyperparam_name:
        mounts[pretrain_hyperparam_name] = pretrain_task.get_results_file()

    # Project
    if project_id or project_name:
        project = _get_or_create_project(project_id=project_id,
                                         project_name=project_name)
    else:
        try:
            project = _get_or_create_default_project()
        except:
            # Backward compatibility when default projects not supported
            project = _get_or_create_project()

    # Train task
    train_task_name = generate_random_name()
    train_task = _create_train_task(
        name=train_task_name,
        algorithm=algo,
        algorithm_git_ref=algorithm_git_ref or current_sha,
        project=project,
        hyperparams=hyperparams,
        mounts=mounts,
        resource_request=resource_request,
        description=task_description,
    )

    DB().create_or_update_train_task(train_task=train_task)
    train_profile = TrainProfile(id=generate_primary_key("DESC"),
                                 train_task_id=train_task.id,
                                 entrypoint=algo.entrypoint_training,
                                 algorithm_id=algo.id,
                                 dataset_id=dset.id if dset else None,
                                 train_params=train_task.train_params,
                                 algorithm_dir=str(algorithm_dir),
                                 algorithm_archive=algorithm_archive,
                                 dataset_dir=str(dataset_dir),
                                 dataset_archive=dataset_archive,)
    train_profile.create_in_db()
    return train_task, algo, dset, project


def quick_evaluate(model_id: Optional[str]=None,
                   model_dir: Optional[Union[str,Path]]=None,
                   model_archive: Optional[str]=None,
                   algorithm_id: Optional[str]=None,
                   algorithm_name: Optional[str]=None,
                   algorithm_dir: Optional[Union[str, Path]]=None,
                   algorithm_archive: Optional[str]=None,
                   dataset_id: Optional[str]=None,
                   dataset_dir: Optional[Union[str, Path]]=None,
                   dataset_archive: Optional[str]=None,
                   entrypoint: Optional[str]=None,
                   output: Optional[str]=None,
                   resource_uploader: ResourceUploader=None,
                   resource_polling: Union[float, int]=5,
                   model_hyperparam_name: str="model_path",
                   dataset_hyperparam_name: str="dataset",
                   hyperparams: dict={},
                   gpu_num: int=1):
    """
    本地模型快速验证接口。

    仅需提供本地资源和验证相关的信息，
    即可在Anylearn后端引擎启动自定义模型/算法/数据集的验证：
    
    - 模型路径（文件目录或压缩包）
    - 模型关联的算法路径（文件目录或压缩包）
    - 数据集路径（文件目录或压缩包）
    - 验证启动命令
    - 验证结果输出路径（结果需写入文件）
    - 验证超参数

    本接口封装了Anylearn从零启动验证的一系列流程：

    - 模型注册、上传
    - 算法注册、上传
    - 数据集注册、上传
    - 验证任务创建

    本地资源初次在Anylearn注册和上传时，
    会在本地记录资源的校验信息。
    下一次调用快速训练或快速验证接口时，
    如果提供了相同的资源信息，
    则不再重复注册和上传资源，
    自动复用远程资源。

    如有需要，也可向本接口传入已在Anylearn远程注册的模型、算法或数据集的ID，
    省略资源创建的过程。

    Parameters
    ----------
    model_id : :obj:`str`, optional
        已在Anylearn远程注册的模型ID。
    model_dir : :obj:`str`, optional
        本地模型目录路径。
    model_archive : :obj:`str`, optional
        本地模型压缩包路径。
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
    dataset_id : :obj:`str`, optional
        已在Anylearn远程注册的数据集ID。
    dataset_dir : :obj:`str`, optional
        本地数据集目录路径。
    dataset_archive : :obj:`str`, optional
        本地数据集压缩包路径。
    entrypoint : :obj:`str`, optional
        启动验证的入口命令。
    output : :obj:`str`, optional
        输出验证结果的相对路径（相对于模型关联的算法的目录）。
    resource_uploader : :obj:`ResourceUploader`, optional
        资源上传实现。
        默认使用系统内置的同步上传器 :obj:`SyncResourceUploader` 。
    resource_polling : :obj:`float|int`, optional
        资源上传中轮询资源状态的时间间隔（单位：秒）。
        默认为5秒。
    model_hyperparam_name : :obj:`str`, optional
        启动验证时，模型路径作为启动命令参数传入算法的参数名。
        需指定长参数名，如 :obj:`--model` ，并省略 :obj:`--` 部分传入。
        模型路径由Anylearn后端引擎管理。
        默认为 :obj:`model_path` 。
    dataset_hyperparam_name : :obj:`str`, optional
        启动验证时，数据集路径作为启动命令参数传入算法的参数名。
        需指定长参数名，如 :obj:`--data` ，并省略 :obj:`--` 部分传入。
        数据集路径由Anylearn后端引擎管理。
        默认为 :obj:`dataset` 。
    hyperparams : :obj:`dict`, optional
        验证超参数字典。
        超参数将作为验证启动命令的参数传入算法。
        超参数字典中的键应为长参数名，如 :obj:`--param` ，并省略 :obj:`--` 部分传入。
        默认为空字典。
    gpu_num : :obj:`int`, optional
        向Anylearn后端引擎请求的GPU数量。
        默认为1。

    Returns
    -------
    EvaluateTask
        创建的验证任务对象
    Algorithm
        在快速验证过程中创建或获取的算法对象
    Model
        在快速验证过程中创建或获取的模型对象
    Dataset
        在快速验证过程中创建或获取的数据集对象
    """
    # Algorithm
    algo = sync_algorithm(
        id=algorithm_id,
        name=algorithm_name,
        dir_path=algorithm_dir,
        archive_path=algorithm_archive,
        entrypoint_evaluation=entrypoint,
        output_evaluation=output,
        uploader=resource_uploader,
        polling=resource_polling,
    )

    # Model
    model, model_archive, model_checksum = _get_or_create_model(
        id=model_id,
        dir_path=model_dir,
        archive_path=model_archive,
        algorithm=algo
    )
    if model_archive:
        # Local model registration
        _upload_model(model=model,
                      model_archive=model_archive,
                      uploader=resource_uploader,
                      polling=resource_polling)
        DB().create_local_model(id=model.id, checksum=model_checksum)

    # Dataset
    dset, dataset_archive, dataset_checksum = _get_or_create_dataset(
        id=dataset_id,
        dir_path=dataset_dir,
        archive_path=dataset_archive
    )
    if dataset_archive:
        # Local dataset registration
        _upload_dataset(dataset=dset,
                        dataset_archive=dataset_archive,
                        uploader=resource_uploader,
                        polling=resource_polling)
        DB().create_local_dataset(id=dset.id, checksum=dataset_checksum)
    
    # Evaluate task
    eval_name = generate_random_name()
    eval_task = _create_eval_task(
        name=eval_name,
        model=model,
        dataset=dset,
        model_hyperparam_name=model_hyperparam_name,
        dataset_hyperparam_name=dataset_hyperparam_name,
        hyperparams=hyperparams,
        gpu_num=gpu_num
    )

    return eval_task, algo, model, dset


def resume_unfinished_local_train_tasks():
    db = DB()
    local_list = db.get_unfinished_train_tasks()
    task_list = [TrainTask(id=local_train_task.id,
                           secret_key=local_train_task.secret_key,
                           project_id=local_train_task.project_id,
                           state=local_train_task.remote_state_sofar,
                           load_detail=True)
                 for local_train_task in local_list]
    [db.update_train_task(train_task) for train_task in task_list]
    return task_list
