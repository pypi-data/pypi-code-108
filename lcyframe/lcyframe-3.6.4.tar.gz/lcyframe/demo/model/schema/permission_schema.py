#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bson.objectid import ObjectId
from base import BaseSchema
import time

class PermissionGroupSchema(BaseSchema):
    """
    permission
    """

    collection = "permission_group"

    def __init__(self):
        self._id = ObjectId()
        self.available = True   # ******
        self.permission_class = {}  # ******
        self.gid = 1    # ******ID
        self.name = "******2"
        self.pid = 1    # ******ID
        self.desc = ""  # ******
        self.create_at = int(time.time())
        self.update_at = int(time.time())

class PermissionClassSchema(BaseSchema):
    """
    permission
    """

    collection = "permission_class"

    def __init__(self):
        self._id = ObjectId()
        self.available = True   # ******
        self.bit_mp = {}  # ******bit
        self.key = 1    # ******ID
        self.name = "******"
        self.desc = ""  # ******
        self.create_at = int(time.time())
        self.update_at = int(time.time())
