# -*- coding: utf-8 -*-
import random, time
from lcyframe.libs.beanstalk_route import BsRoute
from base import BaseModel

"""
目前仅支持监听default tube；所有任务都在此通道
"""

@BsRoute.tasks
class DefaultEvents(BaseModel):
    tube = "default2"

    @classmethod
    def event(cls, job):
        """
        返回False：job不会删除
        返回非False：job会被删除
        :param x:
        :return:
        """
        print(job)
        return True
