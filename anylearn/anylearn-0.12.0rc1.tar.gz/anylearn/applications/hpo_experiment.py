from __future__ import annotations
from datetime import datetime
import json
from threading import Thread
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse, ParseResult

from anylearn.config import AnylearnConfig
from anylearn.interfaces import BaseObject, Project, TrainTask
from anylearn.interfaces.resource import (
    Algorithm,
    AsyncResourceDownloader,
    Dataset,
    Model,
    Resource,
    ResourceDownloader,
)
from anylearn.utils import logger, utc_plus_8
from anylearn.utils.api import url_base, get_with_token, post_with_token
from anylearn.utils.errors import AnyLearnException


class HpoExperiment(BaseObject):
    """
    调参实验描述类。

    一个调参实验的描述包括了
    调参任务配置、
    训练配置以及算法、
    数据集、
    训练的元信息
    等几方面，
    用户可以根据这些信息可以在多次调参实验之间进行区别和回忆。
    调参实验描述中封装了一系列与实验相关的功能，
    如：获取全部实验、获取某一实验、停止实验、重启实验、输出最佳模型等等，
    以便对任一调参实验的生命周期进行完整的回溯和管理。

    Attributes
    ----------
    project_id : :obj:`str`
        已在Anylearn远程创建的训练项目ID。
    algorithm_id : :obj:`str`
        已在Anylearn远程注册的算法ID。
    dataset_id : :obj:`str`
        已在Anylearn远程注册的数据集ID。
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
    hpo_concurrency : :obj:`int`, optional
        调优期望并行度，即期望同时运行的任务数，实际并行度视后端资源调度情况而定。
        默认为 :obj:`1` 。
    gpu_num : :obj:`int`, optional
        向Anylearn后端引擎请求的GPU数量。
        默认为1。

        .. deprecated:: 0.11.1

            Use :obj:`resources_request` instead
            to specify QuotaGroup and resource request.

    gpu_mem : :obj:`int`, optional
        向Anylearn后端引擎请求的显存大小。
        默认为0。

        .. deprecated:: 0.11.1

            Use :obj:`resources_request` instead
            to specify QuotaGroup and resource request.

    resource_request : :obj:`List[Dict[str, Dict[str, int]]]`, optional
        单次训练所需计算资源的请求。
        如未填，则使用Anylearn后端的:obj:`default`资源组中的默认资源套餐。
    created_at : :obj:`str`, optional
        调参实验的创建时间。
        默认为东八时区的当前时间。
    hpo_id : :obj:`str`, optional
        调参实验ID。
    hpo_ip : :obj:`str`, optional
        调参实验容器IP地址。
    hpo_port : :obj:`int`, optional
        调优实验的本地端口绑定。
    project: :obj:`Project`, optional
        已在Anylearn远程创建的训练项目对象
    algorithm : :obj:`Algorithm`, optional
        已在Anylearn远程注册的算法对象。
    dataset : :obj:`Dataset`, optional
        已在Anylearn远程注册的数据集对象。
    dataset_hyperparam_name : :obj:`str`, optional
        启动训练时，数据集路径作为启动命令参数传入算法的参数名。
        需指定长参数名，如 :obj:`--data` ，并省略 :obj:`--` 部分传入。
        数据集路径由Anylearn后端引擎管理。
        默认为 :obj:`dataset` 。
    tasks: :obj:`dict`, optional
        调参实验中的训练任务ID与调参任务ID的映射。
    err: :obj:`list`, optional
        调参准备过程中出现的错误日志。
    """

    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': ['project_id', 'algorithm_id', 'dataset_id',
                       'hpo_search_space', 'dataset_hyperparam_name'],
            'update': [],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': ['project_id', 'algorithm_id', 'dataset_id',
                       'hpo_search_space', 'hpo_max_runs', 'hpo_max_duration',
                       'hpo_tuner_name', 'hpo_mode', 'hpo_concurrency',
                       'dataset_hyperparam_name', 'resource_request'],
            'update': [],
        },
    }

    def __init__(self,
                 project_id: str,
                 algorithm_id: Optional[str]=None,
                 dataset_id: Optional[str]=None,
                 hpo_search_space: Optional[dict]=None,
                 hpo_max_runs: Optional[int]=10,
                 hpo_max_duration: Optional[int]="24h",
                 hpo_tuner_name: Optional[str]="TPE",
                 hpo_mode: Optional[str]="maximize",
                 hpo_concurrency: Optional[int]=1,
                 gpu_num: Optional[int]=-1, # deprecated 0.11.1 - remove soon
                 gpu_mem: Optional[int]=-1, # deprecated 0.11.1 - remove soon
                 resource_request: Optional[List[Dict[str, Dict[str, int]]]]=None,
                 created_at: Optional[datetime]=utc_plus_8(),
                 hpo_id: Optional[str]=None,
                 hpo_ip: Optional[str]=None,
                 hpo_port: Optional[int]=None,
                 hpo_status: Optional[str]=None,
                 project: Optional[Project]=None,
                 algorithm: Optional[Algorithm]=None,
                 dataset: Optional[Dataset]=None,
                 dataset_hyperparam_name: Optional[str]='dataset',
                 tasks: Optional[dict]=dict(),
                 err: Optional[list]=None,
                 load_detail: bool=False):
        """
        Parameters
        ----------
        project_id : :obj:`str`
            已在Anylearn远程创建的训练项目ID。
        algorithm_id : :obj:`str`
            已在Anylearn远程注册的算法ID。
        dataset_id : :obj:`str`
            已在Anylearn远程注册的数据集ID。
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
        hpo_concurrency : :obj:`int`, optional
            调优期望并行度，即期望同时运行的任务数，实际并行度视后端资源调度情况而定。
            默认为 :obj:`1` 。
        gpu_num : :obj:`int`, optional
            向Anylearn后端引擎请求的GPU数量。
            默认为1。

            .. deprecated:: 0.11.1

                Use :obj:`resources_request` instead
                to specify QuotaGroup and resource request.

        gpu_mem : :obj:`int`, optional
            向Anylearn后端引擎请求的显存大小。
            默认为0。

            .. deprecated:: 0.11.1

                Use :obj:`resources_request` instead
                to specify QuotaGroup and resource request.

        resource_request : :obj:`List[Dict[str, Dict[str, int]]]`, optional
            单次训练所需计算资源的请求。
            如未填，则使用Anylearn后端的:obj:`default`资源组中的默认资源套餐。
        created_at : :obj:`str`, optional
            调参实验的创建时间。
            默认为东八时区的当前时间。
        hpo_id : :obj:`str`, optional
            调参实验ID。
        hpo_ip : :obj:`str`, optional
            调参实验容器IP地址。
        hpo_port : :obj:`int`, optional
            调优实验的本地端口绑定。
        project: :obj:`Project`, optional
            已在Anylearn远程创建的训练项目对象
        algorithm : :obj:`Algorithm`, optional
            已在Anylearn远程注册的算法对象。
        dataset : :obj:`Dataset`, optional
            已在Anylearn远程注册的数据集对象。
        dataset_hyperparam_name : :obj:`str`, optional
            启动训练时，数据集路径作为启动命令参数传入算法的参数名。
            需指定长参数名，如 :obj:`--data` ，并省略 :obj:`--` 部分传入。
            数据集路径由Anylearn后端引擎管理。
            默认为 :obj:`dataset` 。
        tasks: :obj:`dict`, optional
            调参实验中的训练任务ID与调参任务ID的映射。
        err: :obj:`list`, optional
            调参准备过程中出现的错误日志。
        """
        self.project_id = project_id
        self.algorithm_id = algorithm_id
        self.dataset_id = dataset_id
        self.hpo_search_space = hpo_search_space
        self.hpo_max_runs = hpo_max_runs
        self.hpo_max_duration = hpo_max_duration
        self.hpo_tuner_name = hpo_tuner_name
        self.hpo_mode = hpo_mode
        self.hpo_concurrency = hpo_concurrency
        self.gpu_num = -1 # deprecated 0.11.1 - remove soon
        self.gpu_mem = -1 # deprecated 0.11.1 - remove soon
        self.resource_request = resource_request
        self.created_at = created_at
        self.hpo_id = hpo_id
        self.hpo_ip = hpo_ip
        self.hpo_port = hpo_port
        self.hpo_status = hpo_status
        self.project = project
        self.algorithm = algorithm
        self.dataset = dataset
        self.dataset_hyperparam_name = dataset_hyperparam_name
        self.tasks = tasks
        self.err = err if isinstance(err, list) else []
        if load_detail:
            if not self.project or self.project_id != self.project.id:
                self.project = Project(id=self.project_id,
                                       load_detail=True)
            if not self.algorithm or self.algorithm_id != self.algorithm.id:
                self.algorithm = Algorithm(id=self.algorithm_id,
                                           load_detail=True)
            if not self.dataset or self.dataset_id != self.dataset.id:
                self.dataset = Dataset(id=self.dataset_id,
                                       load_detail=True)

    @classmethod
    def get_list(cls):
        """
        Listing is currently not supported for HpoExperiment
        """
        raise AnyLearnException("Listing is currently not supported for HpoExperiment")

    def from_dict(self, data: dict, load_detail=False):
        data = dict(
            {
                'project_id': self.project_id,
                'algorithm_id': self.algorithm_id,
                'dataset_id': self.dataset_id,
                'hpo_search_space': self.hpo_search_space,
                'hpo_max_runs': self.hpo_max_runs,
                'hpo_max_duration': self.hpo_max_duration,
                'hpo_tuner_name': self.hpo_tuner_name,
                'hpo_mode': self.hpo_mode,
                'hpo_concurrency': self.hpo_concurrency,
                'resource_request': self.resource_request,
                'created_at': self.created_at,
                'hpo_id': self.hpo_id,
                'hpo_ip': self.hpo_ip,
                'hpo_port': self.hpo_port,
                'hpo_status': self.hpo_status,
                'project': self.project,
                'algorithm': self.algorithm,
                'dataset': self.dataset,
                'tasks': self.tasks,
                'err': self.err,
            },
            **data,
        )
        if 'dataset_ids' in data and data['dataset_ids'] and isinstance(data['dataset_ids'], dict):
            data['dataset_id'] = list(data['dataset_ids'].values())[0].replace('$', '')
        self.__init__(
            project_id=data['project_id'],
            algorithm_id=data['algorithm_id'],
            # dataset_id=list(json.loads(data['dataset_ids']).values())[0].replace('$', ''),
            dataset_id=data['dataset_id'],
            hpo_search_space=(
                json.loads(data['hpo_search_space'])
                if isinstance(data['hpo_search_space'], str)
                else data['hpo_search_space']
            ),
            hpo_max_runs=data['hpo_max_runs'],
            hpo_max_duration=data['hpo_max_duration'],
            hpo_tuner_name=data['hpo_tuner_name'],
            hpo_mode=data['hpo_mode'],
            hpo_concurrency=data['hpo_concurrency'],
            resource_request=data['resource_request'],
            created_at=data['created_at'],
            hpo_id=data['hpo_id'],
            hpo_ip=data['hpo_ip'],
            hpo_port=data['hpo_port'],
            hpo_status=data['hpo_status'],
            tasks=(
                json.loads(data['tasks'])
                if isinstance(data['tasks'], str)
                else data['tasks']
            ),
            err=data['err'],
            load_detail=load_detail,
        )

    def get_detail(self):
        """
        以调参实验ID获取该实验的描述。

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        HpoExperimentNniBack
            符合传入ID的调参实验描述对象。
        """

        data = get_with_token(f"{url_base()}/hpo",
                              params={'project_id': self.project_id})
        self.from_dict(data=data, load_detail=True)

    def stop(self):
        """
        停止调参实验。

        - 对象属性 :obj:`project_id` 应为非空
        """
        self._check_fields(required=['project_id'])
        logger.info(f"Trying to stop HPO of project {self.project_id}")
        res = post_with_token(f"{url_base()}/hpo/stop",
                              data={'project_id': self.project_id})
        return res

    def resume(self):
        """
        重启调参实验。

        - 对象属性 :obj:`project_id` 应为非空
        """
        self._check_fields(required=['project_id'])
        logger.info(f"Trying to resume HPO of project {self.project_id}")
        res = post_with_token(f"{url_base()}/hpo/resume",
                              data={'project_id': self.project_id})
        return res

    def view(self):
        """
        启动调参可视化面板。

        - 对象属性 :obj:`project_id` 应为非空
        """
        self._check_fields(required=['project_id'])
        logger.info(f"Trying to start HPO board of project {self.project_id}")
        res = post_with_token(f"{url_base()}/hpo/view",
                              data={'project_id': self.project_id})
        if not res or 'node_port' not in res:
            logger.error(f"Response error: {res}")
            raise AnyLearnException("请求未能得到有效响应")
        old = urlparse(AnylearnConfig.cluster_address)
        new = ParseResult(
            scheme=old.scheme,
            netloc=f"{old.hostname}:{res['node_port']}",
            path=old.path,
            params=old.params,
            query=old.query,
            fragment=old.fragment,
        )
        return {'url': new.geturl()}

    def get_tasks(self):
        self._check_fields(required=['project_id'])
        logger.info(f"Trying to fetch HPO tasks project {self.project_id}")
        res = get_with_token(f"{url_base()}/hpo/tasks",
                             params={'project_id': self.project_id})
        if not isinstance(res, dict):
            logger.error(f"Response error: {res}")
            raise AnyLearnException("请求未能得到有效响应")
        self.tasks = res
        return self.tasks

    def get_log(self):
        """
        获取调参实验日志（nnimanager.log）。

        - 对象属性 :obj:`project_id` 应为非空
        """
        self._check_fields(required=['project_id'])
        logger.info(f"Trying to retrieve HPO log of project {self.project_id}")
        res = get_with_token(f"{url_base()}/hpo/log",
                             params={'project_id': self.project_id})
        if not res or 'data' not in res:
            logger.error(f"Response error: {res}")
            raise AnyLearnException("请求未能得到有效响应")
        return res['data']

    def get_trial_logs(self):
        """
        获取调参实验日志（nnimanager.log）。

        - 对象属性 :obj:`project_id` 应为非空
        """
        self._check_fields(required=['project_id'])
        logger.info(f"Trying to retrieve HPO log of project {self.project_id}")
        logger.warning("Note that this method may be time-consuming")
        self.get_detail()
        self.get_tasks()
        if not self.tasks:
            return {}
        logs = {}
        for k in self.tasks.keys():
            res = get_with_token(f"{url_base()}/hpo/log/trial",
                                 params={'train_task_id': k})
            if not res or 'data' not in res:
                logger.warning(f"请求未能得到有效响应: {res}")
                continue
            logs[k] = res['data']
        return logs

    def get_trial_train_tasks(self) -> list[TrainTask]:
        self._check_fields(required=['project_id'])
        logger.info(f"Trying to retrieve HPO log of project {self.project_id}")
        self.get_detail()
        self.get_tasks()
        return [TrainTask(id=k, load_detail=True) for k in self.tasks.keys()] if self.tasks else []

    def get_best_train_task(self) -> TrainTask:
        """
        获取调参实验中取得最佳指标的训练任务。

        - 对象属性 :obj:`project_id` 应为非空
        """
        res = get_with_token(f"{url_base()}/hpo/best",
                             params={'project_id': self.project_id})
        if not res or not 'id' in res:
            logger.error(f"Response error: {res}")
            raise AnyLearnException("请求未能得到有效响应")
        task = TrainTask(id=res['id'], load_detail=True)
        task.get_final_metric()
        return task

    def export_best_model(self,
                          local_save_path: str,
                          downloader: Optional[ResourceDownloader]=None):
        """
        导出调参实验中取得最佳指标的模型至本地（下载）。

        - 对象属性 :obj:`project_id` 应为非空

        Parameters
        ----------
        local_save_path : :obj:`str`
            模型下载的本地保存路径。
        downloader : :obj:`ResourceDownloader`, optional
            模型下载器实现对象（建议留空）。
            缺省时将实例化一个内置的异步下载器。
        """
        best_train_task = self.get_best_train_task()
        if not downloader:
            downloader = AsyncResourceDownloader()
        t = Thread(target=Resource.download_file,
                   kwargs={
                       'resource_id': best_train_task.results_id,
                       'save_path': local_save_path,
                       'downloader': downloader, })
        logger.info("Downloading HPO best model...")
        t.start()
        t.join()
        logger.info("Successfully downloaded model.")

    def transform_best_model(
        self,
        model_name: str,
        model_description: Optional[str]=None,
        model_transform_polling: Union[float, int]=5
    ) -> Model:
        """
        转存调参实验中取得最佳指标的模型至Anylearn后端引擎。

        .. Note:: 训练的输出文件夹将被完整转存。

        Parameters
        ----------
        model_name : :obj:`str`
            模型名称。
        model_description : :obj:`str`, optional
            模型描述。
            默认为空。
        model_transform_polling : :obj:`float|int`, optional
            模型转存过程中，轮询模型转存状态的时间间隔。
            默认为5秒。

        Returns
        -------
        Model
            最佳模型转存后的对象。
        """
        best_train_task = self.get_best_train_task()
        model = best_train_task.transform_model(
            file_path=".",
            name=model_name,
            description=model_description,
            polling=model_transform_polling,
        )

        logger.info(
            "Transforming HPO best training "
            "result into Anylearn model..."
        )
        return model

    @classmethod
    def load(cls, data: dict, load_detail=False):
        """
        从接口返回值映射对一个调参实验描述进行实例化。

        Parameters
        ----------
        data : :obj:`dict`
            以字典承载的调参实验元信息。

        Returns
        -------
        HpoExperiment
            调参实验描述对象。
        """
        hpo = HpoExperiment()
        hpo.from_dict(data=data, load_detail=load_detail)
        return hpo

    def save(self):
        # Only create
        self._check_fields(required=self._fields['required']['create'])
        return self._create()

    def _update(self):
        raise AnyLearnException("Update is currently not supported for HpoExperiment")

    def _create(self):
        """
        创建对象，如果子类创建方法与此有较大差异可以重写此方法
        """
        data = self._payload_create()
        data['hpo_search_space'] = json.dumps(data['hpo_search_space'])
        data['dataset_ids'] = json.dumps({
            data['dataset_hyperparam_name']: f"${data['dataset_id']}"
        })
        data['resource_request'] = json.dumps(data['resource_request'])
        res = post_with_token(self._url_create(), data=data)
        if not res or 'project_id' not in res:
            logger.error(f"Response error: {res}")
            raise AnyLearnException("请求未能得到有效响应")
        return True

    def delete(self):
        raise AnyLearnException("Deletion is currently not supported for HpoExperiment")

    def _namespace(self):
        return "hpo"

    def _url_create(self):
        """
        创建对象url，如果子类创建对象接口名称不是 :obj:`add` ，可以重写此方法来定制接口名称
        """
        return f"{url_base()}/{self._namespace()}/start"

    def __repr__(self) -> str:
        kv = (
            f"    project_id = '{self.project_id}',\n"
            f"    algorithm_id = '{self.algorithm_id}',\n"
            f"    dataset_id = '{self.dataset_id}',\n"
            f"    hpo_search_space = '{self.hpo_search_space}',\n"
            f"    hpo_max_runs = '{self.hpo_max_runs}',\n"
            f"    hpo_max_duration = '{self.hpo_max_duration}',\n"
            f"    hpo_tuner_name = '{self.hpo_tuner_name}',\n"
            f"    hpo_mode = '{self.hpo_mode}',\n"
            f"    hpo_concurrency = '{self.hpo_concurrency}',\n"
            f"    gpu_num = '{self.gpu_num}',\n"
            f"    gpu_mem = '{self.gpu_mem}',\n"
            f"    created_at = '{self.created_at}',\n"
            f"    hpo_id = '{self.hpo_id}',\n"
            f"    hpo_ip = '{self.hpo_ip}',\n"
            f"    hpo_port = '{self.hpo_port}',\n"
            f"    hpo_status = '{self.hpo_status}',\n"
            f"    tasks = '{self.tasks}',\n"
            f"    err = '{self.err}',\n"
        )
        return f"HpoExperiment(\n{kv})"
