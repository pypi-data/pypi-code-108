from __future__ import annotations
from datetime import datetime
import json
from typing import Optional, Union

from anylearn.utils.api import url_base, get_with_token, post_with_token
from anylearn.utils.errors import AnyLearnException
from anylearn.interfaces.resource.resource import Resource, ResourceState

class Algorithm(Resource):
    """
    AnyLearn算法类，以方法映射算法CRUD相关接口

    Attributes
    ----------
    id
        算法的唯一标识符，自动生成，由ALGO+uuid1生成的编码中后28个有效位（小写字母和数字）组成）（自动生成）
    name
        算法的名称
    description
        算法的描述
    state
        算法状态
    visibility 
        算法的可见性，（默认为3）
    upload_time
        算法上传时间
    filename
        下一步中会被分片上传的文件的完整文件名（包括扩展名）（非空 长度1~128）
    is_zipfile
        是否为zip文件
    file_path
        算法文件路径
    size
        算法文件大小
    creator_id
        算法的创建者
    node_id
        算法节点ID
    owner
        算法的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
    tags
        算法的标签
    mirror_id
        算法使用的基础镜像的id
    train_params
        算法的训练参数，包括数据集参数
    evaluate_params
        算法的验证参数，包括数据集参数。
    follows_anylearn_norm
        算法是否符合Anylearn的算法规范（默认为True）
    entrypoint_training
        算法训练的启动命令，非标准算法必填
    output_training
        算法训练结果（模型）存储目录路径，非标准算法必填
    entrypoint_evaluation
        算法验证的启动命令，非标准算法必填
    output_evaluation
        算法验证结果（指标）存储文件路径，非标准算法必填
    git_address
        算法的Anylearn Gitea远端代码仓库地址
    git_migrated
        算法是否由传统模式自动迁移至Anylearn Gitea
    load_detail
        初始化时是否加载详情
    """

    """具体资源信息配置"""
    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': ['name', 'filename', 'mirror_id', 'train_params',
                       'evaluate_params'],
            'update': ['id', 'name'],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': ['name', 'description', 'visibility', 'owner',
                       'filename', 'tags', 'mirror_id', 'train_params',
                       'evaluate_params', 'follows_anylearn_norm',
                       'entrypoint_training', 'output_training',
                       'entrypoint_evaluation', 'output_evaluation'],
            'update': ['id', 'name', 'description', 'visibility', 
                       'owner', 'tags', 'mirror_id', 'train_params',
                       'evaluate_params', 'follows_anylearn_norm',
                       'entrypoint_training', 'output_training',
                       'entrypoint_evaluation', 'output_evaluation'],
        },
    }
    """
    创建/更新对象时：

    - 必须包含且不能为空的字段 :obj:`_fields['required']`
    - 所有字段 :obj:`_fields['payload']`
    """

    __train_params = __evaluate_params = None
    required_train_params = required_evaluate_params = []
    default_train_params = default_evaluate_params = {}

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
                 tags: Optional[str]=None,
                 mirror_id: Optional[str]=None,
                 train_params: Optional[str]=None,
                 evaluate_params: Optional[str]=None,
                 follows_anylearn_norm=True,
                 entrypoint_training: Optional[str]=None,
                 output_training: Optional[str]=None,
                 entrypoint_evaluation: Optional[str]=None,
                 output_evaluation: Optional[str]=None,
                 git_address: Optional[str]=None,
                 git_migrated: Optional[bool]=False,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            算法的唯一标识符，自动生成，由ALGO+uuid1生成的编码中后28个有效位（小写字母和数字）组成）（自动生成）
        name
            算法的名称
        description
            算法的描述
        state
            算法状态
        visibility 
            算法的可见性，（默认为3）
        upload_time
            算法上传时间
        filename
            下一步中会被分片上传的文件的完整文件名（包括扩展名）（非空 长度1~128）
        is_zipfile
            是否为zip文件
        file_path
            算法文件路径
        size
            算法文件大小
        creator_id
            算法的创建者
        node_id
            算法节点ID
        owner
            算法的所有者，以逗号分隔的这些用户的ID拼成的字符串，无多余空格
        tags
            算法的标签
        mirror_id
            算法使用的基础镜像的id
        train_params
            算法的训练参数，包括数据集参数
        evaluate_params
            算法的验证参数，包括数据集参数
        follows_anylearn_norm
            算法是否符合Anylearn的算法规范（默认为True）
        entrypoint_training
            算法训练的启动命令，非标准算法必填
        output_training
            算法训练结果（模型）存储目录路径，非标准算法必填
        entrypoint_evaluation
            算法验证的启动命令，非标准算法必填
        output_evaluation
            算法验证结果（指标）存储文件路径，非标准算法必填
        git_address
            算法的Anylearn Gitea远端代码仓库地址
        git_migrated
            算法是否由传统模式自动迁移至Anylearn Gitea
        load_detail
            初始化时是否加载详情
        """
        self.tags = tags
        self.mirror_id = mirror_id
        self.train_params = train_params
        self.evaluate_params = evaluate_params
        self.follows_anylearn_norm = follows_anylearn_norm
        self.entrypoint_training = entrypoint_training
        self.output_training = output_training
        self.entrypoint_evaluation = entrypoint_evaluation
        self.output_evaluation = output_evaluation
        self.git_address = git_address
        self.git_migrated = git_migrated
        super().__init__(id=id, name=name, description=description,
                         state=state, visibility=visibility,
                         upload_time=upload_time, filename=filename,
                         is_zipfile=is_zipfile, file_path=file_path, size=size,
                         creator_id=creator_id, node_id=node_id, owner=owner,
                         load_detail=load_detail)

    def __eq__(self, other: Algorithm) -> bool:
        if not isinstance(other, Algorithm):
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
            # self.tags == other.tags,
            # self.mirror_id == other.mirror_id,
            # self.train_params == other.train_params,
            # self.evaluate_params == other.evaluate_params,
            self.follows_anylearn_norm == other.follows_anylearn_norm,
            self.entrypoint_training == other.entrypoint_training,
            self.output_training == other.output_training,
            self.entrypoint_evaluation == other.entrypoint_evaluation,
            self.output_evaluation == other.output_evaluation,
            self.git_address == other.git_address,
        ])

    @classmethod
    def get_list(cls) -> list:
        """
        获取算法列表
        
        Returns
        -------
        List [Algorithm]
            算法对象的集合。
        """
        res = get_with_token(f"{url_base()}/algorithm/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            Algorithm(id=a['id'], name=a['name'], description=a['description'],
                      state=a['state'], visibility=a['visibility'],
                      upload_time=a['upload_time'], tags=a['tags'],
                      follows_anylearn_norm=a['follows_anylearn_norm'],
                      git_address=a['git_address'],
                      git_migrated=a['git_migrated'])
            for a in res
        ]

    def get_detail(self):
        """
        获取算法详细信息

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        Algorithm
            算法对象。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/algorithm/query",
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
                      owner=res['owner'], tags=res['tags'],
                      mirror_id=res['mirror_id'],
                      train_params=res['train_params'],
                      evaluate_params=res['evaluate_params'],
                      follows_anylearn_norm=res['follows_anylearn_norm'],
                      entrypoint_training=res['entrypoint_training'],
                      output_training=res['output_training'],
                      entrypoint_evaluation=res['entrypoint_evaluation'],
                      output_evaluation=res['output_evaluation'],
                      git_address=res['git_address'],
                      git_migrated=res['git_migrated'])

    def _namespace(self):
        return "algorithm"

    # def _create(self):
    #     if not self.follows_anylearn_norm:
    #         self._check_fields(required=['entrypoint_training',
    #                                      'output_training'])
    #     return super()._create()

    def _payload_create(self):
        payload = super()._payload_create()
        payload['follows_anylearn_norm'] = int(payload['follows_anylearn_norm'])
        return self.__payload_algo_params_to_str(payload)

    def _payload_update(self):
        payload = super()._payload_update()
        payload['follows_anylearn_norm'] = int(payload['follows_anylearn_norm'])
        return self.__payload_algo_params_to_str(payload)

    def __payload_algo_params_to_str(self, payload):
        if 'train_params' in payload:
            payload['train_params'] = json.dumps(payload['train_params'])
        if 'evaluate_params' in payload:
            payload['evaluate_params'] = json.dumps(payload['evaluate_params'])
        return payload

    @property
    def train_params(self):
        """
        获取训练参数
        """
        return self.__train_params

    @train_params.setter
    def train_params(self, train_params):
        """
        设置训练参数
        """
        if not train_params:
            return
        (self.__train_params, 
         self.required_train_params, 
         self.default_train_params) = self.__parse_json_params(train_params)

    @property
    def evaluate_params(self):
        """
        获取验证参数
        """
        return self.__evaluate_params

    @evaluate_params.setter
    def evaluate_params(self, eval_params):
        """
        设置验证参数
        """
        if not eval_params:
            return
        (self.__evaluate_params, 
         self.required_evaluate_params, 
         self.default_evaluate_params) = self.__parse_json_params(eval_params)

    def __parse_json_params(self, json_params):
        params = json.loads(json_params)
        required_params = [p for p in params if 'default' not in p]
        default_params = {p['name']: p['default'] for p in params
                          if 'default' in p}
        return params, required_params, default_params

    @classmethod
    def get_user_custom_algorithm_by_name(cls, name: str):
        """
        根据算法名称获取当前用户的自定义算法

        Parameters
        ----------
        name : :obj:`str`
            算法名称。

        Returns
        -------
        Algorithm
            算法对象。
        """
        res = get_with_token(f"{url_base()}/algorithm/custom",
                             params={'name': name})
        if not res or not isinstance(res, dict):
            raise AnyLearnException("请求未能得到有效响应")
        return Algorithm(
            id=res['id'],
            name=res['name'],
            description=res['description'],
            state=res['state'],
            visibility=res['visibility'],
            upload_time=res['upload_time'],
            filename=res['filename'],
            is_zipfile=True if res['is_zipfile'] == 1 else False,
            file_path=res['file'],
            size=res['size'],
            creator_id=res['creator_id'],
            node_id=res['node_id'],
            owner=res['owner'],
            tags=res['tags'],
            mirror_id=res['mirror_id'],
            train_params=res['train_params'],
            evaluate_params=res['evaluate_params'],
            follows_anylearn_norm=res['follows_anylearn_norm'],
            entrypoint_training=res['entrypoint_training'],
            output_training=res['output_training'],
            entrypoint_evaluation=res['entrypoint_evaluation'],
            output_evaluation=res['output_evaluation'],
            git_address=res['git_address'],
            git_migrated=res['git_migrated'],
        )

    def sync_finish(self, checkout_sha:str=None):
        """
        算法代码仓库同步完成接口

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        None
        """
        self._check_fields(required=['id'])
        post_with_token(f"{url_base()}/resource/sync_finish",
                        data={
                            'algorithm_id': self.id,
                            'checkout_sha': checkout_sha,
                        })
        self.get_detail()
        if self.state != ResourceState.READY:
            raise AnyLearnException("Algorithm is not ready after sync finish")
