#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
from collections import OrderedDict
from tqdm import tqdm
import pandas as pd
import numpy as np
import showlog
import pymysql
import time
import copy
import envx
silence_default = True


def make_con_info(
        env_file_name: str = 'mysql.env'
):
    # ---------------- 固定设置 ----------------
    inner_env = envx.read(file_name=env_file_name)
    con_info = {
        "host": inner_env['host'],
        "port": int(inner_env.get('port', '3306')),
        "username": inner_env.get('username', 'root'),
        "password": inner_env['password'],
        "charset": inner_env.get('charset', 'utf8'),
    }
    # ---------------- 固定设置 ----------------
    return con_info


def con_mysql(
        host: str,
        username: str,
        password: str,
        db_name: str = None,
        port: int = 3306,
        charset: str = 'utf8',
        ssc: bool = False
):
    """
    此函数为有提示信息的Mysql数据库连接函数的优化，内部预定义了连接的默认字符设置
    当连接失败时，将倒计时5秒后重连，直到连接成功
    此函数有运行提示
    :param host:
    :param db_name:
    :param username:
    :param password:
    :param port: 默认端口为3306
    :param charset: 默认字符集为utf8
    :param ssc: 默认不使用流式游标
    :return:(con, cur)
    """
    while True:
        try:
            showlog.info('User [%s] are trying to connect to the database [%s] ...' % (username, db_name))
            con = pymysql.connect(
                host=host,
                db=db_name,
                user=username,
                passwd=password,
                port=port,
                charset=charset
            )
            if ssc is False:
                cur = con.cursor()
            else:
                cur = pymysql.cursors.SSCursor(con)  # 使用流式游标
            cur.execute('SET NAMES utf8mb4')
            cur.execute('SET CHARACTER SET utf8mb4')
            cur.execute('SET character_set_connection=utf8mb4')
            showlog.info('ok! connection success.')
            return con, cur
        except:
            showlog.error('Oops, connection failed, Trying to reconnect in 5 seconds ...')
            time.sleep(5)


def con_mysql_silence(
        host: str,
        username: str,
        password: str,
        db_name: str = None,
        port: int = 3306,
        charset: str = 'utf8',
        ssc: bool = False
):
    """
    此函数为无提示信息的Mysql数据库连接函数的优化，内部预定义了连接的默认字符设置
    当连接失败时，将倒计时5秒后重连，直到连接成功
    此函数无运行提示
    :param host:
    :param db_name:
    :param username:
    :param password:
    :param port: 默认端口为3306
    :param charset: 默认字符集为utf8
    :param ssc: 默认不使用流式游标
    :return:(con, cur)
    """
    while True:
        try:
            con = pymysql.connect(
                host=host,
                db=db_name,
                user=username,
                passwd=password,
                port=port,
                charset=charset
            )
            if ssc is False:
                cur = con.cursor()
            else:
                cur = pymysql.cursors.SSCursor(con)  # 使用流式游标
            cur.execute('SET NAMES utf8mb4')
            cur.execute('SET CHARACTER SET utf8mb4')
            cur.execute('SET character_set_connection=utf8mb4')
            return con, cur
        except:
            time.sleep(5)


def con2db(
        con_info: dict,
        db_name: str = None,
        silence: bool = silence_default,  # 默认为非静默模式
        ssc: bool = False
):
    """
    对连接数据库的方法再次优化，此处可以定义所有数据库的连接
    :param con_info:设置连接的具体信息，必须包含：host、username、password，可选包含：port、charset
    :param db_name:设置需要连接的数据库
    :param silence:设置静默模式，为True表示静默，为False表示非静默
    :param ssc: 默认不使用流式游标
    :return:connection，由(con, cur)组成，所以返回的效果是(con, cur)
    """
    host = con_info.get("host")
    username = con_info.get("username")
    password = con_info.get("password")
    port = con_info.get("port", 3306)
    charset = con_info.get("charset", "utf8")
    if silence is True:
        connection = con_mysql_silence(
            host=host,
            db_name=db_name,
            username=username,
            password=password,
            port=port,
            charset=charset,
            ssc=ssc
        )
        return connection
    else:
        connection = con_mysql(
            host=host,
            db_name=db_name,
            username=username,
            password=password,
            port=port,
            charset=charset,
            ssc=ssc
        )
        return connection


def _query(
        sql: str,
        cur,
        con=None,
        parameter: tuple = None,
        operate: bool = False  # 是否为操作
):
    """
    查询结果以list(dict)形式输出
    :param sql:
    :param cur:
    :param con:
    :param parameter: 参数化查询语句避免SQL注入
    :param operate: 为True的时候执行操作（执行commit），为False的时候执行查询数据（不执行commit）
    :return:
    """
    try:
        if parameter is None:
            cur.execute(sql)
        else:
            cur.execute(sql, parameter)
        if operate is False:
            # 只查询
            index = cur.description
            result = list()
            for res in cur.fetchall():
                row = OrderedDict()
                for i in range(len(index)):
                    row[index[i][0]] = res[i]
                result.append(row)
            return result
        else:
            # 只操作
            effect_rows = cur.rowcount
            con.commit()
            return effect_rows
    except Exception as ex:
        showlog.warning("Oops! there is an error occurred in query:%s , sql: %s" % (ex, sql))
        return


def query_table_all_data(
        db_name: str,
        tb_name: str,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        order_col: str = None,  # 需要排序的列
        order_index: str = "DESC",  # 排序规则
        silence: bool = silence_default
):
    """
    查询某个表的所有数据
    查询结果以list(dict)形式输出
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        con, cur = con2db(
            con_info=con_info,
            db_name=db_name,
            silence=silence
        )
        if order_col is None:
            sql = "SELECT * FROM `?`.`?`"
            parameter = (db_name, tb_name)
        else:
            sql = "SELECT * FROM `?`.`?` ORDER BY `?` ?"
            parameter = (db_name, tb_name, order_col, order_index)
        if silence is True:
            try:
                res = _query(
                    cur=cur,
                    sql=sql,
                    parameter=parameter
                )
                return res
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
        else:
            showlog.info("Executing sql：%s ..." % sql)
            try:
                res = _query(
                    cur=cur,
                    sql=sql,
                    parameter=parameter
                )
                showlog.info("Executing sql success.")
                return res
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
    except Exception as ex:
        showlog.warning("Oops! an error occurred, maybe con2db error. Exception: %s" % ex)
        return


def query_by_sql(
        sql: str,  # 参数用?表示
        parameter: tuple = None,  # 参数化查询避免sql注入
        db_name: str = None,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default
):
    """
    按照sql查询
    查询结果以list(dict)形式输出
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        con, cur = con2db(
            con_info=con_info,
            db_name=db_name,
            silence=silence
        )
        if silence is True:
            try:
                res = _query(
                    cur=cur,
                    sql=sql,
                    parameter=parameter
                )
                return res
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
        else:
            showlog.info("Executing sql：%s ..." % sql)
            try:
                res = _query(
                    cur=cur,
                    sql=sql,
                    parameter=parameter
                )
                showlog.info("Executing sql success.")
                return res
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
    except Exception as ex:
        showlog.warning("Oops! an error occurred, maybe con2db error. Exception: %s" % ex)
        return


def do_by_sql(
        sql: str,
        parameter: tuple = None,  # 参数化查询避免sql注入
        db_name: str = None,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default
):
    """
    按照sql执行
    查询结果以list(dict)形式输出
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        con, cur = con2db(
            con_info=con_info,
            db_name=db_name,
            silence=silence
        )
        if silence is True:
            try:
                effect_rows = _query(
                    sql=sql,
                    parameter=parameter,
                    cur=cur,
                    con=con,
                    operate=True
                )
                return effect_rows
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
        else:
            showlog.info("Executing sql：%s ..." % sql)
            try:
                effect_rows = _query(
                    sql=sql,
                    parameter=parameter,
                    cur=cur,
                    con=con,
                    operate=True
                )
                showlog.info("Executing sql success.")
                return effect_rows
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
    except Exception as ex:
        showlog.warning("Oops! an error occurred, maybe con2db error. Exception: %s" % ex)
        return


def data_bases(
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default
):
    """
    获取MySQL的连接权限范围内的所有db列表
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        con, cur = con2db(
            con_info=con_info,
            silence=silence
        )
        sql = "SHOW DATABASES;"
        if silence is True:
            try:
                res = _query(
                    cur=cur,
                    sql=sql
                )
                inner_db_list = list()
                for each in res:
                    for k, v in each.items():
                        inner_db_list.append(v)
                return inner_db_list
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
        else:
            showlog.info("Executing sql：%s ..." % sql)
            try:
                res = _query(
                    cur=cur,
                    sql=sql
                )
                showlog.info("Executing sql success.")
                inner_db_list = list()
                for each in res:
                    for k, v in each.items():
                        inner_db_list.append(v)
                return inner_db_list
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
    except Exception as ex:
        showlog.warning("Oops! an error occurred, maybe con2db error. Exception: %s" % ex)
        return


def tables(
        db_name: str = None,  # 指定数据库，若不指定，将获取所有
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default
):
    """
        获取所有表，若不指定db_name，将获取所有
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        con, cur = con2db(
            con_info=con_info,
            db_name=db_name,
            silence=silence
        )
        sql = "SHOW TABLES;"
        if silence is True:
            try:
                res = _query(
                    cur=cur,
                    sql=sql
                )
                table_list = list()
                for each in res:
                    for k, v in each.items():
                        table_list.append(v)
                return table_list
            except:
                return
        else:
            showlog.info("Executing sql：%s ..." % sql)
            try:
                res = _query(
                    cur=cur,
                    sql=sql
                )
                showlog.info("Executing sql success.")
                table_list = list()
                for each in res:
                    for k, v in each.items():
                        table_list.append(v)
                return table_list
            except Exception as ex:
                showlog.warning("Oops! an error occurred, maybe query error. Exception: %s" % ex)
                return
    except Exception as ex:
        showlog.warning("Oops! an error occurred, maybe con2db error. Exception: %s" % ex)
        return


def tb_info(
        db_name: str,
        table_name: str,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default
):
    """
    输出表信息，其中：
    COLUMN_NAME：列名
    DATA_TYPE：数据类型
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    where_string = "TABLE_SCHEMA='%s' and TABLE_NAME='%s'" % (db_name, table_name)
    sql = "SELECT * FROM `information_schema`.`COLUMNS` WHERE %s" % where_string
    res = query_by_sql(
        sql=sql,
        silence=silence,
        con_info=con_info
    )
    return res


def column_list(
        db_name: str,
        tb_name: str,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default
):
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        con, cur = con2db(
            con_info=con_info,
            db_name=db_name,
            silence=silence
        )
        sql1 = """
        SELECT
            `COLUMN_NAME` 
        FROM
            `information_schema`.`COLUMNS` 
        WHERE
            `TABLE_SCHEMA` = '?' 
            AND `TABLE_NAME` = '?';
        """
        all_col_dict = _query(
            cur=cur,
            sql=sql1,
            parameter=(db_name, tb_name)
        )
        all_col_list = list()
        for each in all_col_dict:
            all_col_list.append(each.get("COLUMN_NAME"))
        sql2 = """
        SELECT
            `COLUMN_NAME` 
        FROM
            `information_schema`.`KEY_COLUMN_USAGE` 
        WHERE
            `TABLE_SCHEMA` = '?' 
            AND `TABLE_NAME` = '?'
        """
        pk_col_dict = _query(
            cur=cur,
            sql=sql2,
            parameter=(db_name, tb_name)
        )
        pk_col_list = list()
        for each in pk_col_dict:
            pk_col_list.append(each.get("COLUMN_NAME"))
        data_col_list = all_col_list.copy()
        for each in pk_col_list:
            try:
                data_col_list.remove(each)
            except:
                pass
        return all_col_list, pk_col_list, data_col_list
    except Exception as ex:
        showlog.warning("Oops! an error occurred in column_list, Exception: %s" % ex)
        return


def query_to_pd(
        sql: str,
        parameter=None,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default
):
    """
    针对数据量较大的情况，将数据存储到pd中
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        con, cur = con2db(
            con_info=con_info,
            silence=silence
        )
        if parameter is None:
            cur.execute(sql)
        else:
            cur.execute(sql, parameter)
        index = cur.description
        columns = list()
        for each in index:
            columns.append(each[0])
        result = list()
        p_bar = tqdm(cur.fetchall())
        for res in p_bar:
            p_bar.set_description_str("==> Downloading data")
            row = dict()
            for i in range(len(index)):
                row[index[i][0]] = res[i]
            result.append(row)
        return pd.DataFrame(result)
    except:
        showlog.warning("Oops! an error occurred in query, sql: %s" % sql)
        return


def information_schema(
        db_name: str,
        table_name: str,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default
):
    """
    输出表信息，其中：
    COLUMN_NAME：列名
    DATA_TYPE：数据类型
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    where_string = "TABLE_SCHEMA='%s' and TABLE_NAME='%s'" % (db_name, table_name)
    sql = "SELECT * FROM `information_schema`.`COLUMNS` WHERE %s;" % where_string
    res = query_by_sql(
        sql=sql,
        con_info=con_info,
        silence=silence
    )
    return res


def clean_data(
        data_dict_list: list,
        column_info_dict: dict,
        db_name: str,
        tb_name: str,
        replace_space_to_none: bool = True  # 自动将空值null改为None
):
    """
    功能性模块
    格式化数据
    """
    data_dict_list_temp = copy.deepcopy(data_dict_list)  # 深度拷贝，不更改源数据
    all_col_list = column_info_dict.get('all_col_list')  # 所有列名

    # 按照目标表的结构格式化data_dict_list，去除额外列的数据，只保留预设列的数据
    # step1: 清洗数据
    operate_param_set = set()
    for each_data_dict in data_dict_list_temp:  # 遍历数据list里的所有dict
        each_data_dict_copy = copy.deepcopy(each_data_dict)
        for each_key, each_value in each_data_dict_copy.items():  # 遍历单个dict的所有的key
            if each_key in all_col_list:  # 若key在all_col_list中，则收集该key，否则将删除key以及对应的数据，最终得到需要插入数据的列名列表
                operate_param_set.add(each_key)
            else:
                del each_data_dict[each_key]

    # step2: 生成操作语句模板
    operate_param_list = list(operate_param_set)  # 生成插入参数list
    operate_clause_tuple = "`,`".join(operate_param_list)
    insert_data_arg_list = list()
    for _ in operate_param_list:
        insert_data_arg_list.append("%s")
    data_tuple = ",".join(insert_data_arg_list)
    # 生成插入语句模板
    operate_clause = 'REPLACE INTO `%s`.`%s`(`%s`) VALUES(%s)' % \
                     (db_name, tb_name, operate_clause_tuple, data_tuple)

    # step3:
    # 生成插入数据tuple
    data_list = list()
    for each_data_dict in data_dict_list_temp:
        each_data_list = list()
        for each_data_key in operate_param_list:
            temp_data = each_data_dict.get(each_data_key)
            if temp_data == "":
                if replace_space_to_none is True:
                    each_data_list.append(None)
                else:
                    each_data_list.append("")
            else:
                if isinstance(temp_data, np.int64) is True:
                    each_data_list.append(str(temp_data))  # 将Int64转换为str
                else:
                    each_data_list.append(temp_data)
        data_list.append(tuple(each_data_list))  # 转换为tuple确保不变
    data_list_single = list(set(data_list))  # set去重
    return operate_clause, data_list_single


def replace_into(
        data_dict_list: list,  # 数据[{},{}]
        db_name: str,  # 数据库名
        tb_name: str,  # 表名
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        pk_col_list: list = None,  # 主键列表
        silence: bool = silence_default
):
    """
    插入和自动更新，注意，这里的更新是先对原来的数据删除，再插入，不适用于局部更新！
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    if data_dict_list is None or len(data_dict_list) == 0:
        return True
    else:
        try:
            column_info = column_list(
                db_name=db_name,
                tb_name=tb_name,
                con_info=con_info,
                silence=silence
            )  # 获取列名信息
            if column_info is not None:  # 若未获取到列名信息，提示错误并退出
                all_col_list, pk_col_list_get, data_col_list = column_info  # 获取到列名信息
                column_info_dict = {
                    'all_col_list': all_col_list,
                    'data_col_list': data_col_list,
                }
                if pk_col_list is not None:
                    column_info_dict['pk_col_list'] = pk_col_list  # 使用自定义主键列表
                else:
                    column_info_dict['pk_col_list'] = pk_col_list_get  # 使用数据库中定义的主键列表

                operate_clause, data_list_single = clean_data(
                    column_info_dict=column_info_dict,
                    data_dict_list=data_dict_list,
                    db_name=db_name,
                    tb_name=tb_name
                )
                connection = con2db(
                    con_info=con_info,
                    db_name=db_name,
                    silence=silence
                )  # 连接数据库
                if connection is not None:
                    con, cur = connection
                    try:
                        if silence is False:
                            showlog.info('operating %s data...' % len(data_list_single))
                        else:
                            pass
                        cur.executemany(operate_clause, list(data_list_single))
                        con.commit()
                        if silence is False:
                            showlog.info("operate success.")
                        else:
                            pass
                        return True
                    except:
                        if silence is False:
                            showlog.error("operate failure.operate_clause: %s" % operate_clause)
                            print(operate_clause, list(data_list_single)[0])
                        else:
                            pass
                        return False
                else:
                    if silence is False:
                        showlog.warning("Oops! can't get connection.")
                    else:
                        pass
                    return False
            else:
                if silence is False:
                    showlog.warning("Oops! can't get column_info.")
                else:
                    pass
                return False
        except:
            if silence is False:
                showlog.error("Oops! an error occurred!")
            else:
                pass
            return False


def insert(
        data_dict_list: list,
        db_name: str,
        tb_name: str,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        replace_space_to_none: bool = True,  # 自动将空值null改为None
        silence: bool = silence_default
):
    """
    此模块的功能是插入和自动更新
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        # 获取列名信息
        column_info = column_list(
            db_name=db_name,
            tb_name=tb_name,
            con_info=con_info,
            silence=silence
        )
        if column_info is not None:  # 若未获取到列名信息，提示错误并退出
            all_col_list, pk_col_list, data_col_list = column_info  # 获取到列名信息
            connection = con2db(
                con_info=con_info,
                db_name=db_name,
                silence=silence
            )  # 连接数据库
            if connection is not None:
                con, cur = connection
                # 按照目标表的结构格式化data_dict_list，去除额外列的数据，只保留预设列的数据
                insert_param_set = set()
                for each_data_dict in data_dict_list:  # 遍历数据list里的所有dict
                    each_data_dict_in = each_data_dict.copy()  # 复制一份避免发生更改dict的错误
                    for each in each_data_dict_in:  # 遍历单个dict的所有的key
                        if each in all_col_list:  # 若key在all_col_list中，则收集该key，否则将删除key以及对应的数据，最终得到需要插入数据的列名列表
                            insert_param_set.add(each)
                        else:
                            del each_data_dict[each]

                insert_param_list = list(insert_param_set)  # 生成插入参数list
                insert_clause_tuple = "`,`".join(insert_param_list)
                insert_data_arg_list = list()
                for _ in insert_param_list:
                    insert_data_arg_list.append("%s")
                insert_data_tuple = ",".join(insert_data_arg_list)
                # 生成插入语句模板
                insert_clause = 'INSERT INTO `%s`.`%s`(`%s`) VALUES(%s)' % \
                                (db_name, tb_name, insert_clause_tuple, insert_data_tuple)

                # 生成插入数据tuple
                insert_data_list = list()
                for each_data_dict in data_dict_list:
                    each_insert_data_list = list()
                    for each_data_key in insert_param_list:
                        if each_data_dict.get(each_data_key) == "":
                            if replace_space_to_none is True:
                                each_insert_data_list.append(None)
                            else:
                                each_insert_data_list.append("")
                        else:
                            each_insert_data_list.append(each_data_dict.get(each_data_key))
                    insert_data_list.append(tuple(each_insert_data_list))

                insert_data_list = set(insert_data_list)  # set去重

                try:
                    if silence is False:
                        showlog.info('Inserting %s data...' % len(insert_data_list))
                    else:
                        pass
                    cur.executemany(insert_clause, list(insert_data_list))
                    con.commit()
                    if silence is False:
                        showlog.info("Insert success.")
                    else:
                        pass
                    return True
                except:
                    if silence is False:
                        showlog.error("Insert failure.insert_clause: %s" % insert_clause)
                        print(insert_clause, list(insert_data_list)[0])
                    else:
                        pass
                    return False
            else:
                if silence is False:
                    showlog.warning("Oops! can't get connection.")
                else:
                    pass
                return False
        else:
            if silence is False:
                showlog.warning("Oops! can't get column_info.")
            else:
                pass
            return False
    except:
        if silence is False:
            showlog.error("Oops! an error occurred!")
        else:
            return False


def update(
        data_dict_list: list,
        db_name: str,
        tb_name: str,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'mysql.env',
        silence: bool = silence_default,
):
    """
    针对MySQL的数据批量更新方法，不考虑data_dict_list为空或者无数据的情况，仅仅能批量更新，默认where条件是表格的主键，且空值不参与
    先连接目标数据库获取到目标表的结构信息
    :param silence:设置上传的时候是否有提示信息
    :param con_info:连接信息
    :param env_file_name:设置连接数据库的信息
    :param db_name:需要上传到的目标数据库名称
    :param tb_name:需要上传到的目标数据表名称
    :param data_dict_list:需要上传的数据列表
    :return:
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    try:
        # 获取列名信息
        column_info = column_list(
            db_name=db_name,
            tb_name=tb_name,
            con_info=con_info,
            silence=silence
        )
        if column_info is not None:  # 若未获取到列名信息，提示错误并推出
            all_col_list, pk_col_list, data_col_list = column_info  # 获取到列名信息
            connection = con2db(
                con_info=con_info,
                db_name=db_name,
                silence=silence
            )  # 连接数据库
            if connection is not None:
                con, cur = connection
                # 按照目标表的结构格式化data_dict_list，去除额外列的数据，只保留预设列的数据
                try:
                    for each_data_dict in data_dict_list:  # 遍历数据list里的所有dict

                        set_clause_list = list()  # set语句列表
                        for each in each_data_dict:  # 遍历单个dict的所有的key
                            if each in data_col_list:  # 若key在all_col_list中，则收集该key，否则将删除key以及对应的数据，最终得到需要更新的列名列表
                                if each_data_dict.get(each) == "" or each_data_dict.get(each) is None:
                                    set_clause = "`%s`=%s" % (each, "NULL")
                                else:
                                    if isinstance(each_data_dict.get(each), str):
                                        # 这里将'替换为''是为了转义'，规避字符出含'报错
                                        set_clause = "`%s`='%s'" % (each, each_data_dict.get(each).replace("'", "''"))
                                    else:
                                        set_clause = "`%s`=%s" % (each, each_data_dict.get(each))
                                set_clause_list.append(set_clause)
                            else:
                                pass
                        set_string = " , ".join(set_clause_list)  # 生成set语句完成

                        # 所有数据的key遍历完成，将开始生成更新的where语句，where条件根据主键列生成
                        where_clause_list = list()
                        for each in pk_col_list:  # 遍历所有主键列
                            if each_data_dict.get(each) == "" or each_data_dict.get(each) is None:
                                pass
                            else:
                                if isinstance(each_data_dict.get(each), str):
                                    # 这里将'替换为''是为了转义'，规避字符出含'报错
                                    where_clause = "`%s`='%s'" % (each, each_data_dict.get(each).replace("'", "''"))
                                else:
                                    where_clause = "`%s`=%s" % (each, each_data_dict.get(each))
                                where_clause_list.append(where_clause)
                        where_string = " AND ".join(where_clause_list)  # 生成where语句完成

                        # where_string生成完成
                        update_clause = 'UPDATE `%s`.`%s` SET %s WHERE %s' % \
                                        (db_name, tb_name, set_string, where_string)
                        # print(update_clause)
                        cur.execute(update_clause)
                    con.commit()
                    return 1
                except:
                    if silence is False:
                        showlog.error("Update failure with update_clause: %s" % update_clause)
                    else:
                        return
            else:
                if silence is False:
                    showlog.warning("Oops! can't get connection.")
                else:
                    return
        else:
            if silence is False:
                showlog.warning("Oops! can't get column_info.")
            else:
                return
    except:
        if silence is False:
            showlog.error("Oops! an error occurred!")
        else:
            return
