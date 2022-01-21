#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bson.objectid import ObjectId
from base import BaseSchema
import time


class DemoSchema(BaseSchema):
    """
    接口名称
    """

    collection = "demo"
    is_shard = False        # 是否分表
    shard_key = "uid"       # 分表键

    def __init__(self):
        self._id = ObjectId()
        self.uid = 1
        self.sex = 1

    @classmethod
    def shard_rule(cls, shard_key_value):
        """
        复写分表规则
        :param shard_key_value:
        :return:
        """
        cls.shard_key = "uid"
        return shard_key_value % 20
