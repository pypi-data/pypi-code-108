from typing import Optional

from anylearn.interfaces.base import BaseObject
from anylearn.utils.api import url_base, get_with_token
from anylearn.utils.errors import (
    AnyLearnException,
    AnyLearnMissingParamException,
)


class QuotaGroup(BaseObject):
    """
    AnyLearn资源组类

    Attributes
    ----------
    id
        资源组的唯一标识符，自动生成，由QGRP+uuid1生成的编码中后28个有效位（小写字母和数字）组成
    name
        资源组名称（非空 长度1~50）
    level
        资源等级（Guarantee或BestEffort）
    node_level
        节点匹配等级
    capacity
        资源组内各资源类型的容量
    default
        资源组默认的单次任务申请用量
    capacity
        资源组内各资源类型的实际用量
    load_detail
        初始化时是否加载详情
    """

    _fields = {
        'required': {
            'create': [],
            'update': [],
        },
        'payload': {
            'create': [],
            'update': [],
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
                 level: Optional[str]=None,
                 node_level: Optional[str]=None,
                 capacity: Optional[dict]=None,
                 default: Optional[dict]=None,
                 allocated: Optional[dict]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            资源组的唯一标识符，自动生成，由QGRP+uuid1生成的编码中后28个有效位（小写字母和数字）组成
        name
            资源组名称（非空 长度1~50）
        level
            资源等级（Guarantee或BestEffort）
        node_level
            节点匹配等级
        load_detail
            初始化时是否加载详情
        capacity
            资源组内各资源类型的容量
        default
            资源组默认的单次任务申请用量
        capacity
            资源组内各资源类型的实际用量
        """
        self.id = id
        self.name = name
        self.level = level
        self.node_level = node_level
        self.capacity = capacity
        self.default = default
        self.allocated = allocated
        super().__init__(id=id, load_detail=load_detail)

    @classmethod
    def get_list(cls):
        """
        获取资源组列表
        
        Returns
        -------
        List [QuotaGroup]]
            资源组对象的集合。
        """
        res = get_with_token(f"{url_base()}/quota_group/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            QuotaGroup(
                id=item['id'],
                name=item['name'],
                level=item['level'],
                node_level=item['node_level'],
                capacity=item['capacity'],
                default=item['default'],
                allocated=item['allocated'],
            )
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
        if not self.id and not self.name:
            raise AnyLearnMissingParamException("QuotaGroup缺少必要字段：id或name")
        params = {'id': self.id} if self.id else {'name': self.name}
        res = get_with_token(f"{url_base()}/quota_group/query", params=params)
        if not res or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        res = res[0]
        self.__init__(
            id=res['id'],
            name=res['name'],
            level=res['level'],
            node_level=res['node_level'],
            capacity=res['capacity'],
            default=res['default'],
            allocated=res['allocated'],
        )

    def available(self):
        used = dict({k: 0 for k in self.capacity.keys()}, **self.allocated)
        return {k: self.capacity[k] - used[k] for k in self.capacity.keys()}

    def save(self):
        raise AnyLearnException("Saving for QuotaGroup is not supported in SDK")

    def delete(self):
        raise AnyLearnException("Deleting for QuotaGroup is not supported in SDK")

    def _namespace(self):
        return "quota_group"
