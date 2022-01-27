from py3db.log.Log import Log
from pymysql import connect


class MySql:
    def __init__(self, host, port, user_name, password, database, table=None):
        self.host = host
        self.user_name = user_name
        self.port = port
        self.password = password
        self.database = database
        self.db = None
        self.table_name = table
        self.sql_show = False
        self.log = Log("mysql.log")
        self.create_connect()
        self.results = []
        self.op_list = []

    # @classmethod
    # def table(cls, table_name):
    #     cls.table_name = table_name

    def query(self, sql):
        print(sql) if self.sql_show else None
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            self.log.call_error()
            self.log.error(str(e))

    def __str__(self) -> str:
        return "\n".join(["%s:%s" % item for item in self.__dict__.items()])

    def create_connect(self) -> None:
        try:
            self.db = connect(
                host=self.host,
                port=self.port,
                user=self.user_name,
                password=self.password,
                db=self.database,
                charset='utf8mb4'
            )
            if not self.db:
                self.log.call_error()
        except Exception as e:
            self.log.call_error()
            self.log.error(str(e))

    def close_connect(self):
        try:
            self.db.close()
        except Exception as e:
            self.log.call_error()
            self.log.error(str(e))

    def execute(self, sql, variable_name=None, variable=None):
        print(sql) if self.sql_show else None
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.log.call_error()
            self.log.error("{0} {1} {2}".format(
                e, variable_name, variable
            ))

    def insert_one(self, table=None, columns_list=[], columns_dict={}):
        if not columns_list:
            if not len(columns_dict):
                print('无对应数据')
                return
            else:
                columns_list = columns_dict.values()

        self.table_name = table if table else self.table_name
        value_str = "({})".format(
            ",".join(list(map(lambda x: f"'{x}'" if x is not None else "NULL", columns_list))))
        self.column_name_list = columns_dict.keys() if len(columns_dict) else []
        self.column_name_str = ",".join(self.column_name_list)
        self.column_name_str = f"({self.column_name_str})" if len(
            columns_dict) else ""
        self.op_list = [
            'insert',
            'into',
            self.table_name,
            self.column_name_str,
            'values',
            value_str
        ]
        sql = " ".join(self.op_list)
        self.execute(sql)

    def select(self, table=None, field_list=[], condition_dict={}):
        condition_list = []
        equal_str = "="
        condition_str = " and "
        field_sql = ",".join(field_list) if field_list else "*"
        self.table_name = table if table else self.table_name
        for key, item in condition_dict.items():
            item = item if item else "NULL"
            if isinstance(item, dict):
                equal_str = item.get('compare') if item.get(
                    'compare') else equal_str
                item = item.get('value')
            if item != "NULL":
                condition_list.append("`%s` %s '%s'" % (key, equal_str, item))
            else:
                equal_str = "is"
                condition_list.append("`%s` %s %s" % (key, equal_str, item))
            equal_str = "="
        condition_sql = "1=1" if condition_dict == {
        } else condition_str.join(condition_list)
        sql = "select %s from %s where %s" % (
            field_sql, self.table_name, condition_sql)
        return self.query(sql)

    def update(self, table=None, update_dict: dict = {}, condition_dict: dict = {}):
        update_list = []
        condition_list = []
        equal_str = "="
        self.table_name = table if table else self.table_name
        for key, item in update_dict.items():
            item = item if item else "NULL"
            update_list.append("%s='%s'" % (key, item))
        update_sql = ",".join(update_list)

        for key, item in condition_dict.items():
            item = item if item else "NULL"
            if isinstance(item, dict):
                equal_str = item.get('compare') if item.get(
                    'compare') else equal_str
                item = item.get('value')
            condition_list.append("`%s` %s '%s'" % (key, equal_str, item))
        condition_sql = "1=1" if condition_dict == {
        } else ",".join(condition_list)

        sql = "update {} set {} where {}".format(
            self.table_name, update_sql, condition_sql)
        self.execute(sql)

    def delete(self, table=None, condition_dict={}):
        condition_list = []
        equal_str = "="
        self.table_name = table if table else self.table_name
        for key, item in condition_dict.items():
            item = item if item else "NULL"
            if isinstance(item, dict):
                equal_str = item.get('compare') if item.get(
                    'compare') else equal_str
                item = item.get('value')
            condition_list.append("`%s` %s '%s'" % (key, equal_str, item))
        condition_sql = ",".join(condition_list) if len(
            condition_list) else "1 = 1"
        delete_sql = "delete from %s where %s" % (
            self.table_name, condition_sql)
        self.execute(delete_sql)

    def output_sql(self) -> None:
        self.sql_show = True

    def __del__(self):
        if not self.db and not self:
            self.db.close_connect()


if __name__ == "__main__":
    mysql = MySql("10.18.253.184", 9022, "urrfx4l",
                  "cY9UF6kgQ1mXtQnADi0hQ4UU3M2yUmWD", "crawler")

    mysql.output_sql()
    result = mysql.select("crawling_pub", condition_dict={"id": 895})
    print(result)
