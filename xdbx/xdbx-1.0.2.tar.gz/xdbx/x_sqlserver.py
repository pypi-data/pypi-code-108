# #!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2021/12/16 18:56
# @Author : BruceLong
# @FileName: x_sqlserver.py
# @Email   : 18656170559@163.com
# @Software: PyCharm
# @Blog ：http://www.cnblogs.com/yunlongaimeng/
import copy

import pymssql

from .config import SQLSERVER_HOST, SQLSERVER_USERNAME, SQLSERVER_PASSWORD, SQLSERVER_DB
from .x_single import SingletonType


class SqlServerPipeline(metaclass=SingletonType):
    '''
    SqlServer存储管道
    '''

    def __init__(self):
        '''
        初始化操作
        '''
        self.host = SQLSERVER_HOST
        self.username = SQLSERVER_USERNAME
        self.password = SQLSERVER_PASSWORD
        self.db = SQLSERVER_DB

    def __get_connect(self):
        '''
        创建连接信息
        :return:
        '''
        if not self.db:
            raise (NameError, "没有设置数据库信息")
        self.connect = pymssql.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.db,
            charset="utf8"
        )
        cursor = self.connect.cursor()
        if not cursor:
            raise (NameError, "连接数据库失败")
        else:
            return cursor

    def get_connect_test(self):
        return self.__get_connect()

    def __create_table(self, cur, ite: dict, table: str, primary_key: str = None):
        '''
        合建表相关的信息
        :param item: 数据
        :param table: 表名
        :return:
        '''
        # cur = self.__get_connect()
        # 判断是否存在该表
        item = copy.deepcopy(ite)
        sql = f'''SELECT * FROM sys.all_objects WHERE object_id = OBJECT_ID('{table}') AND type IN ('U')'''
        cur.execute(sql)
        if not cur.fetchone():
            # 生成创建字段信息
            # ------------目前只支持两种整型及字符串----------------------
            if primary_key:
                item.pop(primary_key)
            field_info = ',\n'.join(
                [
                    # f'{field} bigint' if isinstance(values, int) else f'{field} nvarchar(max)'
                    f'{field} nvarchar(max)'
                    for field, values in item.items()
                ]
            )
            sql_table = f'''create table {table}(
                    x_id bigint identity(1,1) PRIMARY KEY ,
                    x_inserttime datetime default getdate(),
                    x_updatetime datetime default getdate(),
                    {field_info},
                    )'''
            if primary_key:
                sql_table = f'''create table {table}(
                    x_id bigint identity,
                    x_inserttime datetime default getdate(),
                    x_updatetime datetime default getdate(),
                    {primary_key} nvarchar(255),
                    {field_info},
                    CONSTRAINT pk_{table}_x_id PRIMARY KEY CLUSTERED ({primary_key})
                    )'''
            # --创建update触发器
            sql_trigger = f'''
                    create trigger trig_{table}_updatetime
                    on {table}
                    after update
                    as
                    begin
                        update {table} set x_updatetime =getdate() WHERE x_ID IN (SELECT DISTINCT x_ID FROM inserted)
                    end'''
            try:
                # print(sql_table)
                cur.execute(sql_table)
                cur.execute(sql_trigger)
                self.connect.commit()
                print('Create Table Successful')
            except Exception as e:
                print('Create Table Failed', e)
        else:
            # 查询表字段
            select_fields_sql = f'''SELECT Name FROM SysColumns WHERE id=Object_Id('{table}')'''
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
                        f'{field} nvarchar(max)'
                        for field, values in item.items() if field.lower() in not_exists_fields
                    ]
                )
                add_fields_sql = f'''alter table {table} add {not_exists_fields_info}'''
                try:
                    # print(add_fields_sql)
                    cur.execute(add_fields_sql)
                    self.connect.commit()
                    print('Create Field Successful')
                except Exception as e:
                    print('Create Field Failed', e)

    def insert_one(self, item: dict, table: str, primary_key: str = None):
        '''
        插入一条数据
        :param item:
        :param table:
        :return:
        '''
        cur = self.__get_connect()
        self.__create_table(cur=cur, ite=item, table=table, primary_key=primary_key)
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
            cur.execute(sql, tuple(data))
            print('Insert One Successful')
            self.connect.commit()
        except Exception as e:
            print('Insert One Failed,', e)
            self.connect.rollback()
        finally:
            cur.close()
            self.connect.close()
        pass

    def insert_many(self, items: list, table: str, primary_key: str = None):
        '''
        批量插入数据
        :param items:
        :param table:
        :return:
        '''
        if not isinstance(items, list):
            raise (TypeError, 'please input items for list type')
        cur = self.__get_connect()
        k_temp = {k for ite in items for k in ite.keys()}
        v_temp = ['' for _ in range(len(k_temp))]
        data = dict(zip(k_temp, v_temp))
        self.__create_table(cur=cur, ite=data, table=table, primary_key=primary_key)
        values = ', '.join(['%s'] * len(data))
        # [[item.update({k: str(v)}) for k, v in item.items() if not isinstance(v, (int, str))] for item in items]
        result_data = [{k: str(item.get(k)) if item.get(k) else '' for k in data.keys()} for item in items]
        # print(result_data)
        keys = ', '.join(result_data[0].keys())
        datas = [tuple(i.values()) for i in result_data]
        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        try:
            cur.executemany(sql, datas)
            self.connect.commit()
            print('Insert Many Successful')
        except Exception as e:
            self.connect.rollback()
            print('Insert Many Failed:', e)
        finally:
            cur.close()
            self.connect.close()

    def find(self, sql: str):
        '''
        通过sql查询对应的数据结果
        :param sql: sql语句
        :return:
        '''
        cur = self.__get_connect()
        try:
            cur.execute(sql)
            desc = cur.description
            result = (dict(zip((d[0] for d in desc), data)) for data in cur.fetchall())
            return result
        except Exception as e:
            print('Find Data Failed:', e)
        finally:
            cur.close()
            self.connect.close()


x_mssql = SqlServerPipeline()
