from datetime import datetime
from typing import Optional

from anylearn.interfaces.base import BaseObject
from anylearn.utils.api import url_base, get_with_token
from anylearn.utils.errors import (
    AnyLearnException,
    AnyLearnNotSupportedException
)


class ServiceRecordState:
    """
    服务状态标识：

    - 0(WAITING)表示等待执行
    - 1(RUNNING)表示执行中
    - 2(FINISHED)表示已完成
    - -1(FAILED)表示失败
    """
    WAITING = 0
    RUNNING = 1
    FINISHED = 2
    FAILED = -1


class ServiceRecord(BaseObject):
    """
    Attributes
    ----------
    id
        模型服务结果的唯一标识符，自动生成，由SERE+uuid1生成的编码中后28个有效位（小写字母和数字）组成
    service_id
        模型服务ID
    inference_data_file_id
        上传文件ID
    state
        服务记录运行状态
    create_time
        服务记录创建时间
    finish_time
        服务记录完成时间
    result
        服务推理结果
    error
        错误信息
    load_detail
        初始化时是否加载详情
    """

    def __init__(self,
                 id,
                 service_id: Optional[str]=None,
                 inference_data_file_id: Optional[str]=None,
                 state: Optional[int]=None,
                 create_time: Optional[datetime]=None,
                 finish_time: Optional[datetime]=None,
                 result: Optional[str]=None,
                 error: Optional[str]=None,
                 load_detail=False):
        """
        Parameters
        ----------
        id
            模型服务结果的唯一标识符，自动生成，由SERE+uuid1生成的编码中后28个有效位（小写字母和数字）组成
        service_id
            模型服务ID
        inference_data_file_id
            上传文件ID
        state
            服务记录运行状态
        create_time
            服务记录创建时间
        finish_time
            服务记录完成时间
        result
            服务推理结果
        error
            错误信息
        load_detail
            初始化时是否加载详情
        """
        self.service_id = service_id
        self.inference_data_file_id = inference_data_file_id
        self.state = state
        self.create_time = create_time
        self.finish_time = finish_time
        self.result = result
        self.error = error
        super().__init__(id=id, load_detail=load_detail)
    
    @classmethod
    def get_list(cls):
        """
        AnyLearnSDK接口不支持获取服务记录列表
        """
        raise AnyLearnNotSupportedException

    def get_detail(self):
        """
        获取服务记录详细信息

        - 对象属性 :obj:`id` 应为非空

        Returns
        -------
        ServiceRecord
            服务记录对象。
        """
        self._check_fields(required=['id'])
        res = get_with_token(f"{url_base()}/service_record/query",
                             params={ 'id': self.id })
        if not res or not isinstance(res, list):
            raise AnyLearnException("请求未能得到有效响应")
        res = res[0]
        self.__init__(id=res['id'], service_id=res['service_id'],
                      inference_data_file_id=res['file_id'],
                      state=res['state'],
                      create_time=res['create_time'],
                      finish_time=res['finish_time'],
                      result=res['result'],
                      error=res['error'])
    
    def save(self):
        """
        AnyLearnSDK接口不支持服务记录创建
        """
        raise AnyLearnNotSupportedException

    def delete(self):
        """
        AnyLearnSDK接口不支持服务记录删除
        """
        raise AnyLearnNotSupportedException

    def _namespace(self):
        return "service_record"
