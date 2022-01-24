# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-05-09 20:39:20
:LastEditTime: 2021-02-22 15:34:50
:LastEditors: ChenXiaolei
:Description: 基础控制台类
"""

from seven_framework import *
import sys
global environment
if "--production" in sys.argv:
    environment = "production"
    config_file = "config.json"
elif "--testing" in sys.argv:
    environment = "testing"
    config_file = "config_testing.json"
else:
    environment = "development"
    config_file = "config_dev.json"

sys.path.append(".local")  # 不可删除,置于其他import前
# 初始化配置,执行顺序需先于调用模块导入
config.init_config(config_file)  # 全局配置,只需要配置一次

# 项目标识
project_name = config.get_value("project_name", None)

# 初始化error级别日志
logger_error = None
# 初始化info级别日志
logger_info = None

# 读取日志配置
log_config = config.get_value("logger")

# 日志存储路径
log_file_path = "logs"
if log_config and "log_file_path" in log_config:
    log_file_path = log_config["log_file_path"]

logger_error = Logger(f"{log_file_path.rstrip('/')}/log_error", "ERROR", "log_error",
                        HostHelper.get_host_ip(), project_name,
                        log_config).get_logger()

logger_info = Logger(f"{log_file_path.rstrip('/')}/log_info", "INFO", "log_info",
                        HostHelper.get_host_ip(), project_name,
                        log_config).get_logger()

logger_sql = Logger(f"{log_file_path.rstrip('/')}/log_sql", "SQL", "log_sql",
                        HostHelper.get_host_ip(), project_name,
                        log_config).get_logger()
                    
logger_http = Logger(f"{log_file_path.rstrip('/')}/log_http", "HTTP", "log_http",
                        HostHelper.get_host_ip(), project_name,
                        log_config).get_logger()