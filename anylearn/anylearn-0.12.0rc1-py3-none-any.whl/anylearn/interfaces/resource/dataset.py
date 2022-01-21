from __future__ import annotations
from datetime import datetime
from typing import Optional, Union

from anylearn.utils.api import url_base, get_with_token
from anylearn.utils.errors import AnyLearnException
from anylearn.interfaces.resource.resource import Resource

class Dataset(Resource):
    """
    AnyLearn数据集类，以方法映射数据集CRUD相关接口
        
    Attributes
    ----------
    id
        数据集的唯一标识符，自动生成，由ALGO+uuid1生成的编码中后28个有效位（小写字母和数字）组成（自动生成）
    name
        数据集的名称（长度1~50）
    description
        数据集描述（长度最大255）
    state
        数据集状态
    visibility
        数据集的可见性（默认为3）
    upload_time
        数据集上传时间
    filename
        下一步中会被分片上传的文件的完整文件名（包括扩展名）（长度1~128）
    is_zipfile
        是否为zip文件
    file_path
        数据集文件路径
    size
        数据集文件大小
    creator_id
        创建者ID
    node_id
        数据集节点ID
    owner
        数据集的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
    load_detail
        初始化时是否加载详情
    """

    """具体资源信息配置"""
    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': ['name', 'filename'],
            'update': ['id', 'name'],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': ['name', 'description', 'visibility', 'owner',
                       'filename'],
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
                 visibility=3,
                 upload_time: Optional[Union[datetime, str]]=None,
                 filename: Optional[str]=None,
                 is_zipfile: Optional[bool]=None,
                 file_path: Optional[str]=None,
                 size: Optional[str]=None,
                 creator_id: Optional[str]=None,
                 node_id: Optional[str]=None,
                 owner: Optional[list]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            数据集的唯一标识符，自动生成，由ALGO+uuid1生成的编码中后28个有效位（小写字母和数字）组成（自动生成）
        name
            数据集的名称（长度1~50）
        description
            数据集描述（长度最大255）
        state
            数据集状态
        visibility
            数据集的可见性（默认为3）
        upload_time
            数据集上传时间
        filename
            下一步中会被分片上传的文件的完整文件名（包括扩展名）（长度1~128）
        is_zipfile
            是否为zip文件
        file_path
            数据集文件路径
        size
            数据集文件大小
        creator_id
            创建者ID
        node_id
            数据集节点ID
        owner
            数据集的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
        load_detail
            初始化时是否加载详情
        """
        super().__init__(id=id, name=name, description=description,
                         state=state, visibility=visibility,
                         upload_time=upload_time, filename=filename,
                         is_zipfile=is_zipfile, file_path=file_path, size=size,
                         creator_id=creator_id, node_id=node_id, owner=owner,
                         load_detail=load_detail)

    def __eq__(self, other: Dataset) -> bool:
        if not isinstance(other, Dataset):
            return NotImplemented
        return all([
            self.id == other.id,
            self.name == other.name,
            self.description == other.description,
            self.visibility == other.visibility,
            # self.state == other.state,
            # self.upload_time == other.upload_time,
            # self.filename == other.filename,
            # self.file_path == other.file_path,
            # self.is_zipfile == other.is_zipfile,
            # self.size == other.size,
            # self.creator_id == other.creator_id,
            # self.node_id == other.node_id,
            # self.owner == other.owner,
        ])

    @classmethod
    def get_list(cls) -> list:
        """
        获取数据集列表
        
        Returns
        -------
        List [Dataset]
            数据集对象的集合。
        """
        res = get_with_token(f"{url_base()}/dataset/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            Dataset(id=d['id'], name=d['name'], description=d['description'],
                    state=d['state'], visibility=d['visibility'],
                    upload_time=d['upload_time'])
            for d in res
        ]

    def get_detail(self):
        """
        获取数据集详细信息

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        Dataset
            数据集对象。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/dataset/query",
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
                      owner=res['owner'])

    def _namespace(self):
        return "dataset"
