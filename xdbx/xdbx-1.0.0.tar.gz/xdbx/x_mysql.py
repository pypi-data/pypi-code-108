# #!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2021/12/16 18:56
# @Author : BruceLong
# @FileName: x_sqlserver.py
# @Email   : 18656170559@163.com
# @Software: PyCharm
# @Blog ：http://www.cnblogs.com/yunlongaimeng/
import copy

from .config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT

import datetime
import json
from urllib import parse
from typing import List, Dict

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql import cursors
from pymysql import err
import logging as log
from pyxbox import tools


def auto_retry(func):
    def wapper(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except (err.InterfaceError, err.OperationalError) as e:
                log.error(
                    """
                    error:%s
                    sql:  %s
                    """
                    % (e, kwargs.get("sql") or args[1])
                )

    return wapper


class MysqlDB:
    def __init__(
            self, host=MYSQL_HOST, port=MYSQL_PORT, db=MYSQL_DB, username=MYSQL_USERNAME, password=MYSQL_PASSWORD,
            **kwargs
    ):
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password
        self.kwargs = kwargs
        self.connect_sign = 0

    def connect(self):
        try:

            self.connect_pool = PooledDB(
                creator=pymysql,
                mincached=1,
                maxcached=100,
                maxconnections=100,
                blocking=True,
                ping=7,
                host=self.host,
                port=self.port,
                user=self.username,
                passwd=self.password,
                db=self.db,
                charset="utf8mb4",
                cursorclass=cursors.SSCursor,
                **self.kwargs
            )  # cursorclass 使用服务的游标，默认的在多线程下大批量插入数据会使内存递增
            self.connect_sign = 1

        except Exception as e:
            log.error(
                """
            连接数据失败：
            host: {}
            port: {}
            db: {}
            username: {}
            password: {}
            exception: {}
            """.format(
                    self.host, self.port, self.db, self.username, self.password, e
                )
            )
        else:
            log.debug("连接到mysql数据库 %s : %s" % (self.host, self.db))

    @classmethod
    def from_url(cls, url, **kwargs):
        # mysql://username:password@ip:port/db?charset=utf8mb4
        url_parsed = parse.urlparse(url)

        db_type = url_parsed.scheme.strip()
        if db_type != "mysql":
            raise Exception(
                "url error, expect mysql://username:ip:port/db?charset=utf8mb4, but get {}".format(
                    url
                )
            )

        connect_params = {}
        connect_params["host"] = url_parsed.hostname.strip()
        connect_params["port"] = url_parsed.port
        connect_params["username"] = url_parsed.username.strip()
        connect_params["password"] = url_parsed.password.strip()
        connect_params["db"] = url_parsed.path.strip("/").strip()

        connect_params.update(kwargs)

        return cls(**connect_params)

    @staticmethod
    def unescape_string(value):
        if not isinstance(value, str):
            return value

        value = value.replace("\\0", "\0")
        value = value.replace("\\\\", "\\")
        value = value.replace("\\n", "\n")
        value = value.replace("\\r", "\r")
        value = value.replace("\\Z", "\032")
        value = value.replace('\\"', '"')
        value = value.replace("\\'", "'")

        return value

    def get_connection(self):
        if not self.connect_sign:
            self.connect()
        conn = self.connect_pool.connection(shareable=False)
        # cursor = conn.cursor(cursors.SSCursor)
        cursor = conn.cursor()

        return conn, cursor

    def close_connection(self, conn, cursor):
        cursor.close()
        conn.close()

    def size_of_connections(self):
        """
        当前活跃的连接数
        @return:
        """
        if not self.connect_sign:
            self.connect()
        return self.connect_pool._connections

    def size_of_connect_pool(self):
        """
        池子里一共有多少连接
        @return:
        """
        if not self.connect_sign:
            self.connect()
        return len(self.connect_pool._idle_cache)

    def __create_table(self, cur, con, ite: dict, table: str, primary_key=None):
        '''
        合建表相关的信息
        :param item: 数据
        :param table: 表名
        :return:
        '''
        item = copy.deepcopy(ite)
        # cur = self.__get_connect()
        # 判断是否存在该表
        sql = f'''select * from information_schema.tables where table_name ='{table}';'''
        cur.execute(sql)
        table_sign = cur.fetchone()
        max_len = 767
        if not cur.fetchone():
            # 生成创建字段信息
            primary_key_dict = {}
            if isinstance(primary_key, str):
                primary_key_dict = {primary_key: max_len // 4}
            if isinstance(primary_key, dict):
                primary_key_dict = primary_key
            if isinstance(primary_key, list):
                primary_key_dict = {key: max_len // 4 // len(primary_key) for key in primary_key}
            if primary_key_dict:
                [item.pop(i) for i in primary_key_dict if i in list(item.keys())]
            field_info = ',\n'.join(
                [
                    # f'{field} bigint' if isinstance(values, int) else f'{field} nvarchar(max)'
                    f'{field} text'
                    for field, values in item.items()
                ]
            )

            end_field = list(item.keys())[-1]
            cur.execute('select version()')
            mysql_version = cur.fetchone()[0]
            pk_field = ','.join([f'`{i}`' for i in primary_key_dict.keys()])
            # 解决版本不同创建语句差异问题
            if mysql_version[:3] <= '5.5':
                pk_info = ',\n'.join(
                    [
                        f'{field} varchar({values})'
                        for field, values in primary_key_dict.items()
                    ]
                )
                field_info = ',\n'.join([field_info, pk_info])
                # 数据库版本小于等于5.5版本
                sql_table = f'''create table {table}(
                        x_id bigint NOT NULL AUTO_INCREMENT,
                        x_inserttime timestamp NULL DEFAULT CURRENT_TIMESTAMP,
--                         x_updatetime timestamp NULL DEFAULT '0000-00-00 00:00:00',
                        {field_info},
                        INDEX (x_id),
                        PRIMARY KEY ({pk_field})
                        )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;'''
                # --创建update触发器
                # sql_trigger = f'''CREATE TRIGGER trig_{table}_updatetime
                #                   BEFORE UPDATE ON {table} FOR EACH ROW
                #                   SET NEW.x_updatetime = NOW();
                #                   FLUSH'''
                try:
                    # print(sql_table)
                    cur.execute(sql_table)
                    # cur.execute(sql_trigger)
                    con.commit()
                    print(f'Mysql Version is :{mysql_version}', '*' * 15, 'Create Table Successful')
                except Exception as e:
                    print(f'Mysql Version is :{mysql_version}', '*' * 15, 'Create Table Failed', e)
            else:
                sql_table = f'''create table {table}(
                                x_id bigint NOT NULL AUTO_INCREMENT,
                                x_inserttime timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                                x_updatetime timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                {field_info},
                                PRIMARY KEY (`x_id`)
                                )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;'''
                if primary_key:
                    pk_info = ',\n'.join(
                        [
                            f'{field} varchar(255)'
                            for field, values in primary_key_dict.items()
                        ]
                    )
                    field_info = ',,\n'.join([field_info, pk_info])
                    sql_table = f'''create table {table}(
                                x_id bigint NOT NULL AUTO_INCREMENT,
                                x_inserttime timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                                x_updatetime timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                {field_info},
                                INDEX (x_id),
                                PRIMARY KEY ({pk_field})
                                )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;'''
                try:
                    # print(sql_table)
                    cur.execute(sql_table)
                    con.commit()
                    print(f'Mysql Version is :{mysql_version}', '*' * 15, 'Create Table Successful')
                except Exception as e:
                    print(f'Mysql Version is :{mysql_version}', '*' * 15, 'Create Table Failed', e)
        else:
            # 查询表字段
            select_fields_sql = f'''desc {table}'''
            cur.execute(select_fields_sql)
            # 获取已经存在的表字段
            allready_exists_fields = {i[0].lower() for i in cur.fetchall()}
            # 目前新的字段名
            new_fields = {i.lower() for i in item.keys()}
            # 差集算出需要添加的字段名
            not_exists_fields = new_fields - allready_exists_fields
            if list(not_exists_fields):
                # 构造字段信息
                not_exists_fields_info = ','.join(
                    [
                        # f'{field} bigint' if isinstance(values, int) else f'{field} nvarchar(max)'
                        f'{field} text'
                        for field, values in item.items() if field.lower() in not_exists_fields
                    ]
                )
                add_fields_sql = f'''alter table {table} add {not_exists_fields_info}'''
                try:
                    # print(add_fields_sql)
                    cur.execute(add_fields_sql)
                    con.commit()
                    print('Create Field Successful')
                except Exception as e:
                    print('Create Field Failed', e)

    @auto_retry
    def find(self, sql, limit=0, to_json=False):
        """
        @summary:
        无数据： 返回()
        有数据： 若limit == 1 则返回 (data1, data2)
                否则返回 ((data1, data2),)
        ---------
        @param sql:
        @param limit:
        @param to_json 是否将查询结果转为json
        ---------
        @result:
        """
        conn, cursor = self.get_connection()

        cursor.execute(sql)

        if limit == 1:
            result = cursor.fetchone()  # 全部查出来，截取 不推荐使用
        elif limit > 1:
            result = cursor.fetchmany(limit)  # 全部查出来，截取 不推荐使用
        else:
            result = cursor.fetchall()

        if to_json:
            columns = [i[0] for i in cursor.description]

            # 处理数据
            def convert(col):
                if isinstance(col, (datetime.date, datetime.time)):
                    return str(col)
                elif isinstance(col, str) and (
                        col.startswith("{") or col.startswith("[")
                ):
                    try:
                        # col = self.unescape_string(col)
                        return json.loads(col)
                    except:
                        return col
                else:
                    # col = self.unescape_string(col)
                    return col

            if limit == 1:
                result = [convert(col) for col in result]
                result = dict(zip(columns, result))
            else:
                result = [[convert(col) for col in row] for row in result]
                result = (dict(zip(columns, r)) for r in result)

        self.close_connection(conn, cursor)

        return result

    def add(self, sql, item, table, primary_key, exception_callfunc=None):
        """

        Args:
            sql:
            exception_callfunc: 异常回调

        Returns: 添加行数

        """
        affect_count = None

        try:
            conn, cursor = self.get_connection()
            self.__create_table(cur=cursor, con=conn, ite=item, table=table, primary_key=primary_key)
            affect_count = cursor.execute(sql)
            conn.commit()

        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
            """
                % (e, sql)
            )
            if exception_callfunc:
                exception_callfunc(e)
        finally:
            self.close_connection(conn, cursor)

        return affect_count

    def new_insert_one(self, item: Dict, table: str, primary_key, **kwargs):
        """
        添加数据, 直接传递json格式的数据，不用拼sql
        Args:
            table: 表名
            item: 字典 {"xxx":"xxx"}
            **kwargs:

        Returns: 添加行数

        """

        sql = tools.x_sql.make_insert_sql(table, item, **kwargs)
        return self.add(sql, item, table, primary_key)

    def insert_one(self, item: dict, table: str, primary_key=None, auto_table: bool = True):
        '''
        插入一条数据
        :param item:
        :param table:
        :return:
        '''
        conn, cursor = self.get_connection()
        if auto_table:
            self.__create_table(cur=cursor, con=conn, ite=item, table=table, primary_key=primary_key)
        # 获取到一个以键且为逗号分隔的字符串，返回一个字符串
        keys = ', '.join(item.keys())
        values = ', '.join(['%s'] * len(item))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        # print(sql)
        try:
            # 这里的第二个参数传入的要是一个元组
            # data = [v if isinstance(v, int) else str(v) for v in item.values()]
            data = [str(v) for v in item.values()]
            # print(data)
            cursor.execute(sql, tuple(data))
            print('Insert One Successful')
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
        pass

    def add_batch(self, sql, datas: List[Dict], table, primary_key=None, auto_table: bool = True):
        """
        @summary: 批量添加数据
        ---------
        @ param sql: insert ignore into (xxx,xxx) values (%s, %s, %s)
        # param datas: 列表 [{}, {}, {}]
        ---------
        @result: 添加行数
        """
        affect_count = None

        try:
            conn, cursor = self.get_connection()
            if auto_table:
                self.__create_table(cur=cursor, con=conn, ite=datas[0], table=table, primary_key=primary_key)
            affect_count = cursor.executemany(sql, datas)
            conn.commit()

        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
                """
                % (e, sql)
            )
        finally:
            self.close_connection(conn, cursor)

        return affect_count

    def insert_many(self, table, datas: List[Dict], primary_key: str = None, auto_table: bool = True, **kwargs):
        """
        批量添加数据, 直接传递list格式的数据，不用拼sql
        Args:
            table: 表名
            datas: 列表 [{}, {}, {}]
            **kwargs:

        Returns: 添加行数

        """
        sql, datas = tools.x_sql.make_batch_sql(table, datas, **kwargs)
        return self.add_batch(sql=sql, datas=datas, table=table, primary_key=primary_key, auto_table=auto_table)

    def update(self, sql):
        try:
            conn, cursor = self.get_connection()
            cursor.execute(sql)
            conn.commit()

        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
            """
                % (e, sql)
            )
            return False
        else:
            return True
        finally:
            self.close_connection(conn, cursor)

    def update_one(self, table, data: Dict, where):
        """
        更新, 不用拼sql
        Args:
            table: 表名
            data: 数据 {"xxx":"xxx"}
            where: 更新条件 where后面的条件，如 where='status=1'

        Returns: True / False

        """
        sql = tools.x_sql.make_update_sql(table, data, where)
        return self.update(sql)

    def delete(self, sql):
        """
        删除
        Args:
            sql:

        Returns: True / False

        """
        try:
            conn, cursor = self.get_connection()
            cursor.execute(sql)
            conn.commit()

        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
            """
                % (e, sql)
            )
            return False
        else:
            return True
        finally:
            self.close_connection(conn, cursor)

    def execute(self, sql):
        try:
            conn, cursor = self.get_connection()
            cursor.execute(sql)
            conn.commit()

        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
            """
                % (e, sql)
            )
            return False
        else:
            return True
        finally:
            self.close_connection(conn, cursor)


x_mysql = MysqlDB()
