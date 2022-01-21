# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2021/8/24 15:11
# @Author: "John"
import pymongo
from sshtunnel import SSHTunnelForwarder


def get_srv_and_cursor(esc_address, esc_port, esc_usr, ssh_pkey, ssh_pkey_pwd, mongo_uri, mongo_port, data_base, usr, pwd):
    """

    :param esc_address: 跳板机地址
    :param esc_port: 跳板机端口
    :param esc_usr: 跳板机用户名称
    :param ssh_pkey: ssh 私钥本地路径（注意系统盘符）
    :param ssh_pkey_pwd:
    :param mongo_uri: MongoDB 实例地址
    :param mongo_port: MongoDB 实例端口
    :param data_base: 用户权限下的 database
    :param usr: MongoDB 用户名称
    :param pwd: MongoDB 用户密码
    """
    server = SSHTunnelForwarder(

        ssh_address_or_host=(esc_address, esc_port),
        ssh_username=esc_usr,
        ssh_pkey=ssh_pkey,  # 私钥路径
        ssh_private_key_password=ssh_pkey_pwd,  # 跳板机私钥密码
        remote_bind_address=(mongo_uri, mongo_port)  # 设置数据库服务地址及端口
    )
    # 启动跳板机
    server.start()

    conn = pymongo.MongoClient(
        host='127.0.0.1',  # host、port 固定
        port=server.local_bind_port
    )

    db = conn[data_base]
    db.authenticate(usr, pwd)
    return server, conn


if __name__ == '__main__':
    mongodb_address = ''
    mongodb_user = ''
    mongodb_pwd = ''
    mongodb_authorized_database = ''
    mongodb_port = 0

    esc_ip_or_address = ''
    esc_port_num = 0
    esc_usr_name = ''
    esc_pkey_pwd = ''
    esc_pkey_path = ''

    svr, cur = get_srv_and_cursor(esc_ip_or_address, esc_port_num, esc_usr_name,
                                  esc_pkey_path, esc_pkey_pwd, mongodb_address,
                                  mongodb_port, mongodb_authorized_database, mongodb_user, mongodb_pwd)
    pass
