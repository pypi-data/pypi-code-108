#!/usr/bin/env python3.7
# _*_ coding:utf-8 _*_
import os
import sys

data = os.path.dirname(os.path.abspath(__file__))
print(data)
# 测试项目的路径
# BASE_DIR = os.path.join(os.getcwd())
# sys.path.append(BASE_DIR)
#
# # 邮件配置文件
# EMAIL_DIR = os.path.join(os.getcwd(), "config", "email.ini")
# # 测试报告目录
# TEST_REPORT = os.path.join(BASE_DIR, "report")
# # 日志目录
# LOG_DIR = os.path.join(BASE_DIR, "logs")
#
# if not os.path.exists(EMAIL_DIR) or not os.path.exists(TEST_REPORT) or not os.path.exists(LOG_DIR):
#     print("请把工作目录设置为项目主目录")
#     exit(0)
