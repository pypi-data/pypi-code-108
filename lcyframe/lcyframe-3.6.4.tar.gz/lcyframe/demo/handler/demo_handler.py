#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lcyframe import route
from lcyframe import funts
from base import BaseHandler

@route("/demo")
class DemoHandler(BaseHandler):
    """
    演示
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
        

    @funts.params()
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
        # redis
        # self.redis.set("a", 1)
        # self.redis.get("a")

        # ssdb
        # self.ssdb.set("a", 1)
        # self.ssdb.get("a")

        # mq调用方法
        # self.mq.put({"event": "event1", "a": 1})

        # nsq调用方法
        # self.nsq.pub("test", '{"event": "on_create_user", "uid": 0}')
        # from producer.nsq import user
        # user.PublishUser().on_create_user({"uid": 0})
        # self.nsq.NsqEvent.on_create_user({"uid": 0})

        # mqtt调用方法,2种方法不可同时使用，否则会抢占链接
        # from producer.mqtt import user
        # user.MqttEvent().on_create_user({"a": "mqtt_test"})
        # self.mqtt.MqttEvent.on_create_user({"a": "mqtt_test"})

        # celery
        # self.celery.Events.save_image.delay(111)
        # self.celery.Events.UserEvent.register.delay(111)

        # beanstalk
        # self.beanstalk.ClassName.func({"DemoEvents": 1}, priority=65536, delay=0, ttr=60, tube="tube_name")
        # self.beanstalk.DefaultEvents.event({"DefaultEvents": 1})  # tube1
        # self.beanstalk.DemoEvents.event({"DemoEvents": 1})        # tube2

        # 上传文件 self.request.files = {'excel': [{'filename': 'xxxxxxx.xlsx', 'body':"xxxxxx"}]
        # excel = self.params["excel"]    # {'filename': 'xxxxxxx.xlsx', 'body':"xxxxxx"}

        # graylog
        # self.graylog.from_server(x="sdsdds")
        # 调用model，创建一条用户数据

        # self.model.DemoModel.create_demo()

        data = {"a": "山东省地方"}
        self.write_success(data)






