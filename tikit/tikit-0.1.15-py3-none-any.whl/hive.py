# -*- coding: utf-8 -*-
import os
import random
import string
import csv

from pyhive import hive
from hdfs import Client as HdfsClient


def _get_tmp_path():
    """
    返回随机生成的hdfs临时目录
    :return:    临时目录
    :rtype:     str
    """
    folder = "".join(random.sample(string.ascii_letters + string.digits, random.randint(12, 20)))
    return "/tmp/tikit/%s" % folder


def _get_host_port(server):
    """
    把服务地址解析成主机地址和端口
    :param server:  服务地址
    :type server:   str
    :return:        主机地址和端口
    :rtype:         list
    """
    parts = server.split(":")
    if len(parts) != 2:
        raise Exception('invalid hive_server, should like "10.0.0.1:7001"')
    return parts


def upload_to_hive_by_hdfs(local_path, hdfs_url, hive_server, table_name, database="default", auth="CUSTOM", username=None,
                   password=None, overwrite=False, partition=""):
    """把本地文件的数据导入到hive表中，hdfs作为中间存储。
    过程：先把本地文件上传到hdfs上，然后再从hdfs文件导入到hive中。

    :param local_path:      本地文件或者文件夹。文件夹中不能包含子文件夹。
    :type local_path:       str
    :param hdfs_url:        webhdfs的url，如：http://10.0.3.16:4008
    :type hdfs_url:         str
    :param hive_server:     HiveServer2的地址
    :type hive_server:      str
    :param table_name:      Hive表的名称
    :type table_name:       str
    :param database:        数据库名称
    :type database:         str
    :param auth:            认证的方式
    :type auth:             str
    :param username:        数据库认证的用户名
    :type username:         str
    :param password:        数据库认证的密码
    :type password:         str
    :param overwrite:       是否删掉原来的数据
    :type overwrite:        bool
    :param partition:       分区的选择
    :type partition:        str
    :return:
    :rtype:
    """
    hdfs_path = hdfs_tmp_path = _get_tmp_path()
    hdfs_client = HdfsClient(hdfs_url)
    # 上传文件到一个不存在的目录（斜杠结尾）的时候，hdfs库会把目录当成最终文件
    if os.path.isfile(local_path):
        hdfs_path = os.path.join(hdfs_path, os.path.basename(local_path))
    hdfs_client.upload(hdfs_path, local_path)
    try:
        insert_hdfs_into_hive(hdfs_path, hive_server, table_name, database, auth, username,
                              password, overwrite, partition)
    finally:
        hdfs_client.delete(hdfs_tmp_path, True)


def insert_hdfs_into_hive(hdfs_path, hive_server, table_name, database="default", auth="CUSTOM", username=None,
                          password=None, overwrite=False, partition=""):
    """把hdfs的文件数据导入到hive表中。

    :param hdfs_path:       hdfs上的文件或者文件夹。文件夹中不能包含子文件夹。如：/tmp/file.csv
    :type hdfs_path:        str
    :param hdfs_url:        webhdfs的url，如：http://10.0.3.16:4008
    :type hdfs_url:         str
    :param hive_server:     HiveServer2的地址
    :type hive_server:      str
    :param table_name:      Hive表的名称
    :type table_name:       str
    :param database:        数据库名称
    :type database:         str
    :param auth:            认证的方式
    :type auth:             str
    :param username:        数据库认证的用户名
    :type username:         str
    :param password:        数据库认证的密码
    :type password:         str
    :param overwrite:       是否删掉原来的数据
    :type overwrite:        bool
    :param partition:       分区的选择
    :type partition:        str
    :return:
    :rtype:
    """
    hive_host, hive_port = _get_host_port(hive_server)
    with hive.Connection(host=hive_host, port=hive_port, database=database,
                         username=username, password=password, auth=auth) as conn:
        with conn.cursor() as cursor:
            sql = "LOAD DATA INPATH '{}' {} INTO TABLE {} {}".format(
                hdfs_path,
                "OVERWRITE" if overwrite else "",
                table_name,
                "" if partition == "" else "PARTITION (%s)" % partition
            )
            cursor.execute(sql)


# def export_csv_from_hive(local_path, hive_server, table_name="", sql="", database="default", auth="CUSTOM",
#                          username=None, password=None):
#     """把hive表的数据读出，写到本地的csv文件
#
#     :param local_path:      本地文件或者文件夹。文件夹中不能包含子文件夹。
#     :type local_path:       str
#     :param hive_server:     HiveServer2的地址
#     :type hive_server:      str
#     :param table_name:      Hive表的名称。sql设置时忽略此参数
#     :type table_name:       str
#     :param sql:             查数据sql语句。如：select * from t1
#     :type sql:              str
#     :param database:        数据库名称
#     :type database:         str
#     :param auth:            认证的方式
#     :type auth:             str
#     :param username:        数据库认证的用户名
#     :type username:         str
#     :param password:        数据库认证的密码
#     :type password:         str
#     :return:
#     :rtype:
#     """
#     if local_path.endswith("/") or os.path.isdir(local_path):
#         local_path = os.path.join(local_path, "result.csv")
#     if os.path.exists(local_path):
#         raise Exception('"%s" is already existed' % local_path)
#     local_dir = os.path.dirname(local_path)
#     if local_dir != "" and not os.path.exists(local_dir):
#         os.makedirs(local_dir)
#     # 支持table_name、sql两种方式，sql优先
#     if table_name == "" and sql == "":
#         raise Exception('"table_name" and "sql" cannot both be empty')
#     if sql == "":
#         sql = "SELECT * FROM %s" % table_name
#     # 读出表内容，写入到文件
#     hive_host, hive_port = _get_host_port(hive_server)
#     with hive.Connection(host=hive_host, port=hive_port, database=database,
#                          username=username, password=password, auth=auth) as conn:
#         with conn.cursor() as cursor, open(local_path, 'w') as f:
#             writer = csv.writer(f)
#             cursor.execute(sql)
#             # 测试过使用 cursor.fetchmany(10000)的方式，性能更差（1000万条数据，183M）
#             for row in cursor:
#                 writer.writerow(row)
#     return local_path


def export_from_hive_by_hdfs(local_path, hdfs_url, hive_server, table_name="", sql="", database="default",
                             auth="CUSTOM", username=None, password=None,
                             row_format="row format delimited fields terminated by ','"):
    """导出hive表到本地上，hdfs作为中间存储。对于大文件，这种方式比直接从hive表写到本地的效率更高。
    过程：先把hive导出到hdfs上，然后再从hdfs下载文件到本地。

    :param local_path:      本地的目录
    :type local_path:       str
    :param hdfs_url:        webhdfs的url，如：http://10.0.3.16:4008
    :type hdfs_url:         str
    :param hive_server:     HiveServer2的地址
    :type hive_server:      str
    :param table_name:      Hive表的名称。sql设置时忽略此参数
    :type table_name:       str
    :param sql:             查数据sql语句。如：select * from t1
    :type sql:              str
    :param database:        数据库名称
    :type database:         str
    :param auth:            认证的方式
    :type auth:             str
    :param username:        数据库认证的用户名
    :type username:         str
    :param password:        数据库认证的密码
    :type password:         str
    :param row_format:      行的输出格式
    :type row_format:       str
    :return:
    :rtype:
    """
    if os.path.isfile(local_path):
        raise Exception('"local_path" cannot be file')
    tmp_path = _get_tmp_path()
    hdfs_path = os.path.join(tmp_path, "result")
    hdfs_client = HdfsClient(hdfs_url)
    save_hive_to_hdfs(hdfs_path, hive_server, table_name, sql, database, auth, username, password, row_format)
    try:
        local_dir = os.path.dirname(local_path)
        if local_dir != "" and not os.path.exists(local_dir):
            os.makedirs(local_dir)
        return hdfs_client.download(hdfs_path, local_path)
    finally:
        hdfs_client.delete(hdfs_path, True)


def save_hive_to_hdfs(hdfs_path, hive_server, table_name="", sql="", database="default", auth="CUSTOM",
                      username=None, password=None, row_format="row format delimited fields terminated by ','"):
    """把hive表的数据导出到hdfs上

    :param hdfs_path:       目标hdfs的保存路径
    :type hdfs_path:        str
    :param hive_server:     HiveServer2的地址
    :type hive_server:      str
    :param table_name:      Hive表的名称。sql设置时忽略此参数
    :type table_name:       str
    :param sql:             查数据sql语句。如：select * from t1
    :type sql:              str
    :param database:        数据库名称
    :type database:         str
    :param auth:            认证的方式
    :type auth:             str
    :param username:        数据库认证的用户名
    :type username:         str
    :param password:        数据库认证的密码
    :type password:         str
    :param row_format:      行的输出格式
    :type row_format:       str
    :return:
    :rtype:
    """
    if table_name == "" and sql == "":
        raise Exception('"table_name" and "sql" cannot both be empty')
    hive_host, hive_port = _get_host_port(hive_server)
    with hive.Connection(host=hive_host, port=hive_port, database=database,
                         username=username, password=password, auth=auth) as conn:
        with conn.cursor() as cursor:
            # INSERT OVERWRITE [LOCAL] DIRECTORY directory1 SELECT ... FROM ...
            if sql == "":
                execute_sql = "INSERT OVERWRITE DIRECTORY '{}' {} SELECT {} FROM {}".format(
                    hdfs_path,
                    row_format,
                    "*",
                    table_name
                )
                cursor.execute(execute_sql)
            else:
                execute_sql = "INSERT OVERWRITE DIRECTORY '{}' {} {}".format(
                    hdfs_path,
                    row_format,
                    sql
                )
                cursor.execute(execute_sql)
    return hdfs_path
