#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright lcyframe 123220663@qq.com
from lcyframe import route
from lcyframe import funts
from lcyframe import BaseHandler, BaseModel as Model


@route("/user")
class UserHandler(BaseHandler):
    """
    用户
    """

    @funts.params()
    def post(self):
        """添加
        测试post
        
        Request extra query params:
        - a # 角色id type: integer
        - b # 供应商id type: string
        - c # 手机号 type: string
        - d # 城市全拼列表 type: int
        - pic # 文件 type: file
        

        :return:
        :rtype:
        """

        self.write_success()

    def get(self):
        """查看
        测试get
        
        Request extra query params:
        - a # 角色id type: integer
        - b # 供应商id type: string
        - d # 城市全拼列表 type: int
        

        :return:
        :rtype:
        """
        pass


@route("/user_list")
class UserlistHandler(BaseHandler):
    """
    用户列表
    """

    def post(self):
        """添加
        测试post
        
        Request extra query params:
        - a # 角色id type: integer
        - b # 供应商id type: string
        - c # 手机号 type: string
        - d # 城市全拼列表 type: int
        - pic # 文件 type: file
        

        :return:
        :rtype:
        """
        pass

    def get(self):
        """查看
        测试get
        
        Request extra query params:
        - a # 角色id type: integer
        - b # 供应商id type: string
        - d # 城市全拼列表 type: int
        

        :return:
        :rtype:
        """
        pass

