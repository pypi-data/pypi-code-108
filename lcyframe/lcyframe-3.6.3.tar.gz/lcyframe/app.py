#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import os
import signal
import platform
import asyncio
import tornado
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import options
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import Task
from .libs import Copyright
from .libs import yaml2py, utils
from .libs.route import route
try:
    from .libs.docs.generate_docs import GenerateDocs
except:pass
from .libs.services import ServicesFindet
from .base import BaseHandler, BaseModel
from .handler.docshandler import DocsHandler


class App(tornado.web.Application):
    def __init__(self, port=None, **kwargs):
        """
        A Tornado web frame .
        :param args:
        :param kwargs:
                    debug: default True
                    template_path:
                    static_path:
                    cookie_secret:
                    handler_dir: the handler of web api
                    max_buffer_size:
                    logging_level: debug
                    parse_command_line: view the logging of request. default True
                    db: mongo_db obj
                    redis: redis obj
                    ssdb: ssdb obj
                    solr:
                    task: List. PeriodicCallback handler obj [(obj, callback_time), ...]
        """
        kwargs["ROOT"] = utils.fix_path(kwargs["ROOT"])
        os.environ.app_config = kwargs
        self.kwargs = kwargs
        self.ROOT = utils.fix_path(kwargs["ROOT"])
        self.kwargs["Copyright"] = Copyright
        self.uri = kwargs.get("host") or kwargs["wsgi"].get("host", "127.0.0.1")
        self.port = port or kwargs["wsgi"].get("port", kwargs.get("port", 6678))
        self.debug = kwargs["wsgi"].get("debug", True)
        self.max_buffer_size = int(kwargs["wsgi"].get("max_buffer_size", 10 * 1024 * 1024 * 1024))

        self.template_path = self.get_path(kwargs.get("template_path", "template"))
        self.static_path = self.get_path(kwargs.get("static_path", "static"))
        self.handler_dir = self.get_path(kwargs.get("handler_dir", "handler"))
        self.model_dir = self.get_path(kwargs.get("model_dir", "model"))
        self.api_schema_dir = self.get_path(kwargs.get("api_schema_dir", "api_schema"))
        self.errors_dir = self.get_path(kwargs.get("errors_dir", "utils"))
        self.constant_dir = self.get_path(kwargs.get("constant_dir", "utils"))
        self.api_docs = kwargs.get("api_docs", {})
        self.docs_dir = self.get_path(self.api_docs.get("docs_dir", "docs"))
        self.jinja2_path_dir = kwargs.get("jinja2_dir", "jinja2")

        self.cookie_secret = kwargs.get("cookie_secret", "f465ca164f0e")
        self.settings = dict(debug=self.debug,
                             template_path=self.template_path,
                             static_path=self.static_path,
                             cookie_secret=self.cookie_secret)

        self.log_config = self.kwargs.get("logging_config", {})
        self.init_log()
        self.load_api_schema()
        self.create_base()
        self.create_handler()
        self.create_model()
        self.impmodule()
        self.handlers = route.get_routes(self.ROOT, self.handler_dir)
        # self.handlers.append((r'/docs', DocsHandler))
        self.handlers.append(tornado.web.url(r'/docs', DocsHandler, name=DocsHandler.__name__))
        self.handlers.append(tornado.web.url(r'/.*', BaseHandler, name=BaseHandler.__name__))
        if not self.handlers:
            raise Exception("no api handler has been register.")

        self.task = kwargs.get("task", [])  # you must give the obj list like this: [(func, 1000)]

        tornado.web.Application.__init__(self, self.handlers, **self.settings)

    def check_path(self, path):
        if not os.path.exists(path):
            raise IOError("[Errno 2] No such file or directory: %s" % path)
        else:
            return True

    def get_path(self, name):
        """

        :param p:
        :return:
        """
        return utils.fix_path(os.path.join(self.ROOT, name.lstrip("/")))

    def load_api_schema(self):
        """
        read schema from .yml
        :return:
        """
        assert self.check_path(self.api_schema_dir)
        self.api_schema_mp = yaml2py.load_api_schema(self.api_schema_dir)

    def create_base(self):
        s = utils.fix_path(os.path.join(self.ROOT, "base.py"))
        if not os.path.exists(s) and self.kwargs.get("auto_generate_base", True):
            yaml2py.generate_basepy(self.ROOT + "/base.py", self.jinja2_path_dir)

    def create_handler(self):
        """
        create xxx_handler.py
        :return:
        """
        if not self.kwargs.get("auto_generate_py", True):
            return

        handler_init = utils.fix_path(os.path.join(self.handler_dir, "__init__.py"))
        if not os.path.exists(self.handler_dir) or not os.path.exists(handler_init):
            if not os.path.exists(self.handler_dir):
                os.mkdir(self.handler_dir)

        yaml2py.generate_resource_handler(self.handler_dir, self.model_dir, self.api_schema_mp, self.jinja2_path_dir)

    def create_model(self):
        """
        create mode of model
        :return:
        """
        if not self.kwargs.get("auto_generate_py", True):
            return

        self.model_schema_dir = self.model_dir + "/schema"
        model_init = utils.fix_path(os.path.join(self.model_dir, "__init__.py"))

        if not os.path.exists(self.model_dir) or not os.path.exists(model_init):
            if not os.path.exists(self.model_dir):
                os.mkdir(self.model_dir)

            if not os.path.exists(model_init):
                with open(os.path.join(model_init), "w", encoding='utf-8') as p:
                    p.write(Copyright.file_pre)

            schema_init = utils.fix_path(os.path.join(self.model_schema_dir, "__init__.py"))
            if not os.path.exists(self.model_schema_dir):
                os.mkdir(self.model_schema_dir)

            if not os.path.exists(schema_init):
                with open(schema_init, "w", encoding='utf-8') as p:
                    p.write(Copyright.file_pre)

        yaml2py.generate_resource_model(self.model_dir, self.api_schema_mp, self.jinja2_path_dir)

        schema_init = utils.fix_path(os.path.join(self.model_schema_dir, "__init__.py"))
        if not os.path.exists(schema_init):
            with open(schema_init, "w", encoding='utf-8') as p:
                p.write(Copyright.file_pre)

        yaml2py.generate_resource_model_schema(self.model_schema_dir, self.api_schema_mp, self.jinja2_path_dir)

    def impmodule(self, model_dir=None):
        model_dir = model_dir or self.model_dir
        return yaml2py.impmodule(BaseModel, model_dir)

    def init_setattr(self):
        ServicesFindet(BaseHandler, BaseModel)(self.kwargs)
        setattr(BaseModel, "uri", self.uri)
        setattr(self, "app_config", self.kwargs)
        setattr(BaseHandler, "api_schema", self.api_schema_dir)
        setattr(BaseHandler, "app_config", self.kwargs)
        setattr(BaseModel, "api_schema", self.api_schema_dir)
        setattr(BaseModel, "app_config", self.kwargs)
        setattr(BaseHandler, "request_url", self.request_url)
        setattr(BaseModel, "request_url", self.request_url)

    def init_log(self):
        """
        ###############################################
        # 日志模块配置
        # 使用循环日志文件保存
        # ref: tornado.log.define_logging_options
        ###############################################
        open: true  # 是否开启日志
        # warn 控制台只打印异常请求记录堆栈，debug 打印所有请求记录
        level: warn
        #日志保存地址, 非必填，留空则不保存到文件
        file: "logs/"
        #日志文件名字,不提供时，采用端口号作为名称。port.log
        name: app.log         # 默认格式.log
        #循环日志的个数，app.log,app.log1,app.log2
        nums: 10
        #日志文件的大小，500M
        size: 524288000 # 0.5 * 1024 * 1024
        stderr: True
        :return:
        """
        if self.log_config.get("save"):
            tornado.options.options.log_file_max_size = self.log_config.get("size", 524288000)
            tornado.options.options.log_file_num_backups = self.log_config.get("nums", 10)
            file = self.log_config.get("file")
            if not os.path.abspath(file):
                raise Exception("log path must is abdpath.")

            if not os.path.exists(file):
                os.makedirs(file)

            path = "%s/%s" % (file, self.log_config.get("name", str(self.kwargs["wsgi"]["port"])))
            tornado.options.options.log_file_prefix = path

        tornado.options.options.logging = self.log_config.get('level', "debug")
        tornado.options.parse_command_line()

    def periodic_callback(self):
        for obj, t in self.task:
            PeriodicCallback(obj, t).start()

    def request_url(self, url):
        http_client = AsyncHTTPClient()
        response = yield Task(http_client.fetch, url)
        if response.error:
            raise Exception(response.error)
        return response

    def start(self):
        self.init_setattr()
        tornado.options.define(name="app_config", default=self.kwargs, help='App server config', type=str)
        http_server = tornado.httpserver.HTTPServer(self, max_buffer_size=self.max_buffer_size, xheaders=True)
        http_server.bind(self.port)
        logging.warning("Server Config file: " + self.kwargs["config_name"])
        logging.warning("Server ROOT path: " + self.ROOT)
        logging.warning('Server Running on http://%s:%s' % (self.uri, self.port))
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        http_server.start()
        ioloop = IOLoop.instance()
        self.periodic_callback()
        try:
            GenerateDocs.start(self)
        except Exception as e:
            logging.error(str(e))
        def signal_handler(sig, frame):
            ioloop.add_callback(shutdown)
        def shutdown():
            logging.warning('Stopping http server')
            http_server.stop()
            ioloop.add_callback(ioloop.stop)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        ioloop.start()
