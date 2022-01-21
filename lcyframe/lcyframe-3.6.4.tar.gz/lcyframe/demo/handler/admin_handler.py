#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lcyframe import route
from lcyframe import funts
from base import BaseHandler

@route("/admin/member")
class AdminHandler(BaseHandler):
    """
    后台管理员
    """

    
    @funts.admin
    @funts.params()
    def put(self):
        """无说明
        None
        
        Request extra query params:
        - uid # None type: int
        - nick_name # None type: str
        - sex # 1 无说明 0 无说明 type: int
        - mobile # 无说明 type: str
        - email # 无说明 type: str
        - gid # 无说明 1 无说明 2 无说明 type: int
        

        :return:
        :rtype:
        """
        
        pass
        

    
    @funts.admin
    @funts.params()
    def post(self):
        """无说明
        None
        
        Request extra query params:
        - user_name # None type: str
        - pass_word # 无说明，无说明 type: str
        - nick_name # None type: str
        - sex # 1 无说明 0 无说明 type: int
        - mobile # 无说明 type: str
        - email # 无说明 type: str
        - gid # 无说明 1 无说明 2 无说明 type: int
        

        :return:
        :rtype:
        """
        
        pass
        

    
    @funts.admin
    @funts.params()
    def get(self):
        """无说明
        None
        
        Request extra query params:
        - uid # uid type: int
        

        :return:
        :rtype:
        """
        
            
        data = self.model.AdminModel.get_admin(self.params.get("_id", ""))
        self.write_success(data=data)
            
        

    
    @funts.admin
    @funts.params()
    def delete(self):
        """无说明
        None
        
        Request extra query params:
        - uid # uid type: int
        

        :return:
        :rtype:
        """
        
        self.model.AdminModel.delete(self.params["_id"])
        self.write_success()
        


@route("/admin/states")
class AdminStatesHandler(BaseHandler):
    """
    无说明/无说明
    """

    
    @funts.admin
    @funts.params()
    def post(self):
        """无说明/无说明
        None
        
        Request extra query params:
        - uid # uid type: int
        - state # 1 无说明 -1 无说明 type: int
        

        :return:
        :rtype:
        """
        
        pass
        


@route("/admin/login")
class AdminLoginHandler(BaseHandler):
    """
    无说明
    """

    
    @funts.admin
    @funts.params()
    def post(self):
        """无说明
        None
        
        Request extra query params:
        - user_name # 无说明 type: str
        - pass_word # 无说明 type: str
        

        :return:
        :rtype:
        """
        
        pass
        


@route("/admin/find")
class AdminFindHandler(BaseHandler):
    """
    无说明
    """

    
    @funts.admin
    @funts.params()
    def post(self):
        """无说明
        无说明（无说明）
        
        Request extra query params:
        - page # 无说明 type: str
        

        :return:
        :rtype:
        """
        
        pass
        

    
    @funts.admin
    @funts.params()
    def get(self):
        """无说明
        无说明
        

        :return:
        :rtype:
        """
        
            
        data = self.model.AdminModel.get_admin(self.params.get("_id", ""))
        self.write_success(data=data)
            
        


@route("/admin/resetpwd")
class ResetpwdHandler(BaseHandler):
    """
    无说明
    """

    
    @funts.admin
    @funts.params()
    def post(self):
        """无说明
        None
        
        Request extra query params:
        - pass_word # 无说明 type: str
        - new_pass_word # 无说明 type: str
        

        :return:
        :rtype:
        """
        
        pass
        

