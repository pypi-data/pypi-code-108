# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/11 8:06 下午
# Copyright (C) 2021 The lesscode Team
import os
import sys
import logging
import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.log import LogFormatter as TornadoLogFormatter  # 避免命名歧义，设置了别名
from tornado.options import options, define
from typing import Optional

from lesscode.db.init_connection_pool import InitConnectionPool
from lesscode.web.router_mapping import RouterMapping

# project_name = project_path.split(os.path.sep)[-1]
#
# static_path = os.path.join(project_path, "static")
# template_path = os.path.join(project_path, "templates")
# temp_path = os.path.join(project_path, "temp")
# sql_path = os.path.join(project_path, "sqls")
# convert_path = os.path.join(project_path, "converters")
# dataset_path = os.path.join(project_path, "dataset")

define("application_name", default=f"{os.path.split(os.path.dirname(sys.argv[0]))[-1]}", type=str, help="配置文件")
define("application_path", default=f"{os.path.dirname(sys.argv[0])}", type=str, help="应用运行根路径")
# 生成秘钥方式 print(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes).decode())
define("cookie_secret", default="hRHQlJoUQIiNai2MLV9fQV3YDpxWrUHQp/jnfF9riQk=", type=str, help="cookie 秘钥 ")
define("static_path", default=os.path.join(f"{os.path.dirname(sys.argv[0])}", "static"), type=str, help="静态资源目录")

define("profile", default="profiles.config", type=str, help="配置文件")
define("port", default="8080", type=int, help="服务监听端口")
define("handler_path", default="handlers", type=str, help="处理器文件存储路径")

# 日志初始化配置，配置文件中可修改设置
options.logging = "DEBUG"
options.log_rotate_mode = "time"
options.log_file_prefix = "log"
options.log_rotate_when = "D"
# options.log_rotate_interval,
options.log_file_num_backups = 30


class LogFormatter(TornadoLogFormatter):
    """
    LogFormatter 类用于日志统一格式化处理
    """

    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d]%(end_color)s [%(message)s]',
            datefmt='%Y-%m-%d %H:%M:%S')


# 应用实例
def init_log():
    """
    初始化日志配置，创建控制台日志输出处理类，统一设置格式
    :return:
    """
    console_log = logging.StreamHandler()  # 创建控制台日志输出处理类
    console_log.setLevel(options.logging)  # 设置日志级别
    logging.getLogger().handlers.append(console_log)
    # 为日志处理类指定统一的日志输出格式
    [handler.setFormatter(LogFormatter()) for handler in logging.getLogger().handlers]


def load_profile():
    """
    初始化配置文件，配置文件可通过命令行参数指定 --profile=dev
    :return:
    """
    command_profile_flag = False  # 标识配置文件是否通过命令行参数指定
    # 获取命令行参数，此处仅获取profile配置信息
    profile = [item for item in sys.argv if item.__contains__("--profile=")]
    if profile:  # 如果有指定配置文件，更新参数，如果指定多次，取最后一次
        options.profile = f"profiles.config_{profile[-1].replace('--profile=', '')}"
        command_profile_flag = True
    # 第一次加载配置文件
    try:
        __import__(options.profile)
        # command_profile_flag  是False 表示加载的是默认配置文件，还需要再一次判断默认文件中是否指定了其他配置文件，此判断仅针对默认配置文件，其他配置文件不在进行判断。
        if not command_profile_flag and options.profile != "profiles.config":
            __import__(f"profiles.config_{options.profile}")
    except ModuleNotFoundError:
        # 如果加载失败直接跳过，继续执行，给予WARNING。
        logging.warning(f"配置文件不存在：{options.profile}")


class WebServer:
    """
    Wbe服务对象
    """

    def __init__(self):
        load_profile()  # 1、优先处理加载配置文件，要在命令行解析参数前
        tornado.options.parse_command_line()  # 2、调用tornado的命令行参数解析
        init_log()  # 3、初始化日志配置，要在命令行解析参数后，确保日志参数都已经设置完成。
        # 4、启动时创建数据库连接池
        tornado.ioloop.IOLoop.current().run_sync(InitConnectionPool.create_pool)
        # 5、自动化注册Handler处理类，
        self.autoRegisterHandler(f"{os.path.abspath(os.path.dirname(sys.argv[0]))}/{options.handler_path}", options.handler_path)
        self.app = tornado.web.Application(
            RouterMapping.instance(),
            cookie_secret=options.cookie_secret,
            static_path=options.static_path,
            debug=True if options.logging == "DEBUG" else False  # 依据日志记录级别确认是否开启调试模式
        )
        self.server = tornado.httpserver.HTTPServer(self.app, max_buffer_size=500 * 1024 * 1024)  # 500M

    def start(self, num_processes: Optional[int] = 1, max_restarts: int = None):
        self.server.listen(options.port)
        self.server.start(num_processes, max_restarts)
        logging.info(f"start server : {options.application_name}")
        logging.info(f"start server port : {options.port}")
        try:
            tornado.ioloop.IOLoop.current().start()
        except KeyboardInterrupt:
            pass
        finally:
            # 关掉连接池
            for item in options.database.items():
                tornado.ioloop.IOLoop.current().run_sync(item[1][0].close)
        return self

    def autoRegisterHandler(self, path, pkg_name):
        """
        动态注册Handler模块
        遍历项目指定包内的Handler，将包内module引入。
        :param path: 项目内Handler的文件路径
        :param pkg_name: 引入模块前缀
        """
        # 首先获取当前目录所有文件及文件夹
        dynamic_handler_names = os.listdir(path)
        for handler_name in dynamic_handler_names:
            # 利用os.path.join()方法获取完整路径
            full_file = os.path.join(path, handler_name)
            # 循环判断每个元素是文件夹还是文件
            if os.path.isdir(full_file):
                # 文件夹递归遍历
                self.autoRegisterHandler(os.path.join(path, handler_name), ".".join([pkg_name, handler_name]))
            elif os.path.isfile(full_file) and handler_name.endswith("handler.py"):
                # 文件，并且为handler结尾，认为是请求处理器，完成动态装载
                __import__("{}.{}".format(pkg_name, handler_name.replace(".py", "")))
