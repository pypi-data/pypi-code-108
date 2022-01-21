from __future__ import annotations
from datetime import datetime
from typing import Optional

'''
所有与AnyLearn Project相关的接口
'''
from anylearn.utils.api import url_base, get_with_token, post_with_token, put_with_token, delete_with_token
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from anylearn.utils import no_none_filter
from anylearn.interfaces.base import BaseObject
from anylearn.interfaces.train_task import TrainTask


class ProjectVisibility:
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


class Project(BaseObject):
    """
    AnyLearn项目类，以方法映射项目CRUD相关接口

    Attributes
    ----------
    id
        项目的唯一标识符，自动生成，由PROJ+uuid1生成的编码中后28个有效位（小写字母和数字）组成
    name
        项目名称（非空 长度1~50）
    description
        项目描述（可为空 长度最大255）
    visibility
        项目的可见性（默认值1）
    create_time
        创建时间
    update_time
        更新时间
    creator_id
        创建者的ID
    datasets
        项目实用的数据集,以逗号分隔数据集的ID拼成的字符串，无多余空格
    owner
        项目的所有者，以逗号分隔用户的ID拼成的字符串，无多余空格
    load_detail
        初始化时是否加载详情
    """

    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': ['name'],
            'update': ['id', 'name'],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': ['id', 'name', 'description', 'datasets', 'visibility',
                       'owner'],
            'update': ['id', 'name', 'description', 'datasets', 'visibility',
                       'owner'],
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
                 visibility=3,
                 create_time: Optional[datetime]=None,
                 update_time: Optional[datetime]=None,
                 creator_id: Optional[str]=None,
                 datasets: Optional[list]=None,
                 owner: Optional[list]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            项目的唯一标识符，自动生成，由PROJ+uuid1生成的编码中后28个有效位（小写字母和数字）组成
        name
            项目名称（非空 长度1~50）
        description
            项目描述（可为空 长度最大255）
        visibility
            项目的可见性（默认值1）
        create_time
            创建时间
        update_time
            更新时间
        creator_id
            创建者的ID
        datasets
            项目实用的数据集,以逗号分隔数据集的ID拼成的字符串，无多余空格
        owner
            项目的所有者，以逗号分隔用户的ID拼成的字符串，无多余空格
        load_detail
            初始化时是否加载详情
        """
        self.id = id
        self.name = name
        self.description = description
        self.visibility = visibility
        self.create_time = create_time
        self.update_time = update_time
        self.creator_id = creator_id
        self.datasets = datasets
        self.owner = owner
        super().__init__(id=id, load_detail=load_detail)

    def __eq__(self, other: Project) -> bool:
        if not isinstance(other, Project):
            return NotImplemented
        return all([
            self.id == other.id,
            self.name == other.name,
            self.description == other.description,
            # self.visibility == other.visibility,
            # self.create_time == other.create_time,
            # self.update_time == other.update_time,
            # self.creator_id == other.creator_id,
            # self.datasets == other.datasets,
            # self.owner == other.owner,
        ])

    @classmethod
    def get_list(cls):
        """
        获取训练项目列表
        
        Returns
        -------
        List [Project]
            训练项目对象的集合。
        """
        res = get_with_token(f"{url_base()}/project/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            Project(id=item['id'], name=item['name'],
                    description=item['description'],
                    create_time=item['create_time'],
                    update_time=item['update_time'])
            for item in res
        ]

    def get_detail(self):
        """
        获取训练项目详细信息

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        Project
            训练项目对象。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/project/query",
                             params={'id': self.id})
        if not res or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        res = res[0]
        self.__init__(id=res['id'], name=res['name'],
                      description=res['description'],
                      visibility=res['visibility'],
                      create_time=res['create_time'],
                      update_time=res['update_time'],
                      creator_id=res['creator_id'],
                      datasets=res['datasets'],
                      owner=res['owner'])

    @classmethod
    def get_my_default_project(cls) -> Project:
        res = get_with_token(f"{url_base()}/project/default")
        if not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        res = res[0]
        return Project(id=res['id'], name=res['name'],
                       description=res['description'],
                       visibility=res['visibility'],
                       create_time=res['create_time'],
                       update_time=res['update_time'],
                       creator_id=res['creator_id'],
                       datasets=res['datasets'],
                       owner=res['owner'])

    @classmethod
    def create_my_default_project(cls) -> Project:
        res = get_with_token(f"{url_base()}/project/default")
        if not isinstance(res, dict) or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        project_id = res['data']
        return Project(id=project_id, load_detail=True)

    def get_train_tasks(self, load_detail=False):
        """
        获取训练项目的训练任务列表
        
        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        List [TrainTask]
            训练任务的集合。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/train_task/list",
                             params={'project_id': self.id})
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            TrainTask(id=item['id'], name=item['name'],
                      description=item['description'], state=item['state'],
                      secret_key=item['secret_key'],
                      results_id=item['results_id'],
                      create_time=item['create_time'],
                      finish_time=item['finish_time'],
                      load_detail=load_detail)
            for item in res
        ]

    def _namespace(self):
        return "project"
