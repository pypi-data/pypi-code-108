from typing import Optional

from anylearn.utils.api import url_base, get_with_token
from anylearn.utils.errors import AnyLearnException

class Mirror:
    """
    AnyLearn镜像类，仅提供镜像列表接口

    Attributes
    ----------
    id
        镜像的唯一标识符，自动生成，由MIRR+uuid1生成的编码中后28个有效位（小写字母和数字）组成
    name
        镜像的名称
    requirements
        依赖包
    """

    def __init__(self,
                 id: Optional[str]=None,
                 name: Optional[str]=None,
                 requirements: Optional[str]=None):
        """
        AnyLearn镜像类，仅提供镜像列表接口

        Parameters
        ----------
        id
            镜像的唯一标识符，自动生成，由MIRR+uuid1生成的编码中后28个有效位（小写字母和数字）组成
        name
            镜像的名称
        requirements
            依赖包
        """
        self.id = id
        self.name = name
        self.requirements = requirements

    @classmethod
    def get_list(cls) -> list:
        """
        获取镜像列表
        
        Returns
        -------
        List [Mirror]
            镜像对象的集合。
        """
        res = get_with_token(f"{url_base()}/mirror/list")
        if res is None or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        return [
            Mirror(id=m['id'], name=m['name'], requirements=m['requirements'])
            for m in res
        ]

    def __str__(self):
        return f"Mirror(name={self.name})"

    def __repr__(self):
        d = self.__dict__
        kv = ", ".join([f"{k}={d[k]!r}" for k in d])
        return f"{self.__class__.__name__}({kv})"
