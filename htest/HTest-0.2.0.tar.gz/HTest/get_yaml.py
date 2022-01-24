#!/usr/bin/env python3.7
# _*_ coding:utf-8 _*_
# 读取yaml文件
import os
import sys
import yaml

sys.path.append(os.path.dirname(__file__))
path = os.path.join(os.path.dirname(__file__), "content", "data.yaml")
if not os.path.exists(path):
    os.system(r"touch {}".format(path))


def get_yaml():
    """
    读取yaml文件
    :return: Dict
    order by tao
    """
    f = open(path, encoding='utf-8')
    data = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    return data


def write_yaml(data):
    """
    写入yaml文件
    :param data: [{'database': 'Hs-api', 'port': 21020}, {'url': 'www.baidu.com'}]
    """
    with open(path, encoding='utf-8', mode='w') as f:
        yaml.dump(data, stream=f, allow_unicode=True)


def clear_yaml():
    """
    清除yaml文件
    """
    with open(path, mode='w', encoding='utf-8') as f:
        f.truncate()


if __name__ == '__main__':
    clear_yaml()
    data0 = 'http://cd.sh.hang-shu.com:14528/zentao/user-login.html'
    data1 = [['$args', '$username', '$password', '$check'], ['hs-input', 'id', 'account', '$username'], ['hs-input', 'name', 'password', '$password'], ['hs-click', 'id', 'submit'], ['hs-check', '$check']]
    data2 = [['case1', 'l.tao', 'Aa123456', '密码错误，登录失败'], ['case2', 'w.tao', 'Aa123456', '用户名错误，登录失败'], ['case3', 'None', 'Aa123456', '登录失败，用户名不能为空'], ['case4', 'l.tao', 'None', '登录失败，密码不能为空'], ['case5', 'l.tao', 'l.tao@hang-shu.com', '登录成功']]
    write_yaml({'url': data0, 'case-list': data1, 'main-list': data2})
    print(get_yaml().get("main-list"))
