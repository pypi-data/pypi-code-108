#!/usr/bin/env python
# -*- coding:utf-8 -*-
from base import BaseModel
from model.schema.admin_schema import AdminSchema

class AdminModel(BaseModel, AdminSchema):

    @classmethod
    def get_admin(cls, admin_id, **kwargs):
        """
        详情
        :return:
        :rtype:
        """
        d = cls.find_one_by_oid(admin_id)
        return cls._parse_data(d)


    @classmethod
    def get_admin_by_spec(cls, spec, **kwargs):
        """
        详情
        :return:
        :rtype:
        """
        d = cls.find_one(spec)
        return cls._parse_data(d)


    @classmethod
    def get_admin_list_by_last_id(cls, last_id, count, **kwargs):
        """
        前端列表
        :return:
        :rtype:
        """
        spec = {}
        spec.update(kwargs.get("spec", {}))
        data_list, last_id = cls.find_list_by_last_id(spec,
                                                      count,
                                                      sort=[("create_at", -1), ],
                                                      fields=False,
                                                      last_id_field=False)
        return [cls._parse_data(d) for d in data_list if d], last_id

    @classmethod
    def get_admin_list_by_page(cls, page, count, **kwargs):
        """
        后台列表
        :return:
        :rtype:
        """
        spec = {}
        spec.update(kwargs.get("spec", {}))
        data_list, pages = cls.find_list_by_page(spec,
                                                 page,
                                                 count,
                                                 sort=[("create_at", -1), ],
                                                 fields=False)
        return [cls._parse_data(d) for d in data_list if d], pages

    @classmethod
    def create_admin(cls, *args, **kwargs):
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
    def modify_admin(cls, *args, **kwargs):
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
    def delete_admin(cls, admin_id, **kwargs):
        """
        删除
        :return:
        :rtype:
        """
        return cls.update({"_id": admin_id}, {"state": -1})

    @classmethod
    def _parse_data(cls, d, **kwargs):
        """
        组装单条数据
        :return:
        :rtype:
        """
        if not d:
            return {}

        d["admin_id"] = d.pop("_id", "")

        return d


