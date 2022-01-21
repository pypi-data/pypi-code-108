#!/usr/bin/env python
# -*- coding:utf-8 -*-
from base import BaseSchema
from bson.objectid import ObjectId
import random
import string
import time

class IdGeneratorSchema(BaseSchema):
    """
    自增字段表
    """
    collection = "id_generator"
    def __init__(self):
        self._id = ObjectId()
        self.uid = 100000  # ******
        self.sid = 2000
        self.pid = 3000


