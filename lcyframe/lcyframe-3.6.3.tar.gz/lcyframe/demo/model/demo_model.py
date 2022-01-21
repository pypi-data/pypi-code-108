#!/usr/bin/env python
# -*- coding:utf-8 -*-
from base import BaseModel
from model.schema.demo_schema import DemoSchema

class DemoModel(BaseModel, DemoSchema):

    @classmethod
    def get_demo(cls, demo_id, **kwargs):
        """
        详情
        :return:
        :rtype:
        """
        # 获取当前表所有字段
        fields = DemoSchema.fields()

        # mongo

        # 新增记录（1条或者多条）
        # 1、框架的方法
        id = cls.insert({"uid": 102})
        ids = cls.insert([{"uid": 102}, {"uid": 103}], ordered=False)   # ordered并发写入，不保证顺序
        # 2、原生方法
        # cls.mongo.collection.insert_one({"uid": 102})
        # cls.mongo.collection.insert_many([{"uid": 102}, {"uid": 103}])
        
        # 删除
        # 删除单条
        # deleted_count = cls.remove({"uid": 103}, multi=False)
        # # 删除多条
        # deleted_count = cls.remove({"uid": 102})
        
        # 查看
        data = cls.find_one({"yyy": 102})
        datas = cls.find({"uid": 102}, fields={"uid": 1}, skip=1, limit=10, sort={"uid": 1})
        
        # 替换/覆盖/新增  result.matched_count,result.modified_count,result.upserted_id
        # result = cls.replace_one({"uid": 102}, {"uidx": 102})                             # 修改字段
        # result = cls.replace_one({"xxx": 100}, {"xxx": 100}, upsert=True)                 # 没有则新增
        # result = cls.replace_one({"xxx": 200}, {"yyy": 200, "zzz": 100}, upsert=True)     # 没有则新增一条，并新增一个字段
        
        # 更新数据
        # update_state = cls.update({"yyy": 200},cls.find {"$inc": {"xxx": 1}})
        # update_state = cls.update({"yyy": 200}, {"$inc": {"xxx": 1}}, multi=True)
        # <class 'dict'>: {'n': 6, 'nModified': 6, 'ok': 1.0, 'updatedExisting': True}
        # result = cls.update({"yyy": 200}, {"$inc": {"xxx": 1}}, multi=True, check_updated_state=False)
        # 没有则新增
        # update_state = cls.update({"yyy": 203}, {"$inc": {"xxx": 1}}, upsert=True)
            
        # 原子操作
        # 更新,默认没有则新增，upsert=True，new=True返回更新后的文档
        # result = cls.find_and_modify({"yyy": 300}, {"$inc": {"xxx": 1}}, new=True)  #
        # 替换/覆盖/新增
        # result = cls.find_one_and_replace({"yyy": 300}, {"xxx": 1}, return_document=True)
        # result = cls.find_one_and_replace({"yyy": 400}, {"xxx": 1}, sort={"a": -1}, return_document=True)
        # result = cls.find_one_and_replace({"yyy": 500}, {"xxx": 1}, sort=[("a", -1)], return_document=True)
        # 原子更新
        # result = cls.find_one_and_update({"yyy": 400}, {"$inc": {"xxx": 1}}, sort=[("a", 1)], return_document=True)
        # 原子删除
        # result = cls.find_one_and_delete({"yyy": 400}, sort=[("a", 1)])
        # result = cls.find_one_and_delete({"yyy": 400}, sort={"a": -1}, projection={"_id": 0})

        # 过滤
        result = cls.distinct("yyy", {"a": 2})
        result = cls.distinct("_id", {"a": 2})
        result = cls.distinct("yyy", {"a": 2}, **{"maxTimeMS": 5000})

        # 统计result.upserted_id
        count = cls.count()
        count = cls.count({"uid": 102}, skip=10)
        
        # myqsl
        # cls.mysql.insert(cls.collection, [{"name": 2}, {"name": 3}])
        # data = cls.mysql.query_sql(sql="select * from demo where name=(name)", params={"name": 2})
        # data = cls.mysql.query_sql(sql="select * from demo where name=%s", params=[2, ])
        return cls._parse_data(fields)


    @classmethod
    def get_demo_by_spec(cls, spec, **kwargs):
        """
        详情
        :return:
        :rtype:
        """
        d = cls.find_one(spec)
        return cls._parse_data(d)


    @classmethod
    def get_demo_list_by_last_id(cls, last_id, count, **kwargs):
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
    def get_demo_list_by_page(cls, page, count, **kwargs):
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
    def create_demo(cls, *args, **kwargs):
        """
        创建
        :return:
        :rtype:
        """
        pass

    @classmethod
    def modify_demo(cls, *args, **kwargs):
        """
        修改
        :return:
        :rtype:
        """
        pass

    @classmethod
    def delete_demo(cls, demo_id, **kwargs):
        """
        删除
        :return:
        :rtype:
        """
        return cls.update({"_id": demo_id}, {"state": -1})

    @classmethod
    def _parse_data(cls, d, **kwargs):
        """
        组装单条数据
        :return:
        :rtype:
        """
        if not d:
            return {}

        d["demo_id"] = str(d.pop("_id", ""))

        return d


