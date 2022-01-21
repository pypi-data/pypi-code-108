from datetime import datetime
import requests
from typing import Optional

from anylearn.utils.api import url_base, get_with_token, put_with_token, patch_with_token
from anylearn.utils.errors import AnyLearnException
from anylearn.interfaces.base import BaseObject


class User(BaseObject):
    """
    AnyLearn用户类，以方法映射训练任务CRUD相关接口
    
    Attributes
    ----------
    id
        用户的唯一标识符，自动生成，由USER+uuid1生成的编码中后28个有效位（小写字母和数字）组成
    token
        单点登录令牌
    username
        用户名
    password
        用户密码
    namespace
        命名空间
    email
        邮箱
    role
        用户角色
    algorithm_tree
        暂时忽略不用
    collected_algorithm
        暂时忽略不用
    own_algorithms
        用户算法集合
    own_models
        用户模型集合
    own_files
        用户文件集合
    create_time
        创建时间
    own_datasets
        用户数据集集合
    load_detail
        初始化时是否加载详情
    """

    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': ['username', 'password', 'email'],
            'update': ['id'],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': ['id', 'username', 'password', 'email'],
            'update': ['id', 'username', 'email', 'role'],
        },
    }
    """
    创建/更新对象时：

    - 必须包含且不能为空的字段 :obj:`_fields['required']`
    - 所有字段 :obj:`_fields['payload']`
    """

    def __init__(self,
                 id: Optional[str]=None,
                 token: Optional[str]=None,
                 username: Optional[str]=None,
                 password: Optional[str]=None,
                 namespace: Optional[str]=None,
                 email: Optional[str]=None,
                 role: Optional[str]=None,
                 algorithm_tree: Optional[str]=None,
                 collected_algorithm: Optional[list]=None,
                 own_algorithms: Optional[list]=None,
                 own_models: Optional[list]=None,
                 own_files: Optional[list]=None,
                 create_time: Optional[datetime]=None,
                 own_datasets: Optional[list]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            用户的唯一标识符，自动生成，由USER+uuid1生成的编码中后28个有效位（小写字母和数字）组成
        token
            单点登录令牌
        username
            用户名
        password
            用户密码
        namespace
            命名空间
        email
            邮箱
        role
            用户角色
        algorithm_tree
            暂时忽略不用
        collected_algorithm
            暂时忽略不用
        own_algorithms
            用户算法集合
        own_models
            用户模型集合
        own_files
            用户文件集合
        create_time
            创建时间
        own_datasets
            用户数据集集合
        load_detail
            初始化时是否加载详情
        """
        self.id = id
        self.token = token
        self.username = username
        self.password = password
        self.namespace = namespace
        self.email = email
        self.role = role
        self.algorithm_tree = algorithm_tree
        self.collected_algorithm = collected_algorithm
        self.own_algorithms = own_algorithms
        self.own_datasets = own_datasets
        self.own_models = own_models
        self.own_files = own_files
        self.create_time = create_time
        self.load_detail = load_detail
        super().__init__(id=id, load_detail=load_detail)

    def _url_create(self):
        return f"{url_base()}/{self._namespace()}/registry"

    def _url_update(self):
        return f"{url_base()}/{self._namespace()}"

    def _url_delete(self):
        return f"{url_base()}/{self._namespace()}"

    def _create(self):
        data = self._payload_create()
        res = requests.post(self._url_create(), data=data)
        res.raise_for_status()
        res.encoding = "utf-8"
        res = res.json()
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        self.id = res['data']
        return True

    def get_detail(self):
        """
        获取用户详细信息

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        User
            用户对象。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/user",
                             params={'id': self.id})
        if not res or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        res = res[0]
        self.__init__(id=res['id'], username=res['username'], namespace=res['namespace'],
                      email=res['email'], role=res['role'], own_algorithms=res['own_algorithms'],
                      collected_algorithm=res['collected_algorithm'], own_datasets=res['own_datasets'],
                      own_models=res['own_models'], own_files=res['own_files'])

    @classmethod
    def user_collection(cls, ids: str):
        """
        获取用户集合

        Parameters
        ----------
        ids : :obj:`str`
            要查询的用户ID,多用户用逗号 :obj:`,` 隔开。

        Returns
        -------
        List[User]
            用户对象的集合。
        """
        res = get_with_token(f"{url_base()}/user/collection",
                             params={'collection': ids})
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            User(id=item['id'], username=item['username'],
                 role=item['role'], email=item['email'])
            for item in res
        ]

    def change_password(self, old_password: str, new_password: str):
        """
        修改密码

        - 对象属性 :obj:`id` 应为非空

        :param old_password: :obj:`str`
                        旧密码。
        :param new_password: :obj:`str`
                        新密码。

        :return: 
            .. code-block:: json

                {
                  "data": "USER123",
                  "message": "密码修改成功"
                }
        """

        self._check_fields(required=['id'])
        data = {
            'id': self.id,
            'old_password': old_password,
            'new_password': new_password,
        }
        res = put_with_token(f"{url_base()}/user/password",
                             data=data)
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        return res

    @classmethod
    def get_list(cls):
        """
        获取用户列表
        
        Returns
        -------
        List [User]
            用户对象的集合。
        """
        res = get_with_token(f"{url_base()}/user/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            User(id=item['id'], username=item['username'],
                 role=item['role'], email=item['email'])
            for item in res
        ]

    @classmethod
    def user_check(cls, username: str):
        """
        用户名查重

        Parameters
        ----------
        username : :obj:`str`
            检查用户名是否重复。
        
        Returns
        -------
        bool
            True or False
        """
        if not username:
            raise AnyLearnException("username值不能为空")
        res = requests.get(f"{url_base()}/user/check",
                           params={'username': username})
        res.raise_for_status()
        res.encoding = "utf-8"
        res = res.json()
        if not isinstance(res, bool):
            raise AnyLearnException("请求未能得到有效响应")
        return res

    @classmethod
    def update_role_resource_count(cls, max_gpu: int, max_mem: int):
        """
        更新角色GPU和显存最大数量

        :param max_gpu: :obj:`int`
                        GPU数量。
        :param max_mem: :obj:`int`
                        显存数量。

        :return: 
            .. code-block:: json

                {
                  "msg": "user角色最大GPU和显存数量已分别成功设置为2,26"
                }
        """
        data = {
            'max_gpu': max_gpu,
            'max_mem': max_mem,
        }
        res = put_with_token(f"{url_base()}/user/role",
                             data=data)
        if not res or str (max_mem) not in res['msg']:
            raise AnyLearnException("请求未能得到有效响应")
        return res

    @classmethod
    def update_user_resource_count(cls, id: str, max_gpu: int, max_mem: int):
        """
        单独更新某一用户GPU和显存最大数量

        :param id: :obj:`str`
                        被更新的用户ID。
        :param max_gpu: :obj:`int`
                        GPU数量。
        :param max_mem: :obj:`int`
                        显存数量。

        :return: 
            .. code-block:: json

                {
                  "data": "USER123",
                  "msg": "用户最大GPU和显存数量已分别成功设置为3,18"
                }
        """
        data = {
            'id': id,
            'max_gpu': max_gpu,
            'max_mem': max_mem,
        }
        res = patch_with_token(f"{url_base()}/user/user",
                             data=data)
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        return res

    def _namespace(self):
        return "user"
