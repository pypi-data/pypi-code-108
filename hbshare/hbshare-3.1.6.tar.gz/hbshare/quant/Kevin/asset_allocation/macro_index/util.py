from sqlalchemy import create_engine
import pymysql


def create_table(table_name, sql_script):
    db = pymysql.connect(host='192.168.223.152', user='admin', password='mysql', database='riskmodel')
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS {}".format(table_name))

    try:
        cursor.execute(sql_script)
        db.commit()
        print("创建数据库成功!")
    except Exception as e:
        print("创建数据库失败: case {}".format(e))

    finally:
        cursor.close()
        db.close()


def delete_duplicate_records(sql_script):
    db = pymysql.connect(host='192.168.223.152', user='admin', password='mysql', database='riskmodel')
    cursor = db.cursor()

    try:
        cursor.execute(sql_script)
        db.commit()
        print("删除重复数据成功！")
    except Exception as e:
        print("删除重复数据失败: case {}".format(e))

    finally:
        cursor.close()
        db.close()


class WriteToDB:
    def __init__(self):
        self.engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
            'admin', 'mysql', '192.168.223.152', '3306', 'riskmodel'))

    def write_to_db(self, df, table_name):
        df.to_sql(table_name, self.engine, index=False, if_exists='append')
