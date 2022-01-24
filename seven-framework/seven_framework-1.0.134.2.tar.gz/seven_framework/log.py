# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 21:32:43
:LastEditTime: 2021-07-22 10:32:07
:LastEditors: ChenXiaolei
:Description: 日志帮助类
"""

import logging
import logging.handlers
import time
import os
import json
import socket
import platform
import re

from seven_framework.mysql import *
from seven_framework.json import *


class Logger:
    """
    指定保存日志的文件路径，日志级别，以及调用文件 将日志存入到指定的文件中
    级别优先级:NOTSET < DEBUG < INFO < WARNING < ERROR < CRITICAL
    """

    def __init__(self,
                 log_file_name,
                 log_level,
                 logger,
                 host_ip="",
                 project_name=None,
                 log_config=None):
        """
        :Description:
        :param log_file_name: 日志存储文件路径
        :param log_level: 日志等级
        :param logger: 日志标识
        :param host_ip: 服务器IP
        :param project_name: 项目标志
        :last_editors: ChenXiaolei
        """
        if not project_name:
            if platform.system() == "Windows":
                project_name = os.getcwd().split('\\')[-1]
            else:
                project_name = os.getcwd().split('/')[-1]

        # 判断文件夹是否存在，不存在则创建
        path_list = log_file_name.split("/")
        path_log = log_file_name[0:log_file_name.find(path_list[len(path_list)
                                                                - 1])]
        if not os.path.isdir(path_log):
            os.mkdir(path_log)

        logging_level = ''

        if log_level.upper() == 'NOTSET':
            logging_level = logging.NOTSET
        elif log_level.upper() == 'DEBUG':
            logging_level = logging.DEBUG
        elif log_level.upper() == 'INFO':
            logging_level = logging.INFO
        elif log_level.upper() == 'WARNING':
            logging_level = logging.WARNING
        elif log_level.upper() == 'ERROR':
            logging_level = logging.ERROR
        elif log_level.upper() == 'CRITICAL':
            logging_level = logging.CRITICAL
        elif log_level.upper() == 'SQL':
            logging_level = logging.INFO
        elif log_level.upper() == 'HTTP':
            logging_level = logging.INFO

        storage = None
        if log_config and "storage" in log_config:
            storage = log_config["storage"]

        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging_level)
        # 关闭原始日志在控制台显示(表面日志多次打印)
        self.logger.propagate = False

        # 创建handler，用于写入日志文件
        # 默认日志文件保存30个文件
        backup_count = 30
        # 日志文件备份时间统一设置
        if log_config and "log_file_backup_count" in log_config and log_config["log_file_backup_count"]:
            try:
                backup_count = int(log_config["log_file_backup_count"])
            except:
                print(f"日志模块读取配置中log_file_backup_count值异常")
        # 日志文件备份时间按照level设置(优先)
        if log_config and f"log_file_backup_count_{log_level.lower()}" in log_config and log_config[f"log_file_backup_count_{log_level.lower()}"]:
            try:
                backup_count = int(
                    log_config[f"log_file_backup_count_{log_level.lower()}"])
            except:
                print(f"日志模块读取配置中log_file_backup_count_{log_level.lower()}值异常")

        self.handler_file = LoggerFileHandler(
            log_file_name, 'D', 1, backupCount=backup_count,  encoding="utf-8")
        # 设置 切分后日志文件名的时间格式 默认 log_file_name+"." + suffix 如果需要更改需要改logging 源码
        self.handler_file.suffix = "%Y%m%d.log"
        self.handler_file.extMatch = re.compile(r"^\d{4}\d{2}\d{2}.log$")
        self.handler_file.setLevel(logging_level)

        formatter = logging.Formatter(
            JsonHelper.json_dumps({
                "record_time": "%(asctime)s",
                "level": "%(levelname)s",
                "log_msg": "%(message)s",
                "host_ip": host_ip,
                "project_name": project_name
            }))
        self.handler_file.setFormatter(formatter)

        # 创建handler，用于输出至控制台
        # 定义控制台输出handler的输出格式
        formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s]%(message)s')
        self.handler_console = logging.StreamHandler()  # 输出到控制台的handler
        self.handler_console.setFormatter(formatter)

        # 给logger添加handler
        if not self.logger.handlers:
            # 默认开启文本日志
            if log_config and "log_file_" + log_level.lower(
            ) in log_config and log_config["log_file_" +
                                           log_level.lower()] == False:
                pass
            else:
                self.logger.addHandler(self.handler_file)
            # 默认开启控制台日志
            if not log_config or "log_console" not in log_config or log_config["log_console"]!=False:
                self.logger.addHandler(self.handler_console)

        # 日志存储
        if storage and type(storage) == dict:
            if "level_setting" in storage:
                for level_item in storage["level_setting"]:
                    if "level" in level_item and "storage" in level_item and log_level.lower() == level_item["level"].lower() and level_item["storage"] != False:
                        self.handler_storage = LoggerStorageHandler(
                            log_level, storage, project_name, host_ip)
                        self.logger.addHandler(self.handler_storage)

    def close(self):
        if hasattr(self, "handler_file"):
            self.logger.removeHandler(self.handler_file)
            self.handler_file.close()
        if hasattr(self, "handler_console"):
            self.logger.removeHandler(self.handler_console)
            self.handler_console.close()
        if hasattr(self, "handler_storage"):
            self.logger.removeHandler(self.handler_storage)
            self.handler_storage.close()

    def get_logger(self):
        return self.logger

    @classmethod
    def get_logger_by_name(self, loger_name):
        """
        :Description: 通过日志标识获取logger
        :param loger_name: 日志标识
        :return: logger
        :last_editors: ChenXiaolei
        """
        return logging.getLogger(loger_name)


class LoggerFileHandler(logging.handlers.TimedRotatingFileHandler):

    def emit(self, record):
        """
        :description: 重写文件日志记录方法
        :param record: 日志信息
        :return 无
        :last_editors: ChenXiaolei
        """
        try:
            log_info = {}
            if hasattr(record, "extra") and record.extra:
                for key in record.extra.keys():
                    log_info[key] = record.extra[key]

            format_dict = self.__merge_dict(
                log_info, json.loads(self.formatter._fmt))

            formatter = logging.Formatter(
                JsonHelper.json_dumps(format_dict))
            self.setFormatter(formatter)
        except:
            print("日志emit文件日志时异常时异常:" + traceback.format_exc())
            pass
        # 写入文件日志
        try:
            if self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        except Exception:
            self.handleError(record)

    @classmethod
    def __merge_dict(self, *args):
        """
        :description: 合并多个字典 merge_dict(dict1,dict2,dict3)
        :param args:不限个数的字典   
        :return 合并后的字典
        :last_editors: ChenXiaolei
        """
        result_dict = {}
        for dict_item in args:
            if type(dict_item) != dict:
                continue
            result_dict.update(dict_item)
        return result_dict


class LoggerStorageHandler(logging.Handler):
    def __init__(self, level, storage, project_name="", host_ip=""):
        if "engine" not in storage and "config" not in storage:
            raise "未配置log存储介质"

        self.project_name = project_name
        self.host_ip = host_ip

        self.storage_engine = storage["engine"]

        if self.storage_engine.lower() == "mysql":
            try:
                from seven_framework.mysql import MySQLHelper
                self.mysql_db = MySQLHelper(storage["config"])
                self.mysql_db._log_sql = None

                # 获取表名
                self.table_name = "python_log_tb"

                if "level_setting" in storage:
                    for level_item in storage["level_setting"]:
                        if level_item["level"].lower() == level.lower():
                            self.table_name = level_item["key"]

                # 判断制定数据库中标是否存在
                exist_result = self.mysql_db.fetch_one_row(
                    f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{storage['config']['db']}' AND TABLE_NAME='{self.table_name}';"
                )

                if not exist_result:
                    if level.lower() == "http":
                        self.mysql_db.fetch_and_commit(
                            f"CREATE TABLE `{self.table_name}` ( `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键id', `request_code` varchar(50) DEFAULT NULL COMMENT '请求标识', `action_mode` varchar(10) DEFAULT NULL COMMENT '行为模式', `project_name` varchar(50) DEFAULT NULL COMMENT '项目名称', `handler` varchar(50) DEFAULT NULL COMMENT 'Handler名称', `level` varchar(20) DEFAULT NULL COMMENT '日志等级', `host_ip` varchar(50) DEFAULT NULL COMMENT '服务器ip', `record_time` datetime NOT NULL COMMENT '记录时间', `record_timestamp` int(11) NOT NULL COMMENT '记录时间',`log_msg` longtext NOT NULL COMMENT '日志内容', PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
                        )
                    else:
                        self.mysql_db.fetch_and_commit(
                            f"CREATE TABLE `{self.table_name}` ( `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键id', `request_code` varchar(50) DEFAULT NULL COMMENT '请求标识', `action_mode` varchar(10) DEFAULT NULL COMMENT '行为模式', `project_name` varchar(50) DEFAULT NULL COMMENT '项目名称', `level` varchar(20) DEFAULT NULL COMMENT '日志等级', `host_ip` varchar(50) DEFAULT NULL COMMENT '服务器ip', `record_time` datetime NOT NULL COMMENT '记录时间', `record_timestamp` int(11) NOT NULL COMMENT '记录时间',`log_msg` longtext NOT NULL COMMENT '日志内容', PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
                        )
            except:
                print("构建mysql日志环境异常:" + traceback.format_exc())
                pass
        elif self.storage_engine.lower() == "redis":
            from seven_framework.redis import RedisHelper
            try:
                self.redis_log_client = RedisHelper.redis_init(
                    config_dict=storage["config"])
                # 获取表名
                self.redis_list_key = "python_log_list"

                if "level_setting" in storage:
                    for level_item in storage["level_setting"]:
                        if level_item["level"].lower() == level.lower():
                            self.redis_list_key = level_item["key"]
                            # 可定制不通level走不通的redis连接
                            if "config" in level_item["level"]:
                                self.redis_log_client = RedisHelper.redis_init(
                                    level_item["level"]["config"])
            except:
                print("构建redis日志环境异常:" + traceback.format_exc())
                pass
        elif self.storage_engine.lower() == "clickhouse":
            try:
                from seven_framework.clickhouse import ClickhouseHelper
                self.clickhouse_client = ClickhouseHelper(
                    **storage["config"]).clickhouse_client

                # 获取表名
                self.table_name = "python_log_tb"

                if "level_setting" in storage:
                    for level_item in storage["level_setting"]:
                        if level_item["level"].lower() == level.lower():
                            self.table_name = level_item["key"]

                # 判断制定数据库中标是否存在
                exist_result = self.clickhouse_client.execute(
                    f"SELECT name FROM system.tables WHERE database='{storage['config']['database']}' AND name='{self.table_name}';"
                )

                if not exist_result:
                    if level.lower() == "http":
                        self.clickhouse_client.execute(
                            f"CREATE TABLE {storage['config']['database']}.{self.table_name}( request_code String, action_mode String, project_name String, level String, handler String, host_ip String, record_time datetime, log_msg String) ENGINE = MergeTree() ORDER BY record_time;"
                        )
                    else:
                        self.clickhouse_client.execute(
                            f"CREATE TABLE {storage['config']['database']}.{self.table_name}( request_code String, action_mode String, project_name String, level String, host_ip String, record_time datetime, log_msg String) ENGINE = MergeTree() ORDER BY record_time;"
                        )
            except:
                print("构建clickhouse日志环境异常:" + traceback.format_exc())
                pass

        logging.Handler.__init__(self)

    def emit(self, record):
        """
        :description: logging.Handler内置事件
        :param record: 日志信息
        :return: 无
        :last_editors: ChenXiaolei
        """
        project_name = self.project_name
        level = record.levelname
        host_ip = self.host_ip
        record_time = int(record.created)
        if hasattr(record, "message"):
            log_msg = record.message
        elif hasattr(record, "msg"):
            log_msg = record.msg
        else:
            log_msg = ""

        if self.storage_engine == "mysql":
            try:
                extra_sql_field = ""
                extra_sql_value = ""
                if hasattr(record, "extra") and record.extra:
                    for key in record.extra.keys():
                        extra_sql_field += f",{key}"
                        extra_sql_value += f",'{record.extra[key]}'"

                self.mysql_db.fetch_and_commit(
                    f"INSERT INTO {self.table_name}(project_name,level,host_ip,record_time,record_timestamp,log_msg{extra_sql_field}) VALUE('{project_name}','{level}','{host_ip}','{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record_time))}',{record_time},'{pymysql.converters.escape_string(log_msg)}'{extra_sql_value});"
                )
            except:
                print("日志入库异常:" + traceback.format_exc())
                pass

        elif self.storage_engine == "redis":
            try:
                log_info = {}
                log_info["project_name"] = project_name
                log_info["level"] = level
                log_info["host_ip"] = host_ip
                log_info["record_time"] = record_time
                log_info["log_msg"] = log_msg

                if hasattr(record, "extra") and record.extra:
                    for key in record.extra.keys():
                        log_info[key] = record.extra[key]

                self.redis_log_client.lpush(self.redis_list_key,
                                            JsonHelper.json_dumps(log_info))
            except:
                print("日志lpush至redis时异常:" + traceback.format_exc())
                pass
        elif self.storage_engine == "clickhouse":
            try:
                extra_sql_field = ""
                extra_sql_value = ""
                if hasattr(record, "extra") and record.extra:
                    for key in record.extra.keys():
                        extra_sql_field += f",{key}"
                        extra_sql_value += f",'{record.extra[key]}'"

                self.clickhouse_client.execute(
                    f"INSERT INTO {self.table_name}(project_name,level,host_ip,record_time,log_msg{extra_sql_field}) VALUES('{project_name}','{level}','{host_ip}',{record_time},'{pymysql.converters.escape_string(log_msg)}'{extra_sql_value});"
                )
            except:
                print("日志写入clickhouse异常:" + traceback.format_exc())
                pass
