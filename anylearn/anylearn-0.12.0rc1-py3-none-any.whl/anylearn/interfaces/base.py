from typing import Optional
from abc import ABC, abstractclassmethod, abstractmethod

from anylearn.utils.api import (
    url_base,
    post_with_token,
    put_with_token,
    delete_with_token
)
from anylearn.utils.errors import (
    AnyLearnException,
    AnyLearnMissingParamException
)


class BaseObject(ABC):

    """具体资源信息配置"""
    _fields = {
        # 资源创建/更新请求包体中必须包含且不能为空的字段
        'required': {
            'create': [],
            'update': [],
        },
        # 资源创建/更新请求包体中包含的所有字段
        'payload': {
            'create': [],
            'update': [],
        },
    }
    """
    所有子类中需定制 :obj:`_fields` 的字段内容以满足创建/更新所需要的字段

    创建/更新对象时：

    - 必须包含且不能为空的字段 :obj:`_fields['required']`
    - 所有字段 :obj:`_fields['payload']`
    """

    def __init__(self,
                 id: Optional[str]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            对象的ID
        load_detail
            初始化对象时是否加载详情
        """
        self.id = id
        if load_detail:
            self.get_detail()

    @abstractclassmethod
    def get_list(self) -> list:
        """
        获取对象列表，子类需实现此抽象方法
        """
        raise NotImplementedError

    @abstractmethod
    def get_detail(self):
        """
        获取对象详情，子类需实现此抽象方法
        """
        raise NotImplementedError

    @abstractmethod
    def _namespace(self):
        """
        - 子类的命名空间，调用此方法以获取子类的名称用于异常信息输出等，以 :obj:`User` 为例， :obj:`_namespace` 可以为 :obj:`user` 
        - 子类需实现此抽象方法
        """
        raise NotImplementedError

    def save(self):
        """
        创建或更新对象

        - 对象包含非空属性 :obj:`id` 时为更新，否则为创建
        - 创建对象时必须包含且不能为空的字段： :obj:`_fields['required']['create']`
        - 创建对象时包含的所有字段： :obj:`_fields['payload']['create']`
        - 更新对象时必须包含且不能为空的字段： :obj:`_fields['required']['update']`
        - 更新对象时包含的所有字段： :obj:`_fields['payload']['update']`
            
        Returns
        -------
        bool
            True or False
        """
        if self.id:
            self._check_fields(required=self._fields['required']['update'])
            return self._update()
        else:
            self._check_fields(required=self._fields['required']['create'])
            return self._create()

    def _update(self):
        """
        更新对象，如果子类更新方法与此有较大差异可以重写此方法
        """
        data = self._payload_update()
        res = put_with_token(self._url_update(), data=data)
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        return self.id == res['data']

    def _payload_update(self):
        return {k: self.__getattribute__(k)
                for k in self._fields['payload']['update']}

    def _create(self):
        """
        创建对象，如果子类创建方法与此有较大差异可以重写此方法
        """
        data = self._payload_create()
        res = post_with_token(self._url_create(), data=data)
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        self.id = res['data']
        return True

    def _payload_create(self):
        return {k: self.__getattribute__(k)
                for k in self._fields['payload']['create']}

    def delete(self, force: bool=False):
        """
        删除对象

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        bool
            True or False
        """
        self._check_fields(required=['id'])
        res = delete_with_token(self._url_delete(),
                                params={
                                    'id': self.id,
                                    'force': 1 if force else 0,
                                })
        if not res or 'data' not in res:
            raise AnyLearnException("请求未能得到有效响应")
        return self.id == res['data']

    def _check_fields(self, required=[]):
        """
        对象检查属性是否存在
        """
        missed = [field
                  for field in required
                  if not self.__getattribute__(field)]
        if missed:
            msg = f"{self.__class__.__name__}缺少必要字段：{missed}"
            raise AnyLearnMissingParamException(msg)

    def _url_create(self):
        """
        创建对象url，如果子类创建对象接口名称不是 :obj:`add` ，可以重写此方法来定制接口名称
        """
        return f"{url_base()}/{self._namespace()}/add"

    def _url_update(self):
        """
        更新对象url，如果子类更新对象接口名称不是 :obj:`update` ，可以重写此方法来定制接口名称
        """
        return f"{url_base()}/{self._namespace()}/update"

    def _url_delete(self):
        """
        删除对象url，如果子类删除对象接口名称不是 :obj:`delete` ，可以重写此方法来定制接口名称
        """
        return f"{url_base()}/{self._namespace()}/delete"

    def __repr__(self):
        d = self.__dict__
        kv = ", ".join([f"{k}={d[k]!r}" for k in d])
        return f"{self.__class__.__name__}({kv})"
