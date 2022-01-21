from datetime import datetime
import json
from os import path
import requests
from typing import Optional

from anylearn.config import AnylearnConfig
from anylearn.utils.api import url_base, get_with_token
from anylearn.utils.errors import AnyLearnException
from anylearn.interfaces.base import BaseObject
from .record import ServiceRecord, ServiceRecordState


class ServiceVisibility:
    """
    服务可见性标识：

    - 1(PRIVATE)表示仅创建者可见
    - 2(PROTECTED)表示所有者可见
    - 3(PUBLIC)表示公开
    """
    PRIVATE = 1
    PROTECTED = 2
    PUBLIC = 3


class ServiceState:
    """
    服务状态标识：

    - 0(CREATED)表示已创建
    - 1(RUNNING)表示已部署运行中
    - -1(DELETED)表示已删除
    - -2(STOPPED)表示已停止
    """
    CREATED = 0
    RUNNING = 1
    DELETED = -1
    STOPPED = -2


class Service(BaseObject):
    """
    Attributes
    ----------
    id
        模型服务的唯一标识符，自动生成，由SERV+uuid1生成的编码中后28个有效位（小写字母和数字）组成（非空）
    name
        模型服务的名称
    description
        模型服务描述（默认None，最大长度255）
    visibility
        模型服务的可见性（默认值3）
    model_id
        模型服务使用的模型ID
    address
        模型服务运行地址
    secret_key
        模型服务秘钥
    creator_id
        创建者ID
    envs
        环境变量
    replicas
        模型服务副本数量
    gpu_num
        模型服务申请的GPU数目
    gpu_mem
        模型服务申请的GPU显存
    state
        状态
    create_time
        创建时间
    owner
        模型服务的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
    load_detail
        初始化时是否加载详情
    """
    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': ['name', 'model_id'],
            'update': ['id', 'name'],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': ['name', 'description', 'visibility', 'model_id', 'envs',
                       'replicas', 'gpu_num', 'gpu_mem', 'owner'],
            'update': ['id', 'name', 'description', 'visibility', 'owner'],
        },
    }
    """
    创建/更新对象时：

    - 必须包含且不能为空的字段 :obj:`_fields['required']`
    - 所有字段 :obj:`_fields['payload']`
    """

    def __init__(self,
                 id: Optional[str]=None,
                 name: Optional[str]=None,
                 description: Optional[str]=None,
                 visibility=ServiceVisibility.PUBLIC,
                 model_id: Optional[str]=None,
                 address: Optional[str]=None,
                 secret_key: Optional[str]=None,
                 creator_id: Optional[str]=None,
                 envs: Optional[str]=None,
                 replicas=1,
                 gpu_num=0,
                 gpu_mem=0,
                 state: Optional[int]=None,
                 create_time: Optional[datetime]=None,
                 owner: Optional[list]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            模型服务的唯一标识符，自动生成，由SERV+uuid1生成的编码中后28个有效位（小写字母和数字）组成（非空）
        name
            模型服务的名称
        description
            模型服务描述（默认None，最大长度255）
        visibility
            模型服务的可见性（默认值3）
        model_id
            模型服务使用的模型ID
        address
            模型服务运行地址
        secret_key
            模型服务秘钥
        creator_id
            创建者ID
        envs
            环境变量
        replicas
            模型服务副本数量
        gpu_num
            模型服务申请的GPU数目
        gpu_mem
            模型服务申请的GPU显存
        state
            状态
        create_time
            创建时间
        owner
            模型服务的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
        load_detail
            初始化时是否加载详情
        """
        self.name = name
        self.description = description
        self.state = state
        self.visibility = visibility
        self.creator_id = creator_id
        self.owner = owner
        self.model_id = model_id
        self.address = address
        self.secret_key = secret_key
        self.envs = envs
        self.replicas = replicas
        self.gpu_num = gpu_num
        self.gpu_mem = gpu_mem
        self.create_time = create_time
        super().__init__(id=id, load_detail=load_detail)

    @classmethod
    def get_list(cls) -> list:
        """
        获取服务列表
        
        Returns
        -------
        List [Service]
            服务对象的集合。
        """
        res = get_with_token(f"{url_base()}/service/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            Service(id=s['id'], name=s['name'], description=s['description'],
                    state=s['state'], visibility=s['visibility'],
                    owner=s['owner'], model_id=s['model_id'],
                    creator_id=s['creator_id'], address=s['address'],
                    secret_key=s['secret_key'], create_time=s['create_time'],
                    gpu_num=s['gpu_num'], gpu_mem=s['gpu_mem'])
            for s in res
        ]

    def get_detail(self):
        """
        获取服务详细信息

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        Service
            服务对象。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/service/query",
                             params={'id': self.id})
        if not res or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        res = res[0]
        self.__init__(id=res['id'], name=res['name'],
                      description=res['description'],
                      visibility=res['visibility'], model_id=res['model_id'],
                      address=res['address'], secret_key=res['secret_key'],
                      creator_id=res['creator_id'], envs=res['envs'],
                      replicas=res['replicas'], gpu_num=res['gpu_num'],
                      gpu_mem=res['gpu_mem'], state=res['state'],
                      create_time=res['create_time'], owner=res['owner'])

    def scale(self, replicas: int):
        """
        模型服务伸缩接口

        - 对象属性 :obj:`id` 应为非空

        Parameters
        ----------
        replicas : :obj:`int`
            模型服务副本数量(replicas>=1)。

        Returns
        -------
        bool
            True or False
        """
        if replicas < 1:
            raise AnyLearnException("服务副本数量不应小于1")
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/service/scale",
                             params={
                                 'id': self.id,
                                 'replicas': replicas,
                             })
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        self.replicas = replicas
        return res.get('data', None) == self.id

    def stop(self):
        """
        模型服务停止接口

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        bool
            True or False
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/service/stop",
                             params={
                                 'id': self.id,
                             })
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        self.state = ServiceState.STOPPED
        return res.get('data', None) == self.id

    def restart(self):
        """
        模型服务重启接口

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        bool
            True or False
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/service/restart",
                             params={
                                 'id': self.id,
                             })
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        self.state = ServiceState.RUNNING
        return res.get('data', None) == self.id

    def get_deployment_status(self):
        """
        模型服务状态查询接口

        - 对象属性 :obj:`id` 应为非空

        :return: 
            .. code-block:: json

                {
                  "pod_names": [
                      "deployment-serv001",
                      "deployment-serv002",
                      "deployment-serv003"
                    ],
                  "workers": {
                    "available_workers": 1,
                    "replicas": 1,
                    "unavailable_workers": 0
                    }
                }
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/service/status",
                             params={
                                 'id': self.id,
                             })
        if not res or 'pods' not in res or 'workers' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        res = {
            'pod_names': [p['name'] for p in res['pods']],
            'workers': res['workers'],
        }
        return res

    def get_log(self, pod_name, limit=100, direction="init", offset=0, includes=False):
        """
        模型服务日志查询接口

        - 对象属性 :obj:`id` 应为非空

        :param pod_name: :obj:`str`
                    容器单位名称。
        :param limit: :obj:`int`
                    日志条数上限（默认值100）。
        :param direction: :obj:`str`
                    日志查询方向。
        :param offset: :obj:`int`
                    日志查询索引。
        :param includes: :obj:`bool`
                    是否包含指定索引记录本身。

        :return: 
            .. code-block:: json

                [
                  {
                    "offset": 6554,
                    "text": "[Xlearn-Serving SERV123 ] - 2020-11-26 01:55:23,660 - DEBUG - (worker:1) is waiting"
                  }
                ]
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/service/log",
                             params={
                                 'id': self.id,
                                 'pod_name': pod_name,
                                 'limit': limit,
                                 'direction': direction,
                                 'index': offset,
                                 'self': 1 if includes else 0,
                             })
        if not res:
            raise AnyLearnException("请求未能得到有效响应")
        return res

    def get_records(self, page=1, size=20, load_detail=False):
        """
        模型服务运行结果查询接口

        - 对象属性 :obj:`id` 应为非空

        Parameters
        ----------
        page: :obj:`sintr`
            页面索引（默认值1）。
        size: :obj:`int`
            每页结果数量（默认值20）。
        load_detail: :obj:`bool`
            是否加载记录详情（默认为False）。

        Returns
        -------
        List [ServiceRecord]
            服务运行记录结果的集合。
        """
        self._check_fields(required=['id'])
        ress = get_with_token(f"{url_base()}/service/record",
                              params={
                                  'id': self.id,
                                  'page_index': page,
                                  'page_size': size,
                              })
        if not ress or not isinstance(ress, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            ServiceRecord(id=res['id'], service_id=res['service_id'],
                          inference_data_file_id=res['file_id'],
                          error=res['error'], state=res['state'],
                          create_time=res['create_time'],
                          finish_time=res['finish_time'],
                          load_detail=load_detail)
            for res in ress
        ]

    def predict_online(self, file_binary: str):
        """
        在线预测接口

        Parameters
        ----------
        file_binary: :obj:`str`
            预测的文件。

        Returns
        -------
        ServiceRecord.result
            结果示例: :obj:`[[0.06298828125, 0.11171875149011612, 0.44580078125, 0.35546875, 5, 0.9521484375]]`
        ServiceRecord
            服务记录。
        """
        # Ensure service's address
        if not self.address:
            self.get_detail()
        
        # Call service's predict_online API
        url = lambda :AnylearnConfig.cluster_address + \
                self.address + \
                "/predict_online"
        res = requests.post(url(), files={'file': file_binary})
        res.raise_for_status()
        res.encoding = "utf-8"
        res = res.json()

        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        
        # Fetch prediction results
        record = ServiceRecord(id=res['data'])
        while record.state not in [ServiceRecordState.FINISHED,
                                   ServiceRecordState.FAILED]:
            record.get_detail()
        filename = record.inference_data_file_id
        if not record.result:
            return "", record
        results = json.loads(json.loads(record.result)[filename])['object']
        return results, record

    def _namespace(self):
        return "service"
