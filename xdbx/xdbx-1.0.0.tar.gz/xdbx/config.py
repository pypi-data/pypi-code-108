# #!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2021/12/16 16:55
# @Author : BruceLong
# @FileName: config.py
# @Email   : 18656170559@163.com
# @Software: PyCharm
# @Blog ：http://www.cnblogs.com/yunlongaimeng/

import os

# ***************Elasticsearch配置-start*********************
ES_HOST_PORT_LIST = os.getenv("ES_HOST_PORT_LIST")

# ***************Elasticsearch配置-end*********************

# ***************Kafka配置-start*********************
KAFKA_HOST = os.getenv("KAFKA_HOST", '127.0.0.1')
KAFKA_PORT = os.getenv("KAFKA_PORT", '9092')
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
KAFKA_PARTITION = os.getenv("KAFKA_PARTITION")
# ***************Kafka配置-end*********************


# ***************mongo数据库配置-start*********************
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB")
MONGO_USERNAME = os.getenv("MONGO_USER_NAME")
MONGO_PASSWORD = os.getenv("MONGO_USER_PASS")
# ***************mongo数据库配置-end*********************

# ***************SqlServer数据库配置-start*********************
SQLSERVER_HOST = os.getenv("SQLSERVER_HOST", '127.0.0.1')
SQLSERVER_DB = os.getenv("SQLSERVER_DB")
SQLSERVER_USERNAME = os.getenv("SQLSERVER_USERNAME")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD")
# ***************SqlServer数据库配置-end*********************


# ***************MySQL数据库配置-start*********************
MYSQL_HOST = os.getenv("MYSQL_HOST", '127.0.0.1')
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
# ***************MySQL数据库配置-end*********************
