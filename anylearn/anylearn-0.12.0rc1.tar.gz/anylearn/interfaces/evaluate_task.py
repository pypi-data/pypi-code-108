from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from typing import Optional

from anylearn.utils.api import url_base, get_with_token, post_with_token
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from anylearn.interfaces.base import BaseObject


class EvaluateTaskState:
    """
    训练任务状态标识：

    - 0(CREATED)表示已创建
    - 1(RUNNING)表示运行中
    - 2(SUCCESS)表示已完成
    - -1(DELETED)表示已删除
    - -2(FAIL)表示失败
    - -3(ABORT)表示中断
    """
    CREATED = 0
    RUNNING = 1
    SUCCESS = 2
    DELETED = -1
    FAIL = -2
    ABORT = -3


class EvaluateTaskVisibility:
    """
    项目可见性标识：

    - -1(HIDDEN)表示不可见
    - 1(PRIVATE)表示仅创建者可见
    - 2(PROTECTED)表示所有者可见
    - 3(PUBLIC)表示公开
    """
    HIDDEN = -1
    PRIVATE = 1
    PROTECTED = 2
    PUBLIC = 3


@dataclass
class EvaluateSubTask:
    """
    AnyLearn验证子任务类，以方法映射数据集CRUD相关接口

    Attributes
    ----------
    id
        子任务ID，格式为EVRE+uuid1生成的编码中后28个有效位（小写字母和数字）组成
    model_id
        模型ID
    files
        数据集ID
    evaluate_params
        验证参数，包括 :obj:`dataset` 、 :obj:`eval_metric` 、 :obj:`model_path`
    envs
        环境变量
    gpu_num
        申请的GPU数目
    results
        验证结果
    """

    id: Optional[str]=None
    model_id: Optional[str]=None
    files: list = field(default_factory=list)
    evaluate_params: dict = field(default_factory=dict)
    envs: dict = field(default_factory=dict)
    gpu_num: int = 1
    results: Optional[str]=None


class EvaluateTask(BaseObject):
    """
    AnyLearn验证项目类，以方法映射数据集CRUD相关接口

    Attributes
    ----------
    id
        验证任务的唯一标识符，自动生成，由EVAL+uuid1生成的编码中后28个有效位（小写字母和数字）组成
    name
        验证任务的名称
    description
        验证任务描述
    state
        验证任务状态
    visibility
        验证任务的可见性
    creator_id
        验证任务的创建者
    owner
        验证任务的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
    create_time
        验证任务创建时间
    finish_time
        验证任务完成时间
    params_list
        验证任务参数列表
    sub_tasks
        子验证任务
    secret_key
        秘钥
    load_detail
        初始化时是否加载详情
    """

    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': ['name', 'sub_tasks'],
            'update': ['id', 'name'],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': ['id', 'name', 'description', 'visibility', 'owner',
                       'params_list'],
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
                 state: Optional[int]=None,
                 visibility: Optional[int]=None,
                 creator_id: Optional[str]=None,
                 owner: Optional[list]=None,
                 create_time: Optional[datetime]=None,
                 finish_time: Optional[datetime]=None,
                 params_list: Optional[str]=None,
                 sub_tasks: Optional[list]=None,
                 secret_key: Optional[str]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            验证任务的唯一标识符，自动生成，由EVAL+uuid1生成的编码中后28个有效位（小写字母和数字）组成
        name
            验证任务的名称
        description
            验证任务描述
        state
            验证任务状态
        visibility
            验证任务的可见性
        creator_id
            验证任务的创建者
        owner
            验证任务的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
        create_time
            验证任务创建时间
        finish_time
            验证任务完成时间
        params_list
            验证任务参数列表
        sub_tasks
            子验证任务
        secret_key
            秘钥
        load_detail
            初始化时是否加载详情
        """
        self.id = id
        self.name = name
        self.description = description
        self.state = state
        self.visibility = visibility
        self.creator_id = creator_id
        self.owner = owner
        self.create_time = create_time
        self.finish_time = finish_time
        self.params_list = params_list
        self.sub_tasks = sub_tasks
        self.secret_key = secret_key
        super().__init__(id, load_detail=load_detail)

    @classmethod
    def get_list(cls):
        """
        获取验证任务列表
        
        Returns
        -------
        List [EvaluateTask]
            验证任务对象的集合。
        """
        res = get_with_token(f"{url_base()}/evaluate_task/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            EvaluateTask(id=e['id'], name=e['name'],
                         description=e['description'], state=e['state'],
                         visibility=e['visibility'],
                         creator_id=e['creator_id'], owner=e['owner'],
                         create_time=e['create_time'],
                         finish_time=e['finish_time'],
                         secret_key=e['secret_key'])
            for e in res
        ]

    def get_detail(self):
        """
        获取验证任务详细信息

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        EvaluateTask
            验证任务对象。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/evaluate_task/query",
                             params={'id': self.id})
        if not res or not isinstance(res, dict):
            raise AnyLearnException("请求未能得到有效响应")
        self.__init__(id=res['id'], name=res['name'],
                      description=res['description'], state=res['state'],
                      visibility=res['visibility'],
                      creator_id=res['creator_id'], owner=res['owner'],
                      create_time=res['create_time'],
                      finish_time=res['finish_time'],
                      params_list=res['params_list'],
                      secret_key=res['secret_key'])
        if 'results' not in res or not res['results']:
            self.__load_sub_tasks_from_params_list()
        else:
            self.__load_sub_tasks_from_results(res['results'])

    def _create(self):
        self.__dump_sub_tasks_to_params_list()
        return super()._create()

    def get_log(self, limit=100, direction="init", offset=0, includes=False):
        """
        验证任务日志查询接口

        - 对象属性 :obj:`id` 应为非空
        
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

                {
                  "EVRE123": [
                    {
                      "offset": 2955,
                      "text": "Task EVRE123 finished."
                    }
                  ]
                }
        """
        self._check_fields(required=['id'])
        params = {
            'id': self.id,
            'limit': limit,
            'direction': direction,
            'index': offset,
            'self': 1 if includes else 0,
        }
        res = get_with_token(f"{url_base()}/evaluate_task/log", params=params)
        if not res or type(res) != dict:
            raise AnyLearnException("请求未能得到有效响应")
        return res

    def _namespace(self):
        return "evaluate_task"
    
    def __dump_sub_tasks_to_params_list(self):
        sub_tasks = [asdict(t) for t in self.sub_tasks]
        for t in sub_tasks:
            if not t['model_id']:
                raise AnyLearnMissingParamException("EvaluateSubTask缺少必要字段：model_id")
            t['files'] = ",".join(t['files'])
            t['envs'] = ",".join([f"{k}={v}" for k, v in t['envs'].items()])
        self.params_list = json.dumps(sub_tasks)
        return self.params_list

    def __load_sub_tasks_from_params_list(self):
        if not self.params_list:
            self.sub_tasks = []
            return []
        sub_tasks = json.loads(self.params_list)
        self.sub_tasks = [
            EvaluateSubTask(id=t['id'] if 'id' in t else None,
                            model_id=t['model_id'],
                            files=t['files'].split(",") if t['files'] else [],
                            evaluate_params=t['evaluate_params'],
                            envs={kv[0]: kv[1]
                                    for kv in [
                                        env.split("=")
                                        for env in t['envs'].split(",")
                                    ]} if 'envs' in t and t['envs'] else {},
                            gpu_num=t['gpu_num'] if 'gpu_num' in t else 1,
                            results=t['results'] if 'results' in t else None)
            for t in sub_tasks
        ]
        return self.sub_tasks

    def __load_sub_tasks_from_results(self, results: list):
        self.sub_tasks = [
            EvaluateSubTask(id=t['id'],
                            model_id=t['model_id'],
                            files=t['files'].split(","),
                            evaluate_params=json.loads(t['args']),
                            envs={kv[0]: kv[1]
                                    for kv in [
                                        env.split("=")
                                        for env in t['envs'].split(",")
                                    ]} if t['envs'] else {},
                            gpu_num=t['gpu_num'], results=t['results'])
            for t in results
        ]
        return self.sub_tasks
