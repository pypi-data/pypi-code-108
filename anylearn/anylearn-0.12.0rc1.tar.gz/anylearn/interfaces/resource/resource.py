from datetime import datetime
import os
from typing import Optional, Union

from anylearn.interfaces.base import BaseObject
from anylearn.interfaces.resource.resource_uploader import ResourceUploader
from anylearn.interfaces.resource.resource_downloader import ResourceDownloader
from anylearn.utils.errors import AnyLearnException
from anylearn.utils.api import (
    url_base,
    get_with_token,
    post_with_token,
)


class Resource(BaseObject):
    """
    Attributes
    ----------
    id
        资源的唯一标识符，自动生成，由类名前四位+uuid1生成的编码中后28个有效位（小写字母和数字）组成（自动生成）
    name
        资源的名称（长度1~50）
    description
        资源描述（长度最大255）
    state
        资源状态
    visibility
        资源可见性（默认3）
    upload_time
        资源上传时间
    filename
        下一步中会被分片上传的资源的完整名（包括扩展名）
    is_zipfile
        是否为zip文件
    file_path
        资源文件路径
    size
        资源文件大小
    creator_id
        创建者ID
    node_id
        节点ID
    owner
        资源的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
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
                 load_detail=False):
        """
        Parameters
        ----------
        id
            资源的唯一标识符，自动生成，由类名前四位+uuid1生成的编码中后28个有效位（小写字母和数字）组成（自动生成）
        name
            资源的名称（长度1~50）
        description
            资源描述（长度最大255）
        state
            资源状态
        visibility
            资源可见性（默认3）
        upload_time
            资源上传时间
        filename
            下一步中会被分片上传的资源的完整名（包括扩展名）
        is_zipfile
            是否为zip文件
        file_path
            资源文件路径
        size
            资源文件大小
        creator_id
            创建者ID
        node_id
            节点ID
        owner
            资源的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
        load_detail
            初始化时是否加载详情
        """
        self.name = name
        self.description = description
        self.state = state
        self.visibility = visibility
        self.upload_time = upload_time
        self.filename = filename
        self.is_zipfile = is_zipfile
        self.file_path = file_path
        self.size = size
        self.creator_id = creator_id
        self.node_id = node_id
        self.owner = owner
        super().__init__(id=id, load_detail=load_detail)

    @classmethod
    def list_dir(cls, resource_id):
        """
        文件列表查询接口

        :param resource_id: :obj:`str`
                    文件ID

        :return: 
            .. code-block:: json

                {
                  "vgg_ssd300_tianyuan.yaml": {
                        "name": "vgg_ssd300_tianyuan.yaml",
                        "type": "file"
                    }
                }

        """
        assert resource_id
        return get_with_token(f"{url_base()}/resource/listdir",
                              params={ 'file_id': resource_id })
    
    @classmethod
    def upload_file(cls,
                    resource_id: str,
                    file_path: str,
                    uploader: Optional[ResourceUploader]=None,
                    chunk_size: int=2048000):
        """
        对指定路径的本地文件进行分割并使用aiohttp异步上传

        Parameters
        ----------
        resource_id : :obj:`str`
            资源ID。
        file_path : :obj:`str`
            文件路径。
        uploader : :obj:`ResourceUploader`
            可以使用SDK中的AsyncResourceUploader，也可以自定义实现ResourceUploader。
        chunk_size : :obj:`int`
            文件分割大小，默认2048000。

        Returns
        -------
        bool
            True or False
        """

        assert resource_id, file_path

        # 读取选定文件的内容并根据chunk_size进行切割
        file_size = os.path.getsize(file_path)
        n_chunks = (file_size // chunk_size) + 1
        with open(file_path, 'rb') as f:
            chunks = [f.read(chunk_size) for i in range(n_chunks)]
        
        # 执行异步上传
        uploader.run(resource_id=resource_id, chunks=chunks)

        # 告知后端上传结束
        res = post_with_token(f"{url_base()}/resource/upload_finish",
                              data={ 'file_id': resource_id })
        return not not res

    @classmethod
    def download_file(cls,
                      resource_id: str,
                      save_path: str,
                      polling: Union[float, int]=5,
                      downloader: Optional[ResourceDownloader]=None,
                      ):
        """
        把服务器资源使用aiohttp异步下载到本地指定的文件夹

        Parameters
        ----------
        resource_id : :obj:`str`
            资源ID。
        save_path : :obj:`str`
            保存路径。
        downloader : :obj:`ResourceDownloader`
            可以使用SDK中的AsyncResourceDownloader，也可以自定义实现ResourceDownloader。
        polling : :obj:`float, int`
            下载前要先压缩文件，轮询查看文件有没有压缩完的时间间隔，单位：秒。默认值5

        Returns
        -------
        str
            文件名。
        """

        assert resource_id, save_path
        if not os.path.exists(save_path):
            raise AnyLearnException(f"保存路径{save_path}不存在")

        # 执行异步下载
        return downloader.run(resource_id=resource_id,  # type: ignore
                              save_path=save_path,
                              polling=polling,
                             )


class ResourceState:
    """
    资源状态标识：

    - 1(CREATED)表示已创建
    - 2(UPLOADING)表示上传中
    - 3(READY)表示就绪
    - -1(DELETED)表示已删除
    - -2(ERROR)表示出错
    """
    CREATED = 1
    UPLOADING = 2
    READY = 3
    DELETED = -1
    ERROR = -2


class ResourceVisibility:
    """
    资源可见性标识：

    - -1(HIDDEN)表示不可见
    - 1(PRIVATE)表示仅创建者可见
    - 2(PROTECTED)表示所有者可见
    - 3(PUBLIC)表示公开
    """
    HIDDEN = -1
    PRIVATE = 1
    PROTECTED = 2
    PUBLIC = 3
