#!/usr/bin/env python
# -*- coding:utf-8 -*-
from base import BaseModel
from model.schema.igGenerator_schema import IdGeneratorSchema

class IdGeneratorModel(BaseModel, IdGeneratorSchema):
    @classmethod
    def gen_uid_id(cls, seq=1):
        """自动分配UID"""
        z = cls.find_and_modify({}, {'$inc': {"uid": seq}})["uid"]
        return z

    @classmethod
    def gen_order_id(cls, prefix="O", seq=1):
        """分配订单ID"""
        pass

    @classmethod
    def gen_company_id(cls, prefix="CD", seq=1):
        """分配企业ID"""
        z = cls.find_and_modify({}, {'$inc': {"company_id": seq}})["company_id"]
        return "%s%07d" % (prefix, z)

    @classmethod
    def gen_agent_id(cls, prefix="A", seq=1):
        """分配代理ID"""
        z = cls.find_and_modify({}, {'$inc': {"agent_id": seq}})["agent_id"]
        return "%s%07d" % (prefix, z)

