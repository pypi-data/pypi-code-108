#!/usr/bin/env python
# -*- coding:utf-8 -*-
from lcyframe import BaseModel
from model.schema.user_schema import UserSchema


class UserModel(BaseModel, UserSchema):

    @classmethod
    def get(cls, *args, **kwargs):
        """
        单条记录
        :return:
        :rtype:
        """
        pass

    @classmethod
    def query(cls, *args, **kwargs):
        """
        列表
        :return:
        :rtype:
        """
        pass

    @classmethod
    def create(cls, *args, **kwargs):
        """
        创建
        :return:
        :rtype:
        """
        pwd = kwargs.pop("pass_word")

        if not pwd or not kwargs["user_name"]:
            return -1

        if cls.find_one({"nick_name": kwargs["nick_name"]}):
            return - 2

        docs = {}
        docs["gid"] = kwargs["gid"]
        docs["uid"] = cls.IdGeneratorModel.gen_uid_id()
        docs["salt"] = cls.utils.gen_salt()
        docs["pass_word"] = cls.utils.gen_salt_pwd(pwd, docs["salt"])
        docs.update(kwargs)
        cls.insert(docs)
        return docs["uid"]

    @classmethod
    def modify(cls, *args, **kwargs):
        """
        修改
        :return:
        :rtype:
        """
        spec = {"uid": kwargs.pop("uid")}
        update_docs = {}
        for k, v in kwargs.items():
            if k not in vars(cls.UserSchema()):
                continue

            # 改密码
            if k == "pass_word" and kwargs["pass_word"]:
                update_docs[k] = cls.utils.gen_salt_pwd(kwargs["pass_word"], kwargs["salt"])
            # 改用户组
            elif k == "gid":
                update_docs[k] = v
                update_docs["permission"] = cls.UserSchema.gid_permission[v]
            else:
                update_docs[k] = v

        return cls.update(spec, update_docs)

    @classmethod
    def delete(cls, *args, **kwargs):
        """
        删除
        :return:
        :rtype:
        """
        pass

