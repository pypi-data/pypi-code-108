"""
Created on Wed Oct 30 09:42:55 2019
@author:
"""

import time

import pymysql
import pandas as pd

class SqlData():
    # 读取数据库数据
    db_youlian = pymysql.connect(  # 有播数据库
        host='rm-uf6szc0pdl707a0bhgo.mysql.rds.aliyuncs.com',
        user='youlian_data_ls',  # 数据库用户名
        password='pass@1234',  # 数据库密码
        database='youlian',
        charset='utf8',
        port=3306
    )
    
    # 读取数据库数据
    db_youboReadCnn = pymysql.connect(  # 有播数据库
        host='rm-uf68h8f6ot3q1h2hqio.mysql.rds.aliyuncs.com',
        user='lishuang',  # 数据库用户名
        password='pass@1234',  # 数据库密码
        database='youbo_new',
        charset='utf8',
        port=3306
    )

    # 读取数据库数据
    db_youboCnn = pymysql.connect(  # 有播数据库
        host='rm-uf68h8f6ot3q1h2hqio.mysql.rds.aliyuncs.com',
        user='youbo',  # 数据库用户名
        password='zV6b8NZAtBa64zE9K36tmmhW',  # 数据库密码
        database='youbo_new',
        charset='utf8',
        port=3306
    )

    # 读取数据库数据
    db_youbaoCnn = pymysql.connect(  # 有宝数据库
        host='rm-uf68h8f6ot3q1h2hqio.mysql.rds.aliyuncs.com',
        user='youbo',  # 数据库用户名
        password='zV6b8NZAtBa64zE9K36tmmhW',  # 数据库密码
        database='youbao',
        charset='utf8',
        port=3306
    )

    # # 读取数据库数据
    db_localCnn = pymysql.connect(  # 本地数据库
        host='114.215.203.26',
        user='bigmessage',  # 数据库用户名
        password='pass@1234',  # 数据库密码
        database='bigmessage',
        charset='utf8',
        port=3306
    )

    # 读取本地 数据库ai数据
    db_localCnn_ai = pymysql.connect(  # 本地数据库
        host='114.215.203.26',
        user='db_my_ai',  # 数据库用户名
        password='e63hTYYcsfhhtEEK',  # 数据库密码
        database='db_my_ai',
        charset='utf8',
        port=3306
    )

    # 读取自己本地数据库 ub 数据
    db_localCnn_ub = pymysql.connect(  # 本地数据库
        host='114.215.203.26',
        user='db_my_ub',  # 数据库用户名
        password='7drDHa3pYPJDPnCe',  # 数据库密码
        database='db_my_ub',
        charset='utf8',
        port=3306
    )

    def get_youliandata(self, sql_str):
        # 获取有播的数据库 的sql数据
        return pd.read_sql(sql_str, self.db_youlian).to_numpy().tolist()

    def get_youbodata(self, sql_str):
        # 获取有播的数据库 的sql数据
        list_info = pd.read_sql(sql_str, self.db_youboCnn).to_numpy().tolist()
        return list_info

    def go_youbao(self, sqlStr):
        # 获取有宝的数据库 的sql数据
        list_info = pd.read_sql(sqlStr, self.db_youbaoCnn).to_numpy().tolist()
        return list_info

    def git_local(self, sqlStr):
        # 获取本地数据库的sql数据
        list_info = pd.read_sql(sqlStr, self.db_localCnn).to_numpy().tolist()
        return list_info

    def get_query(self, cnn1, addSql, *data):
        # 获取数据
        cursor = cnn1.cursor()
        # sql = "update maoyan_movie set movie=%s where ranking=%s"
        # data = ('寂静之地', 1)
        cursor.execute(addSql, data)
        result = cursor.fetchall()  # fetchall 获取全部数据[[]],fetchone  获取第一条数据 []
        cnn1.commit()  # 提交，不然无法保存插入或者修改的数据
        cursor.close()  # 关闭游标
        return result

    def add_data(self, cnn1, add_sql, list_data):  # addSql 添加数据的数据库
        # 创建一个游标
        cursor = cnn1.cursor()
        # 插入数据
        # 数据直接写在sql后面
        # sql = "insert into yb_common_log(id,app_id,merchant_id,user_id,method,module,controller,action,url,get_data,post_data,header_data, ip,error_code,error_msg,error_data,req_id,user_agent,status,created_at , updated_at) values (%s,%s, %s, %s, %s,%s,%s, %s, %s, %s,%s,%s, %s, %s, %s,%s,%s, %s, %s, %s,%s)"  # 注意是%s,不是s%
        result = cursor.execute(add_sql, list_data)  # 列表格式数据
        cnn1.commit()  # 提交，不然无法保存插入或者修改的数据(这个一定不要忘记加上)
        cursor.close()  # 关闭游标
        return result

    def updata_sql(self, cnn1, updata_sql, list_data):
        cursor = cnn1.cursor()
        # 修改数据
        # sql = "update maoyan_movie set movie=%s where ranking=%s"
        # data = ('寂静之地', 1)
        cursor.execute(updata_sql, list_data)
        cnn1.commit()  # 提交，不然无法保存插入或者修改的数据
        cursor.close()  # 关闭游标

if __name__ == "__main__":
    # 示例代码

    pass
