#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bson.objectid import ObjectId
from lcyframe import utils
from base import BaseSchema

class AdminSchema(BaseSchema):
    """
    admin ******
    """
    collection = "admin"

    def __init__(self):
        self._id = ObjectId()
        self.uid = 0    # ******uid
        self.user_name = ''
        self.nick_name = ""  # ******
        self.pass_word = ""  # ****** MD5(******+salt)
        self.salt = utils.gen_salt()  # ******
        self.mobile = ''  # ******
        self.email = ""  # ******
        self.sex = 1  # ****** 0:******  1:******
        self.gid = 1024  # ****** 1024 ****** 2 ******
        self.state = 1
