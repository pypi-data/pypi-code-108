# coding=utf-8
import os
import logging
import json
import time
from lcyframe.libs import utils

class BsRoute(object):
    """消息队列路由"""
    _workers = {}

    def __init__(self, event=None):
        self.event = event

    def __call__(self, _handler):
        event = self.event and self.event or _handler.__name__
        self._workers[event] = _handler
        return _handler

    @classmethod
    def tasks(cls, _handler):
        class_name = _handler.__name__
        if class_name in cls._workers:
            raise Exception("The event is exists multiple: `%s`" % class_name)

        cls._workers[class_name] = _handler
        return cls._workers

    @classmethod
    def get_workers(cls, ROOT, workers_path):

        if not isinstance(workers_path, list):
            workers_path = [workers_path]

        if workers_path is None:
            raise Exception("args workers_path is not allow empty")

        if not cls._workers:
            for work in workers_path:
                for root, dirs, files in os.walk(utils.fix_path(os.path.join(ROOT, work))):
                    for file in files:
                        if file.startswith("__"):
                            continue
                        if file.endswith(".pyc"):
                            continue
                        if not file.endswith(".py"):
                            continue
                        model_name = root.replace(ROOT, "").lstrip("/").replace("/", ".") + "." + file.rstrip(".py")
                        __import__(model_name, globals(), locals(), [model_name], 0)
                        logging.debug("register beanstalk workers [%s.py] success!" % model_name)

        return cls._workers

class Events(object):

    def __getattr__(self, event):
        event = "%s.%s" % (self.classname, event)
        if event not in self.__dict__:
            self.__dict__[event] = Agent(self.beanstalk, event, self.tube)

        return self.__dict__[event]


class Agent:

    def __init__(self, beanstalk, event, tube):
        self.beanstalk = beanstalk
        self.event = event
        self.tube = tube

    def __repr__(self):
        return "event '%s'" % self.event

    def __call__(self, body, priority=65536, delay=0, ttr=60):
        payload = {}
        payload["__event__"] = self.event  # message_handler name by Consumer
        payload["ts"] = int(time.time())
        payload.update(body)

        self.beanstalk.put(json.dumps(payload), priority=priority, delay=delay, ttr=ttr, tube=self.tube)

