#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# $ pip3 install PyMySQL
# Collecting PyMySQL
#   Downloading PyMySQL-0.10.1-py2.py3-none-any.whl (47 kB)
#      |████████████████████████████████| 47 kB 1.9 kB/s
# Installing collected packages: PyMySQL
# Successfully installed PyMySQL-0.10.1

import pymysql
# 打开数据库连接
# db = pymysql.connect("localhost","testuser","test123","TESTDB")
db = pymysql.connect("10.84.234.28", "ccc_test_info", "ccc_test_info", "db_ccc_test_info", 5002)
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()
# 使用 execute()  方法执行 SQL 查询
intVar = cursor.execute("SELECT VERSION()")
print("返回{0}条数据".format(intVar))
# 使用 fetchone() 方法获取单条数据.
dbVersion = cursor.fetchone()
print("dbVersion = {0}".format(dbVersion))
print("Database version : %s " % dbVersion)
# 关闭数据库连接
db.close()

# 因上面已经close了数据库连接，所以若不重新建立连接就直接查询，则connection.py会报出pymysql.err.InterfaceError: (0, '')问题。
db = pymysql.connect("10.84.234.28", "ccc_test_info", "ccc_test_info", "db_ccc_test_info", 5002)
cursor = db.cursor()
# querySql = "SELECT * FROM test_env WHERE UID > %s" % ("3")
querySql = "SELECT * FROM test_env WHERE UID > 3"
intVar = cursor.execute(querySql)
print("返回{0}条数据".format(intVar))
tupleResult = cursor.fetchall()
for var in tupleResult:
    print("当前结果集元祖为：", var)
    print("结果集共{0}个字段".format(len(var)))
    print("结果集第一个字段值=", var[0])



