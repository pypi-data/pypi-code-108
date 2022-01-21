# 功能：简单连接或关闭db
############################################################################################################
## mysql
## pip install pymysql==0.10.1

import pymysql
def mysql_connect(mysql_info):
    """[连接mysql]

    Args:
        mysql_info ([dict]): 包含连接mysql数据库的基础信息

    Returns:
        mysql_obj ([tuple]): (mysql_conn mysql连接, mysql_cursor mysql游标)  
    """
    try:
        conn = pymysql.connect(
            host=mysql_info['host'], 
            port=mysql_info['port'],
            user=mysql_info['user'],
            password=mysql_info['password'],
            database=mysql_info['database'],
            charset='utf8'
        )
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor) 
        return (conn, cursor)

    except Exception as err:
        print(err)
        raise Exception(err)


def mysql_close(mysql_obj=()):
    """[主动关闭mysql连接]

    Args:
        mysql_obj ([tuple]): mysql_obj[0] mysql连接对象
                             mysql_obj[1] mysql游标对象

    Returns:
        [None]: 
    """
    try:
        mysql_obj[1].close()    # 先关闭游标
        mysql_obj[0].close()    # 再关闭连接

    except Exception as err:
        print(err)
        raise Exception(err)


############################################################################################################
## redis
## pip install redis==2.10.6

import redis
def redis_connect(redis_info):
    """[连接mysql]

    Args:
        redis_info ([dict]): 包含连接mysql数据库的基础信息

    Returns:
        conn ([class]): redis连接
    """
    try:
        conn = redis.Redis(
            host=redis_info['host'], 
            port=redis_info['port'], 
            db=redis_info['db'], 
            password=redis_info['password'], 
            decode_responses=True
        )
        return conn

    except Exception as err:
        print(err)
        raise Exception(err)



