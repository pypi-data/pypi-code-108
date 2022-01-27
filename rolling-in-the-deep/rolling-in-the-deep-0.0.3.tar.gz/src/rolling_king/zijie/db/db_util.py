#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/8 3:26 下午
# @Author  : zhengyu.0985
# @FileName: db_util.py
# @Software: PyCharm

import pymysql
import configparser
import json
import sys


# 定义一个db链接类
class DBConn:
    """
    使用cnn进行db连接
    """
    def __init__(self, db_key, db_conf_relative_path):
        self.db_key = db_key
        conf_file = open(db_conf_relative_path)
        cf = configparser.ConfigParser()
        cf.read_file(conf_file)
        json_str = cf.get("mysql", db_key)
        print(json_str)
        dict_val = json.loads(json_str)
        host = dict_val['db_host']
        user = dict_val['db_user']
        passwd = dict_val['db_passwd']
        db = dict_val['db_db']
        charset = dict_val['db_charset']
        port = dict_val['db_port']
        print("host = {0}".format(host))
        print("user = {0}".format(user))
        print("passwd = {0}".format(passwd))
        print("db = {0}".format(db))
        print("charset = {0}".format(charset))
        print("port = {0}".format(port))

        self.conn = pymysql.connect(host=host,
                                    user=user,
                                    passwd=passwd,
                                    db=db,
                                    charset=charset,
                                    port=int(port),
                                    )
        print("成功连接{0}数据库。".format(self.db_key))

    def query_db(self, sql_str):
        cur = self.conn.cursor()
        try:
            affected_row = cur.execute(sql_str)
            print("【{0}】SQL语句返回{1}条数据".format(sql_str, affected_row))
            self.conn.commit()
            return cur.fetchall()
        except Exception as e:
            print(e.with_traceback(sys.exc_info()[2]))
        finally:
            cur.close()

    def update_db(self, sql_str):
        cur = self.conn.cursor()
        try:
            affected_row = cur.execute(sql_str)
            self.conn.commit()
            print("【{0}】SQL语句共影响{1}条数据".format(sql_str, affected_row))
            return affected_row
        except Exception as e:
            print(e.with_traceback(sys.exc_info()[2]))
        finally:
            cur.close()

    def close_db(self):
        self.conn.close()
        print("与{0}的数据库连接已关闭。".format(self.db_key))


if __name__ == "__main__":
    # 建立连接
    conn = DBConn("DB_BOE_Site_Reldb", "../../conf/db.conf")
    # 执行SELECT
    tuple_result = conn.query_db("select * from union_media where id in (45535, 45532, 45507, 259);")
    print(tuple_result)
    for row_result in tuple_result:
        print("当前行元祖为：", row_result)
        print("当前行共{0}个字段".format(len(row_result)))
        print("当前行第一个字段值=", row_result[0])
    # 执行UPDATE
    affected_row_num = conn.update_db("update union_media_function_rel set function_id = 35 where id = '111287';")
    print("更新了{0}行。".format(affected_row_num))
    # 关闭连接
    conn.close_db()
