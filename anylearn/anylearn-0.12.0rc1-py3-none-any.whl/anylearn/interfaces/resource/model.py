from datetime import datetime
from typing import Optional, Union

from anylearn.utils.api import url_base, get_with_token
from anylearn.utils.errors import AnyLearnException
from anylearn.interfaces.resource.resource import Resource


class Model(Resource):
    """
    AnyLearn模型类，以方法映射模型CRUD相关接口

    Attributes
    ----------
    id
        模型的唯一标识符，自动生成，由MODE+uuid1生成的编码中后28个有效位（小写字母和数字）组成（自动生成）
    name
        模型的名称（长度1~50）
    description
        模型描述（长度最大255）
    state
        模型状态
    visibility
        模型可见性（默认3）
    upload_time
        模型上传时间
    filename
        下一步中会被分片上传的模型的完整模型名（包括扩展名）
    is_zipfile
        是否为zip文件
    file_path
        模型文件路径
    size
        模型文件大小
    creator_id
        创建者ID
    node_id
        节点ID
    owner
        模型的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
    algorithm_id
        模型使用的算法
    load_detail
        初始化时是否加载详情
    """

    """具体资源信息配置"""
    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': ['name', 'filename', 'algorithm_id'],
            'update': ['id', 'name'],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': ['name', 'description', 'visibility', 'owner',
                       'filename', 'algorithm_id'],
            'update': ['id', 'name', 'description', 'visibility', 'owner',
                       'algorithm_id'],
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
                 visibility=3,
                 upload_time: Optional[Union[datetime, str]]=None,
                 filename: Optional[str]=None,
                 is_zipfile: Optional[int]=None,
                 file_path: Optional[str]=None,
                 size: Optional[str]=None,
                 creator_id: Optional[str]=None,
                 node_id: Optional[str]=None,
                 owner: Optional[list]=None,
                 algorithm_id: Optional[str]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            模型的唯一标识符，自动生成，由MODE+uuid1生成的编码中后28个有效位（小写字母和数字）组成（自动生成）
        name
            模型的名称（长度1~50）
        description
            模型描述（长度最大255）
        state
            模型状态
        visibility
            模型可见性（默认3）
        upload_time
            模型上传时间
        filename
            下一步中会被分片上传的模型的完整模型名（包括扩展名）
        is_zipfile
            是否为zip文件
        file_path
            模型文件路径
        size
            模型文件大小
        creator_id
            创建者ID
        node_id
            节点ID
        owner
            模型的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
        algorithm_id
            模型使用的算法
        load_detail
            初始化时是否加载详情
        """
        self.algorithm_id = algorithm_id
        super().__init__(id=id, name=name, description=description,
                         state=state, visibility=visibility,
                         upload_time=upload_time, filename=filename,
                         is_zipfile=is_zipfile, file_path=file_path, size=size,
                         creator_id=creator_id, node_id=node_id, owner=owner,
                         load_detail=load_detail)

    @classmethod
    def get_list(cls) -> list:
        """
        获取模型列表
        
        Returns
        -------
        List [Model]
            模型对象的集合。
        """
        res = get_with_token(f"{url_base()}/model/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            Model(id=m['id'], name=m['name'], description=m['description'],
                  state=m['state'], visibility=m['visibility'],
                  upload_time=m['upload_time'], creator_id=m['creator_id'],
                  node_id=m['node_id'], owner=m['owner'],
                  algorithm_id=m['algorithm_id'])
            for m in res
        ]

    def get_detail(self):
        """
        获取模型详细信息

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        Model
            模型对象。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/model/query",
                             params={'id': self.id})
        if not res or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        res = res[0]
        self.__init__(id=res['id'], name=res['name'],
                      description=res['description'], state=res['state'],
                      visibility=res['visibility'],
                      upload_time=res['upload_time'], filename=res['filename'],
                      is_zipfile=True if res['is_zipfile'] == 1 else False,
                      file_path=res['file'], size=res['size'],
                      creator_id=res['creator_id'], node_id=res['node_id'],
                      owner=res['owner'], algorithm_id=res['algorithm_id'])

    def _namespace(self):
        return "model"
