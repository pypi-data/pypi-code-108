#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lcyframe import BaseHandler as Handler
from lcyframe import BaseModel as Model
from lcyframe import BaseSchema as Schema
from utils import errors, helper, keys

class BaseHandler(Handler):
    """
    This is the base class RequestHandler you apply
    You can rewrite the function you want and inherit the frame parent class
    """
    api_error = errors
    helper = helper
    keys = keys

    def write(self, chunk):
        if type(chunk) is dict and chunk.get("code") == 0:
            chunk['code'] = 200
        return super(BaseHandler, self).write(chunk)

class BaseModel(Model):
    """
    This is the base class Model you apply
    You can rewrite the function you want and inherit the frame parent class
    """
    api_error = errors
    helper = helper
    keys = keys


class BaseSchema(Schema):

    @classmethod
    def shard_rule(cls, shard_key_value):
        """
        :param shard_key_value:
        :return: table_value

        This is default rule by `mod10`
        you can rewrite like this

        :example :: DemoSchema.yml
            def shard_rule(shard_key_value):
                do_your_thing
                ...
        """
        return cls.mod10(shard_key_value)
