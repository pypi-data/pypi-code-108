import pymysql

from autoTestScheme.common import logger


class MySql(object):
    database_kwargs = {}

    def __init__(self):
        pass

    def excute(self, sql_str, is_excute=False, is_logger=True):
        """
        执行sql语句
        :param sql_str: 执行命令
        :param is_excute: 是否为执行语句
        :param is_logger: 是否打印日志
        :return:
        """
        result = []
        self.sql = pymysql.Connect(charset='utf8', **self.database_kwargs, read_timeout=300)
        cursor = self.sql.cursor()
        if is_logger is True:
            logger.debug("执行sql命令({}:{}):{}".format(self.database_kwargs['host'], self.database_kwargs['port'], sql_str))
        cursor.execute(sql_str)
        if is_excute is False:
            result = self.sql_fetch_json(cursor)
        else:
            self.sql.commit()
        cursor.close()
        if is_logger is True:
            logger.debug(result)
        self.sql.close()
        return result

    def select_database(self, db):
        self.sql.select_db(db)
        logger.debug("切换数据库:{}".format(db))

    def connect(self, database_kwargs):
        """
        连接数据库
        :param database_kwargs: 数据库参数，字典，包含但不限于 host，port，user，password，database
        :return:
        """
        self.database_kwargs = database_kwargs
        # self.sql = pymysql.Connect(charset='utf8', **self.database_kwargs, read_timeout=300)

    def close(self):
        """
        关闭连接
        :return:
        """
        # self.sql.close()
        ...

    def sql_fetch_json(self, cursor: pymysql.cursors.Cursor):
        """
            将cursors的执行结果转换为字典
        """
        keys = []
        for column in cursor.description:
            keys.append(column[0])
        key_number = len(keys)
        json_data = []
        for row in cursor.fetchall():
            item = dict()
            for q in range(key_number):
                item[keys[q]] = row[q]
            json_data.append(item)
        return json_data


