#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bson.objectid import ObjectId
from base import BaseSchema
from lcyframe.libs import utils

class UserSchema(BaseSchema):
    """
    user
    用户
    """

    collection = "user"

    def __init__(self):
        self._id = ObjectId()
        self.uid = utils.random.randint(1, 50000000)
        self.sex = 1
        self.city = utils.random_int(5)
        self.age = utils.random.randint(20, 80)
        self.addr = utils.random_string(20)
        self.iphone = str(utils.random_int(10))
        self.name = utils.random_string(10)
        self.money = int(utils.random_int(5))


