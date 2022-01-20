# -*- coding: utf-8 -*-
#
# Copyright 2016 Ricequant, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import re
import sys

import click
import requests
import rqdatac
from rqdatac.share.errors import AuthenticationFailed
from rqsdk.const import PERMISSIONS_INFO_URL, RQDATAC_DEFAULT_ADDRESS
from rqsdk.script_update import update_bash_file
from tabulate import tabulate


def format_rqdatac_uri(uri):
    """
    整理rqdatac_uri 并返回
    uri可能有以下三种方式
    * 纯license
    * 手机号:密码
    * 完整的rqdatac_uri
    """
    if uri is None:
        raise ValueError("参数异常")

    if ":" not in uri:
        uri = "license:{}".format(uri)

    if '@' not in uri:
        if '/' in uri:
            raise ValueError("输入的 license 存在非法斜线'/'")
        uri = "tcp://{}@{}".format(uri, RQDATAC_DEFAULT_ADDRESS)

    if not re.match(r"\w*://.+:[^\n\r/]+@.+:\d+", uri):
        raise ValueError('无效的 rqdatac_uri ,格式应为 user:password 或者 tcp://user:password@ip:port')
    return uri


def get_permissions_info(rqdtac_uri):
    """访问米筐官网获取license信息"""
    proxy_uri = os.environ.get("RQSDK_PROXY", "")
    if not proxy_uri:
        resp = requests.get(PERMISSIONS_INFO_URL, params={"rqdatac_uri": rqdtac_uri})
    else:
        resp = requests.get(PERMISSIONS_INFO_URL, params={"rqdatac_uri": rqdtac_uri}, proxies={
            'http': proxy_uri,
            'https': proxy_uri
        })
    res = resp.json()
    if res['code'] != 0:
        raise AuthenticationFailed("获取license权限信息错误\nuri={}\n{}".format(rqdtac_uri, res.get("message")))
    return res['data']


def get_license_info(uri, license_name='RQSDK LICENSE'):
    """从license获取账户的相关信息"""
    if not uri:
        click.echo("当前环境无{}".format(license_name))
        return
    try:
        _info = get_permissions_info(uri)
    except AuthenticationFailed as err:
        click.echo("{}不可用： {}".format(license_name, err.args[0]))
        click.echo("license_name 设置失败，请检查输入是否有效，或者联系米筐技术支持。")
        click.echo("")
        return
    return _info


def get_rqdata_info(uri=None, license_name='RQDATA LICENSE'):
    """从rqdata获取账户的相关信息"""
    try:
        rqdatac.init(uri=uri)
        _info = rqdatac.user.get_quota()
    except(AuthenticationFailed, ValueError) as err:
        click.echo("{}：{}".format(license_name, uri))
        click.echo("{} 不可用，原因：【{}】；请使用【rqsdk config --rqdatac】 命令更新".format(license_name, err.args[0]))
    else:
        return _info


def print_license_info(uri_license=os.environ.get('RQSDK_LICENSE') or os.environ.get('RQDATAC2_CONF'),
                       uri_rqdata=os.environ.get('RQDATAC2_CONF')):
    """展示 rqdata_uri 账户的相关信息"""
    license_info = get_license_info(uri_license)
    rqdata_info = get_rqdata_info(uri_rqdata)
    if not license_info or not rqdata_info:
        return
    license_info.update(rqdata_info)

    table_data = license_info["permissions_table"]
    data = [[i["name"], i["type"], i["back_test_level"], i["enable"]] for i in table_data]

    tb = tabulate(data, headers=["产品", "标的品种", "频率", "开启"], tablefmt="rst")
    width = tb.find("\n")
    click.echo("=" * width + tb[width:-width] + "=" * width)
    row = []
    if "rqdata_limit__license_type__full" in license_info["current_permissions"]:
        pass
    elif "rqdata_limit__license_type__edu" in license_info["current_permissions"]:
        row += ["教育版 |"]
    else:
        row += ["试用版 |"]

    if license_info['bytes_limit'] == 0:
        row += ["流量限制:该 license 无流量限制 |"]
    else:
        row += ["流量限制: {:.2f} MB |".format(license_info['bytes_limit'] / 2 ** 20)]
        row += [
            "剩余流量: {:.2f} MB |".format((license_info['bytes_limit'] - license_info['bytes_used']) / 2 ** 20)]
    row += ["剩余有效天数: {} |".format(license_info['date_to_expire'])]

    click.echo(tabulate([row], tablefmt="plain"))
    click.echo("=" * width)
    for i in range(int(len(uri_license) / width) + 1):
        click.echo(uri_license[i * width:(i + 1) * width])
    click.echo("=" * width)
    return True


def set_to_environ(variables, value):
    """将变量设置到环境变量
    :param variable_name: string
    :param value: string
    """
    if set(variables) == {"RQDATAC_CONF", "RQSDK_LICENSE"}:
        var_name = "license"
    elif variables == ["RQDATAC2_CONF"]:
        var_name = "rqdatac license"
    else:
        var_name = "代理"

    if not isinstance(variables, list):
        variables = [variables]
    if sys.platform.startswith("win"):
        for variable_name in variables:
            os.popen('setx {variable_name} "{value}" '.format(variable_name=variable_name, value=value))
    else:
        update_bash_file(variables, value)
    # os.environ第一次加载后即使改了配置文件也不会刷新，除非重新加载或重新设置
    for variable_name in variables:
        os.environ[variable_name] = value
    click.echo("当前 {var_name} 已设置为 {value}".format(var_name=var_name, value=value))
    click.echo("请重启当前的 terminal ".format(uri=value))


def license_console():
    """license 交互环境"""
    # print
    uri_license = os.environ.get('RQSDK_LICENSE') or os.environ.get('RQDATAC2_CONF')
    if uri_license:
        print_license_info(uri_license)
    else:
        click.echo("当前环境没有配置 license ")

    while True:
        # input
        click.echo('如需修改请按照【用户名:密码】的格式输入您的用户名密码或直接键入license key。')
        click.echo('不更改则按 Enter 键退出')
        rqsdk_license = input()
        if not rqsdk_license:
            return
        rqsdk_license = format_rqdatac_uri(rqsdk_license)
        rqdata_license = os.environ.get('RQDATAC2_CONF') or rqsdk_license
        if print_license_info(rqsdk_license, rqdata_license):
            set_to_environ(['RQSDK_LICENSE', 'RQDATAC_CONF'], rqsdk_license)
            return
