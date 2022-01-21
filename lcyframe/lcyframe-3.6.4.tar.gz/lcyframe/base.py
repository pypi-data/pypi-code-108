#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import json
import logging
import random
import time
import types
from functools import wraps
from traceback import format_exc

from bson.objectid import ObjectId
from tornado.web import HTTPError
from tornado.web import RequestHandler
from lcyframe.libs import Copyright, errors
from lcyframe.libs import utils
from lcyframe.libs.funts import get_params, get_return
from lcyframe.libs.permissions import Permission


class BaseHandler(RequestHandler):
    __structure__ = {}
    logging = logging
    app_config = {}
    model = None
    mongo = None
    mysql = None
    redis = None
    ssdb = None
    mq = None
    nsq = None
    mqtt = None
    celery = None
    beanstalk = None
    qiniu = None
    emchat = None
    aes = None
    graylog = None

    def __init__(self, application, request, **kwargs):
        self.application = application
        self.request = request
        super(BaseHandler, self).__init__(application, request, **kwargs)
        if request.headers.get("cdn-src-ip", None):
            request.remote_ip = request.headers["cdn-src-ip"]
        elif request.headers.get("X-Forwarded-For", None):
            try:
                request.remote_ip = request.headers["X-Forwarded-For"].split(",")[0]
            except Exception as e:
                request.remote_ip = self.request.headers.get('X-Real-Ip', '')
        self.cors_config = self.application.app_config.get("cors_config", {})

    def prepare(self):
        if self.request.method == "OPTIONS" and self._allow_cors:
            self.set_cors_header()
            self.set_status(204)
            self.finish()
            return

    @property
    def _allow_cors(self):
        """
        校验授信跨域来路
        :return:
        """
        self.cors_config = self.application.app_config.get("cors_config", {})
        allow = self.cors_config and self.cors_config.get("allow", False)
        self.origin = self.request.headers.get("origin")
        self.cors_config["origin"].append(self.application.app_config["wsgi"]["host"])
        auto_origin = self.cors_config["origin"]
        if not allow or ("*" not in auto_origin and self.origin not in auto_origin):
            raise errors.ErrorCorsUri
        return True

    def set_cors_header(self):
        """通过授信校验后，允许设置响应头"""
        self.set_header("Content-Type", self.cors_config.get("content-type", "text/html") + "; charset=utf-8")
        self.set_header("Access-Control-Allow-Origin", "*" if "*" in self.cors_config.get("origin", "origin") else self.request.headers.get("origin", ""))
        self.set_header("Access-Control-Allow-Headers", ",".join(self.cors_config.get("headers", ["*"])))
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", ",".join(self.cors_config.get("methods", ["GET", "POST", "PUT", "DELETE"])))
        self.set_header("Access-Control-Max-Age", self.cors_config.get("max-age", 60))

    def write_error(self, status_code, **kwargs):
        self.cors_config = self.application.app_config.get("cors_config", {})
        allow = self.cors_config and self.cors_config.get("allow", False)
        if allow:
            self.set_cors_header()

        if status_code == 404:
            return self.write_failed(code=status_code, msg="Not Found", name="HTTP 404")
        elif status_code == 405:
            return self.write_failed(code=status_code, msg="HTTP 405: Method/URL Not Allowed", name="HTTP 405")
        elif status_code == 500:
            typ, value, tb = sys.exc_info()
            logging.error("Uncaught exception %s\n%r", self._request_summary(), self.request, exc_info=(typ, value, tb))

            error = kwargs["exc_info"][1]
            # 把除跨域异常外所有用raise抛出的内置异常类型，都转为200返回，内部保留500异常log
            if isinstance(error, errors.ApiError) and error.code != errors.ErrorCorsUri.code:
                self.set_status(200, "HTTP STATUS 200")

            logging.error("异常时间：" + self.utils.int_to_date_string(self.utils.now(), "%Y-%m-%d %H:%M:%S"))
            if not hasattr(error, "message"):
                message = "%s:%s" % (type(error).__name__, error.args[0]) if error.args else "未知错误"
                logging.error("异常信息：" + message)
            else:
                logging.error("异常码：" + str(error.code))
                logging.error("异常信息：" + error.message)

            logging.error("请求地址: %s %.2fms", self.request.uri, 1000.0 * self.request.request_time())
            logging.error("请求参数: " + (json.dumps(utils.pparams(self.request, self.params), ensure_ascii=False) if hasattr(self, "params") else str(utils.pparams(self.request, self.request.arguments) or {})))
            if not hasattr(error, "code_name") or not hasattr(error, "code"):
                return self.write_failed()
            else:
                return self.write_failed(code=error.code, msg=error.message, name=error.code_name)
        else:
            return self.write_failed()

    def write_success(self, data=None):
        request_time = 1000.0 * self.request.request_time()
        is_slow_request = request_time > int(self.application.app_config["wsgi"].get("slow_request_time", 1000))
        p = self.params if hasattr(self, "params") else {}
        if is_slow_request:
            logging.warning("[%s] %d %s %.2fms", "慢请求", self.get_status(), self._request_summary(), request_time)

        if hasattr(self, "graylog") and self.graylog:
            if self.application.app_config["graylog_config"].get("mode", 0) or is_slow_request:
                self.graylog.from_server(short_message="OK", code=0, host=self.request.host, request_time=int(request_time), remote_ip=self.request.remote_ip,
                                         uri=self.request.path, params=utils.pparams(self.request, p), method=self.request.method)
        return self.write({"code": 0, "msg": "OK", "data": get_return(self, data or {})})

    def write_failed(self, code=1, msg="Error. unknown error", name="HTTP 500"):
        if hasattr(self, "graylog") and self.graylog:
            p = self.params if hasattr(self, "params") else {}
            self.graylog.from_server(short_message=msg, code=code, track=format_exc()[-500:], host=self.request.host, header=self.request.headers._dict,
                                     remote_ip=self.request.remote_ip, uri=self.request.path, params=utils.pparams(self.request, p), method=self.request.method)
        if name:
            self.write({"code": code, "msg": msg, "name": name, "data": None})
            return
        else:
            self.write({"code": code, "msg": msg, "data": None})
            return

    def write(self, chunk):
        # from bson import json_util
        # chunk = json_util.dumps(chunk)
        chunk = utils.check2json(chunk)
        chunk = json.dumps(chunk, ensure_ascii=False)
        return super(BaseHandler, self).write(chunk)

    # def _request_summary(self):
    #     return "- [%s] %s %s (%s)" % (Copyright.frame_name, self.request.method, self.request.uri,
    #                            self.request.remote_ip)

    def json_callback(self, data):
        """json回调跨域
        """
        jsoncallback = self.get_argument("jsoncallback", None)
        if jsoncallback:
            self.write("%s(%s)" % (jsoncallback, json.dumps(data)))
        else:
            self.write(data)

    def restrict(self, count, duration=60):
        """接口访问限制"""

        def wrap(method):
            @wraps(method)
            def has_role(self, *args, **kwargs):
                if not hasattr(self, "redis"):
                    return method(self, *args, **kwargs)

                # 获取客户端ip
                ip = None
                if self.request.headers.get("cdn-src-ip"):
                    ip = self.request.headers.get("cdn-src-ip")
                elif self.request.headers.get("X-Forwarded-For"):
                    z = self.request.headers["X-Forwarded-For"].split(",")
                    if len(z) > 0:
                        ip = z[0]
                ip = ip or self.request.remote_ip

                n = self.redis.incr("restrict:%s" % ip)

                if n == 1:
                    self.redis.expire("restrict:%s" % ip, duration)
                elif n > count:
                    raise HTTPError(503, "Slow Down")

                return method(self, *args, **kwargs)

            return has_role

        return wrap

    @property
    def utils(self):
        return utils

    def get_headers(self, HEADERS=dict()):
        _headers = {}
        if not HEADERS:
            for k, v in self.request.headers.items():
                _headers[k.lower()] = v

        for k, v in HEADERS.items():
            value = self.request.headers.get(k)
            if value is None:
                # 客户端没有传值, 按照默认值类型赋值
                value = v(value) if isinstance(v, types.FunctionType) else v
            else:
                # 按照默认值的类型 转换参数
                value = utils.TypeConvert.apply(v, value)

            _headers[k] = value

        return _headers

    @property
    def Permission(self):
        return Permission.initial()

    @property
    def app_config(self):
        return self.application.app_config

    @property
    def model(self):
        return BaseModel.model



class BaseModel(object):
    logging = logging
    utils = utils
    Permission = None
    api_error = None
    app_config = {}
    model = None
    mongo = None
    mysql = None
    redis = None
    ssdb = None
    mq = None
    nsq = None
    mqtt = None
    celery = None
    beanstalk = None
    qiniu = None
    emchat = None
    aes = None
    graylog = None

    @classmethod
    def _parse_data(cls, d, **kwargs):
        """
        组装单条数据
        :return:
        :rtype:
        """
        return_data = {}
        if not d:
            return {}

        for k, v in d.items():
            # if k in ["pass_word", "salt", "permission"] and k not in kwargs.get("kwargs", {}):
            #     continue
            return_data[k] = v

        return return_data


class BaseSchema(object):
    """
    is_shard = True                           # 是否分表
    shard_key = "uid"                         # 分表键
    shard_rule()                              # 分表规则，允许复写
    """
    collection = ""
    is_shard = False
    shard_key = ""

    @classmethod
    def ts(cls):
        return int(time.time())

    @classmethod
    def fields(cls):
        return vars(cls())

    @classmethod
    def shard_rule(cls, shard_key_value):
        """
        :param shard_key_value:
        :return: table_value

        This is default rule by `mod10`
        you can overwriter like this

        :example ::
            def shard_rule(shard_key_value):
                do_your_thing
                ...
        """
        return cls.mod10(shard_key_value)

    @classmethod
    def get_shard_table(cls, sql=None, shard_key_value=None):
        """
        默认分表规则
        可以在从schema中复写该方法
        :param shard_key:
        :return:
        """
        if cls.is_shard:
            assert sql is not None or shard_key_value is not None
            assert cls.shard_key in cls.fields()
            value = shard_key_value if shard_key_value is not None else cls.get_value_with_sql(sql)
            return cls.collection + "_" + str(cls.shard_rule(value))
        else:
            return cls.collection

    @classmethod
    def get_value_with_sql(cls, sql):
        """
        :param sql:
        :return:
        """
        if cls.shard_key not in sql:
            raise KeyError("When shard table, shard key must in sql")
        return sql[cls.shard_key]

    @classmethod
    def mod10(cls, shard_key_value=None):
        """
        取模10
        :param mod:
        :return:
        """
        if type(shard_key_value) != int:
            raise KeyError("When shard table, shard key type must int")
        return shard_key_value % 10

    @classmethod
    def dbo(cls, sql=None, shard_key_value=None):
        return cls.mongo[cls.get_shard_table(sql=sql, shard_key_value=shard_key_value)]

    @classmethod
    def get_by_oid(cls, oid, shard_key_value=None, **kwargs):
        """
        单条记录
        :return:
        :rtype:
        """
        return cls.find_one_by_oid(oid, shard_key_value=None, **kwargs)

    @classmethod
    def get_by_spec(cls, spec, shard_key_value=None, **kwargs):
        """
        条件查询
        :param spec:
        :return:
        """
        return cls.find_one(spec)

    @classmethod
    def create(cls, **kwargs):
        """
        创建
        :return:
        :rtype:
        """
        docs = cls.fields()
        for k, v in kwargs.items():
            if k in docs:
                docs[k] = v
        return cls.insert(docs)

    @classmethod
    def delete(cls, oid, shard_key_value=None, **kwargs):
        """
        删除
        注意，使用该方法时，默认-1
        :return:
        :rtype:
        """
        return cls.update({"_id": oid}, {"$set": {"state": -1}})

    @classmethod
    def count(cls, sql=None, shard_key_value=None, **kwargs):
        """
        skip: 0
        limit: 0
        maxTimeMS
        :param sql:
        :param shard_key_value:
        :param kwargs:
        :return:
        """
        try:
            count = cls.dbo(shard_key_value=shard_key_value).count_documents(sql or {}, **kwargs)
        except Exception as e:
            count = cls.dbo(shard_key_value=shard_key_value).count(sql or {}, **kwargs)

        return count

    @classmethod
    def insert(cls, docs, shard_key_value=None, **kwargs):
        doc_or_docs = []
        if not docs:
            return None

        if not isinstance(docs, list):
            insert_docs = [docs]
        else:
            insert_docs = docs

        for d in insert_docs:
            d["create_at"] = utils.now()
            d["update_at"] = utils.now()
            s = vars(cls())
            s.update(d)
            doc_or_docs.append(s)

        try:
            if len(insert_docs) == 1:
                data = cls.insert_one(doc_or_docs[0], shard_key_value=None, **kwargs)
            else:
                data = cls.insert_many(doc_or_docs, shard_key_value=None, **kwargs)
        except Exception as e:
            data = cls.dbo(sql=docs, shard_key_value=shard_key_value).insert(doc_or_docs, **kwargs)

        return str(data) if not isinstance(data, list) else list(map(str, data))

    @classmethod
    def insert_one(cls, docs, shard_key_value=None, **kwargs):
        """
        ordered: True(the default) 按顺序写入，报错终端；False，无序并发写入，报错跳过
        :param docs:
        :param shard_key_value:
        :param kwargs:
        :return:
        """

        data = cls.dbo(sql=docs, shard_key_value=shard_key_value).insert_one(docs, **kwargs)
        return str(data.inserted_id)

    @classmethod
    def insert_many(cls, docs, shard_key_value=None, **kwargs):
        """
        ordered: True(the default) 按顺序写入，报错终端；False，无序并发写入，报错跳过
        :param docs:
        :param shard_key_value:
        :param kwargs:
        :return:
        """

        data = cls.dbo(sql=docs, shard_key_value=shard_key_value).insert_many(docs, **kwargs)
        data = list(map(str, data.inserted_ids))
        return data

    @classmethod
    def remove(cls, spec, shard_key_value=None, **kwargs):
        spec = cls.__check_id(spec)
        try:
            if kwargs.pop("multi", True) is True:
                deleted_count = cls.delete_many(spec, is_check_id=True, shard_key_value=shard_key_value, **kwargs)
            else:
                deleted_count = cls.delete_one(spec, is_check_id=True, shard_key_value=shard_key_value, **kwargs)
        except Exception as e:
            deleted_count = cls.dbo(sql=spec, shard_key_value=shard_key_value).remove(spec)

        return deleted_count

    @classmethod
    def delete_one(cls, spec, is_check_id=False, shard_key_value=None, **kwargs):
        if not is_check_id:
            spec = cls.__check_id(spec)
        result = cls.dbo(sql=spec, shard_key_value=shard_key_value).delete_one(spec, **kwargs)
        return result.deleted_count

    @classmethod
    def delete_many(cls, spec, is_check_id=False, shard_key_value=None, **kwargs):
        if not is_check_id:
            spec = cls.__check_id(spec)
        result = cls.dbo(sql=spec, shard_key_value=shard_key_value).delete_many(spec, **kwargs)
        return result.deleted_count

    @classmethod
    def find_one_by_oid(cls, oid, shard_key_value=None, **kwargs):
        """

        :param oid: ObjectId
        :return:
        """
        return cls.find_one({"_id": oid}, shard_key_value=shard_key_value, **kwargs)

    @classmethod
    def find_one(cls, spec=None, shard_key_value=None, **kwargs):
        """
        max_time_ms： 默认最大请求超时 60秒
        :param spec:
        :param shard_key_value:
        :param kwargs:
        :return:
        """
        spec = cls.__check_id(spec)
        kwargs.setdefault("max_time_ms", 60*1000)
        d = cls.dbo(sql=spec, shard_key_value=shard_key_value).find_one(spec or {}, **kwargs) or {}
        return cls._parse_data(cls.__parse_oid(d)) if d else {}

    @classmethod
    def find(cls, spec=None, fields=False, limit=False, skip=False, sort=False, is_cursor=False, shard_key_value=None, **kwargs):
        """
        fields: {"uid": 1}
        limit: 10
        skip: 10
        sort: {"uid": -1}
        :param spec:
        :param cursor:  True 返回游标，否则返回list
        :return:
        """
        cursor = cls.__find(spec, fields, limit, skip, sort, is_cursor, shard_key_value)
        if not is_cursor:
            data_list = [cls._parse_data(cls.__parse_oid(d), **kwargs) for d in cursor if d]
            return data_list
            # return data_list, total_page, cursor.count()
        else:
            return cursor

    @classmethod
    def distinct(cls, distinct, spec, shard_key_value=None, **kwargs):
        """
        根据spec条件，查询并返回键为distinct的列表，且不重复
        # 返回所有uid的列表，且不重复
        cls.distinct("uid", {"a": 2})
        [2, 4]

        example:
        > db.demo.find({"yyy": {"$exists": 1}})
        { "_id" : ObjectId("6138bf73dca4c58a13c81b84"), "yyy" : 400, "update_at" : 1631107579, "xxx" : 2, "a" : 2, "b" : 2 }
        { "_id" : ObjectId("6138c460dca4c58a13c81b8d"), "yyy" : 500, "update_at" : 1631107579, "xxx" : 2, "a" : 2, "b" : 3 }
        { "_id" : ObjectId("6139b44c107f8ef7d49bea5a"), "yyy" : 600, "update_at" : 1631107579, "xxx" : 4, "a" : 1, "b" : 3 }
        { "_id" : ObjectId("6139b490107f8ef7d49bea5b"), "yyy" : 400, "update_at" : 1631107579, "xxx" : 4, "a" : 2, "b" : 3 }
        > db.demo.distinct("yyy")   # 列出所有yyy的值，并且不重复
        [ 400, 500, 600 ]
        > db.demo.distinct("yyy", {"a": 2})   # 当a=2时， 列出所有yyy的值，并且不重复
        [ 400, 500 ]
        > db.demo.distinct("yyy", {"a": 2}, **{"maxTimeMS": 5000})   # 限制5s超时，防止资源耗尽
        [ 400, 500 ]
        :param spec:
        :param distinct:
        :return:
        """
        spec = cls.__check_id(spec)
        if not kwargs:  # 利用cursor游标
            result = cls.__find(spec, is_cursor=True, shard_key_value=shard_key_value).distinct(distinct)
        else:
            result = cls.dbo(shard_key_value=shard_key_value).distinct(key=distinct, filter=spec, **kwargs)

        for index, value in enumerate(result):
            if type(value) is float and int(value) == value:
                result[index] = int(value)
            elif isinstance(value, ObjectId):
                result[index] = str(value)
            else:
                result[index] = value

        return result

    @classmethod
    def aggregate(cls, pipeline, shard_key_value=None):
        return cls.dbo(shard_key_value=shard_key_value).aggregate(pipeline)

    @classmethod
    def replace_one(cls, spec, docs, shard_key_value=None, **kwargs):
        """Replace a single document matching the filter.

          >>> for doc in db.test.find({}):
          ...     print(doc)
          ...
          {u'x': 1, u'_id': ObjectId('54f4c5befba5220aa4d6dee7')}
          >>> result = db.test.replace_one({'x': 1}, {'y': 1})
          >>> result.matched_count
          1
          >>> result.modified_count
          1
          >>> for doc in db.test.find({}):
          ...     print(doc)
          ...
          {u'y': 1, u'_id': ObjectId('54f4c5befba5220aa4d6dee7')}

        The *upsert* option can be used to insert a new document if a matching
        document does not exist.

          >>> result = db.test.replace_one({'x': 1}, {'x': 1}, True)
          >>> result.matched_count
          0
          >>> result.modified_count
          0
          >>> result.upserted_id
          ObjectId('54f11e5c8891e756a6e1abd4')
          >>> db.test.find_one({'x': 1})
          {u'x': 1, u'_id': ObjectId('54f11e5c8891e756a6e1abd4')}
        """
        if docs is None:
            raise Exception('document is None!')
        if spec is None:
            raise Exception('spec is None!')

        spec = cls.__check_id(spec)
        docs.setdefault("update_at", utils.now())
        result = cls.dbo(sql=spec, shard_key_value=shard_key_value).replace_one(spec, docs, **kwargs)
        return result

    @classmethod
    def update(cls, spec=None, docs=None, check_updated_state=True, shard_key_value=None, **kwargs):
        """
        wrap collection's update
        :param spec: 更新条件
        :param docs: 更新文档
        :param check_updated_state: True 直接返回是否成功更新状态字段值(updatedExisting)
        False 返回完整的更新结果
        :param kwargs:
        """
        if docs is None:
            raise Exception('document is None!')
        if spec is None:
            raise Exception('spec is None!')

        spec = cls.__check_id(spec)

        if not any(k.startswith('$') for k in docs.keys()):
            docs = {"$set": docs}

        docs.setdefault("$set", {})['update_at'] = utils.now()

        multi = kwargs.pop("multi", False)

        try:
            if multi is True:
                result = cls.dbo(sql=spec, shard_key_value=shard_key_value).update_many(spec, docs, **kwargs)
            else:
                result = cls.dbo(sql=spec, shard_key_value=shard_key_value).update_one(spec, docs, **kwargs)
            return result.modified_count if check_updated_state else result.raw_result
        except Exception as e:
            result = cls.dbo(sql=spec, shard_key_value=shard_key_value).update(spec, docs, **kwargs)
            return result.get('nModified') if check_updated_state else result

    @classmethod
    def find_and_modify(cls, spec, docs, shard_key_value=None, **kwargs):
        spec = cls.__check_id(spec)
        docs.setdefault("$set", {})['update_at'] = utils.now()
        kwargs["new"] = kwargs.get("new", True)
        d = cls.dbo(sql=spec, shard_key_value=shard_key_value).find_and_modify(spec,
                                                                               docs,
                                                                               upsert=kwargs.pop("upsert", True),
                                                                               sort=kwargs.pop("sort", None),
                                                                               full_response=kwargs.pop("full_response", False),
                                                                               manipulate=kwargs.pop("manipulate", False), **kwargs)
        return cls._parse_data(cls.__parse_oid(d), **kwargs) if d else {}

    @classmethod
    def find_one_and_replace(cls, spec, docs, shard_key_value=None, **kwargs):
        """
        替换/覆盖/新增
        :param spec:
        :param docs:
        :param shard_key_value:
        :param kwargs:
            指定需要/不需要返回的字段
            projection：{"need_return_field": 1/True, "_id": 0/False}
            没有则新增
            upsert: True/False
            返回更新后的文档
            return_document: True/False
            按该规则排序后，更新第一条数据
            sort: {"a": -1} or [("a", -1)]
        :return:
        """
        spec = cls.__check_id(spec)
        sort = kwargs.get("sort", None)
        if sort and type(sort) == dict:
            kwargs["sort"] = list(sort.items())
        kwargs.setdefault("return_document", True)
        d = cls.dbo(sql=spec, shard_key_value=shard_key_value).find_one_and_replace(spec, docs, **kwargs)
        return cls._parse_data(cls.__parse_oid(d), **kwargs) if d else {}

    @classmethod
    def find_one_and_update(cls, spec, docs, shard_key_value=None, **kwargs):
        """
        原子更新
        :param spec:
        :param docs:
        :param shard_key_value:
        :param kwargs:
            指定需要/不需要返回的字段
            projection：{"need_return_field": 1/True, "_id": 0/False}
            没有则新增
            upsert: True/False
            返回更新后的文档
            return_document: True/False
            按该规则排序后，更新第一条数据
            sort: {"a": -1} or [("a", -1)]
        :return:
        :param spec:
        :param docs:
        :param shard_key_value:
        :param kwargs:
        :return:
        """
        spec = cls.__check_id(spec)
        sort = kwargs.get("sort", None)
        if sort and type(sort) == dict:
            kwargs["sort"] = list(sort.items())
        docs.setdefault("$set", {})['update_at'] = utils.now()
        d = cls.dbo(sql=spec, shard_key_value=shard_key_value).find_one_and_update(spec, docs, **kwargs)
        return cls._parse_data(cls.__parse_oid(d), **kwargs) if d else {}

    @classmethod
    def find_one_and_delete(cls, spec, shard_key_value=None, **kwargs):
        """
        原子删除
        :param spec:
        :param docs:
        :param shard_key_value:
        :param kwargs:
            指定需要/不需要返回的字段
            projection：{"need_return_field": 1/True, "_id": 0/False}
            返回更新后的文档
            return_document: True/False
            按该规则排序后，更新第一条数据
            sort: {"a": -1} or [("a", -1)]
        :return:
        :param spec:
        :param docs:
        :param shard_key_value:
        :param kwargs:
        :return:
        """
        spec = cls.__check_id(spec)
        sort = kwargs.get("sort", None)
        if sort and type(sort) == dict:
            kwargs["sort"] = list(sort.items())
        d = cls.dbo(sql=spec, shard_key_value=shard_key_value).find_one_and_delete(spec, **kwargs)
        return cls._parse_data(cls.__parse_oid(d), **kwargs) if d else {}

    @classmethod
    def find_list_by_page(cls, spec, page, count=10, sort={"create_at": -1}, fields=False, shard_key_value=None, **kwargs):
        """
        按照count分页，返回当前页数据和总页数
        :param spec:
        :param count:
        :param sort: must be obj like [("a", -1), ...]
        :return:
        """
        cursor = cls.__find(spec, fields=fields, is_cursor=True, shard_key_value=shard_key_value)
        data_list = [cls._parse_data(cls.__parse_oid(d), **kwargs) for d in list(cls.__meta_cursor(cursor, page, count, sort)) if d]
        total_page = cls.__get_total_page(cursor, count)
        return data_list, total_page, cursor.count()

    @classmethod
    def find_list_by_last_id(cls, spec, count=10, sort={"create_at": -1}, fields=False, last_id_field=False, shard_key_value=None, **kwargs):
        """
        list by last_id
        :param spec:
        :param count:
        :param sort: must be obj like [("a", -1), ...]
        :return:
        """
        cursor = cls.__find(spec, fields=fields, is_cursor=True, shard_key_value=shard_key_value)
        data_list = [cls._parse_data(cls.__parse_oid(d), **kwargs) for d in list(cls.__meta_cursor(cursor, count=count, sort=sort)) if d]
        last_id_field = last_id_field if last_id_field else "create_at"
        last_id = data_list[-1][last_id_field] - 1 if data_list else -1
        return data_list, last_id

    @classmethod
    def get_batch_data(cls, *vals, **kwargs):
        """
        批量获取一批数据
        :param k:
        :param vals:
        :return:
        """
        key = kwargs.pop("key", "_id")
        data_mp = {}
        skip_field_list = kwargs.get("skip_field_list", [])

        shard_key_value = kwargs.get("shard_key_value", None)
        fields = kwargs.get("fields", None)
        page = kwargs.get("page", 0)
        count = kwargs.get("count", 0)
        sort = kwargs.get("sort", {"create_at": -1})

        if vals:
            cursor = cls.__find({key: {"$in": vals}}, fields=fields, is_cursor=True, shard_key_value=shard_key_value)
            data = [cls.__parse_oid(d) for d in list(cls.__meta_cursor(cursor, 0, 0, sort)) if d]
        else:
            data = []

        for d in data:
            tmp = {}
            if skip_field_list:
                for k, v in d.items():
                    if k in skip_field_list:
                        continue
                    tmp[k] = v
            else:
                tmp = d
            data_mp[d[key]] = tmp

        return {k: cls._parse_data(v, **kwargs) for k, v in data_mp.items()}

    @classmethod
    def next_seq_id(cls, seq_name="seq_id", val=0, random_step=10):
        """Generate next value
        :param val: step value
        :return: :rtype:
        """
        if not val:
            val = random.randrange(1, random_step)

        result = cls.mongo.sequence.find_and_modify({'seq_name': seq_name}, {'$inc': {'val': val}}, True, new=True)

        if result:
            return result['val']
        return None

    @classmethod
    def __find(cls, spec=None, fields=False, limit=False, skip=False, sort=False, is_cursor=False, shard_key_value=None, **kwargs):
        """
        fields: {"uid": 1}
        limit: 10
        skip: 10
        sort: {"uid": -1}
        :param spec:
        :param cursor:  True 返回游标，否则返回list
        :return:
        """
        spec = cls.__check_id(spec)
        spec = spec or {}
        if type(sort) == dict:
            sort = list(sort.items())
        if fields and isinstance(fields, dict):
            cursor = cls.dbo(sql=spec, shard_key_value=shard_key_value).find(spec, fields)
        else:
            cursor = cls.dbo(sql=spec, shard_key_value=shard_key_value).find(spec)

        if limit is not False:
            cursor = cursor.limit(int(limit))
        if skip is not False:
            cursor = cursor.skip(int(skip))
        if sort is not False:
            cursor = cursor.sort(sort)

        if is_cursor:
            return cursor
        else:
            return list(cursor)

    @classmethod
    def _parse_data(cls, d, **kwargs):
        """
        you can rewrite this，in model
        :return:
        :rtype:
        """
        name = cls.__name__.lower().rstrip("model")
        id_name = "%s_id" % name
        if "_id" in d and id_name not in d:
            d[id_name] = str(d["_id"]) if utils.ObjectId.is_valid(d["_id"]) else d["_id"]
        return d

    @classmethod
    def __meta_cursor(cls, cursor, page=None, count=10, sort=dict()):
        sort = list(sort.items()) if type(sort) == dict else list(sort) if sort else False

        if page:
            skip = (int(page) - 1) * int(count)
            cursor.skip(skip)

        if count:
            cursor = cursor.limit(int(count))

        if sort:
            cursor = cursor.sort(sort)

        return cursor

    @classmethod
    def __get_total_page(cls, cursor, count=10):
        if not count:
            return 1
        c = cursor.count() // count
        s = cursor.count() % count
        return c + 1 if s else c

    @classmethod
    def __parse_oid(cls, d):
        if not isinstance(d, dict):
            return d

        if not d:
            d = {}
        if d and isinstance(d.get("_id"), ObjectId):
            d["_id"] = str(d["_id"])

        d = cls.__parse_date(d)
        return d

    @classmethod
    def __check_id(cls, spec):
        if not spec:
            return spec

        for k, v in spec.items():
            if k == "_id":
                if isinstance(v, dict):
                    v1 = list(v.keys())
                    if v1[0] in ["$in", "$nin"]:
                        sin = v1[0]
                        v[sin] = list(map(utils.to_ObjectId, spec[k][sin]))
                    else:
                        continue

                    spec[k] = v
                elif isinstance(v, list):
                    spec[k] = list(map(utils.to_ObjectId, spec[k]))
                else:
                    spec[k] = utils.to_ObjectId(v)
        return spec



    @classmethod
    def __parse_date(cls, d):
        if not d:
            return d

        try:
            for k in ["create_at", "update_at", "start_at", "end_at"]:
                prefix, _ = k.split("_")
                if k in d:
                    if isinstance(d[k], str) and d[k].isdigit():
                        d[k] = int(d[k])
                    d["%s_date" % prefix] = utils.timestamp2str(d[k], "%Y-%m-%d %H:%M:%S")
        except:
            pass
        return d