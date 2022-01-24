#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# 创建项目目录
import argparse
import os
import sys

from HTest.logger import logger

sys.path.append(os.path.dirname(__file__))


def create_scaffold(project_path):

    if os.path.isdir(project_path):
        logger.error(u"Folder {} exists, please specify a new folder name.".format(project_path))
        return 1

    elif os.path.isfile(project_path):
        logger.error(f"Project name {project_path} conflicts with existed file, please specify a new one.")
        return 1

    logger.error(f"Start to create new project: {project_path}\n")

    def create_folder(path):
        os.makedirs(path)
        print(f"Created folder: {path}")

    def create_file(file, file_content=""):
        with open(file, "w", encoding="utf-8") as f:
            f.write(file_content)
        print(f"Created file: {file}")

    config_content = """
# 数据库的配置信息
DB:
  user: Hsapi
  pwd: Hsapi-2021
  host: 192.168.1.8
  database: hs_dl
  port: 21023

# 发邮件的配置信息
email:
  HOST_SERVER: smtp.qq.com
  FROM: 1285642171@qq.com
  TO: [l.tao@hang-shu.com, 1285642171@qq.com]
  user_code: bancxgdgvdevbafd
  SUBJECT: 自动化测试报告

    """

    login_step_content = """# 功能步骤编写规则
config:
    name: login-step  # 功能名称
    driver: HTest     # 驱动
    driver-args:      # 其他引用
    info: 登陆功能     # 功能描述

step-list:
    # [函数，元素定位方式， 元素定位内容， 输入参数]
    - [hs-input, $path, $pathname, $username]   # 输入用户名步骤
    - [hs-input, $path, $pathname, $password]   # 输入密码步骤
    - [hs-click, $path, $pathname]              # 登陆步骤
    - [hs-check, $path, $pathname, $check]      # 校验步骤
    """

    login_case_content = """# 测试用例编写规则
config:
  name: login-case      # 测试用例名称
  driver: HTest         # 测试驱动
  driver-args: H5-ui    # 其他引用
  info: 禅道登陆         # 用例描述

# 调用的是login-step.yml文件中的测试步骤规则
import: login-step

用例执行，定义hs-input为输入标识，hs-click为点击标识，hs-check为校验标识
case-list:
  - [$args, $username, $password, $check]  # 测试用例总览
  - [hs-input, id, account, $username]     # 输入用户名
  - [hs-input, name, password, $password]  # 输入密码
  - [hs-click, id, submit]                 # 点击登陆
  - [hs-check, $check]                     # 校验                 
    """

    login_suit_content = """# 测试套件编写规则
config:
  name: login-suit    # 测试用例集名称
  driver: HTest       # 测试驱动
  driver-args:        # 其他引用
  info: 禅道登陆用例集合 # 用例集合描述
  
# 调用的是login-case.yml文件中的测试用例规则
import: login-case

# 测试url地址
url: 'http://cd.sh.hang-shu.com:14528/zentao/user-login.html'

# 用例集合，设计五条测试用例
main-list:
   - [case1, l.tao, Aa123456, 密码错误，登录失败]
   - [case2, w.tao, l.tao@hang-shu.com, 用户名错误，登录失败]
   - [case3, None, l.tao@hang-shu.com, 登录失败，用户名不能为空]
   - [case4, l.tao, None, 登录失败，密码不能为空]
   - [case5, l.tao, l.tao@hang-shu.com, 登录成功]
    """

    create_folder(project_path)
    create_folder(os.path.join(project_path, "testcase"))
    create_folder(os.path.join(project_path, "testcase", "step"))
    create_folder(os.path.join(project_path, "testcase", "case"))
    create_folder(os.path.join(project_path, "testcase", "suit"))
    create_folder(os.path.join(project_path, "config"))
    create_folder(os.path.join(project_path, "report"))
    create_folder(os.path.join(project_path, "logs"))
    create_folder(os.path.join(project_path, "plugin"))
    create_file(os.path.join(project_path, "config", "config.yaml"), config_content)
    create_file(os.path.join(project_path, "testcase", "step", "login-step.yml"), login_step_content)
    create_file(os.path.join(project_path, "testcase", "case", "login-case.yml"), login_case_content)
    create_file(os.path.join(project_path, "testcase", "suit", "login-suit.yml"), login_suit_content)

    return 0


def main_HTest():
    """
    UI test: parse command line options and run commands.
    """
    parser = argparse.ArgumentParser(
        description='Automated testing framework based on unittest by Tao.')
    parser.add_argument(
        '-v', '--version', dest='version', action='store_true',
        help="show version")
    parser.add_argument(
        '-s', '--start', dest='project',
        help="Create a new project name.")
    parser.add_argument(
        '-r', '--run', dest='testcase',
        help="Run the test case.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)

    else:
        if args.version:
            logger.error("{}".format("0.2.0"))
            exit(0)

        elif args.project:
            project_path = os.path.join(os.getcwd(), args.project)
            create_scaffold(project_path)
            exit(0)

        elif args.testcase and sys.argv[1] == "-r":
            file_suffix = os.path.splitext(sys.argv[2])[1].lower()  # 获取文件后缀名
            file = os.path.join(os.getcwd(), args.testcase)  # 获取执行文件
            print(file)
            if file_suffix in ['.yaml', '.yml']:
                from testcase import get_data
                get_data(file)
                from run_yaml import test_yaml
                test_yaml()
            elif file_suffix == '.py':
                from unittest.main import main
                main(module=None)
            else:
                print("ModuleFoundError: Not supported %s" % file)
            exit(0)

        else:
            logger.error("Please enter correct argument")
            exit(0)
