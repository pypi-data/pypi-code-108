from dbpoolpy.dbpool import acquire, release
from dbpoolpy.dbhelper import SelectHelper, InsertHelper, UpdateHelper, DeleteHelper

class TableBase():

    def __init__(self, db):
        self._db = db
        self._conn = None
        self.open_conn()

    def __enter__(self):
        return self

    def __exit__(self):
        ''' 退出时如果没有关闭，则关闭连接 '''
        self.close_conn()

    def __del__(self):
        ''' 变量回收时，关闭连接 '''
        self.close_conn()

    def close_conn(self):
        if self._conn:
            release(self._conn)
            self._conn = None

    def open_conn(self):
        if not self._conn:
            _conn = acquire(self._db)
            self._conn = _conn
            return _conn
        else:
            return self._conn

    def sql(self, cls, is_auto_close, fill_args):
        sql = cls.sql(self, fill_args)
        if is_auto_close:
            self.close_conn()
        return sql


class SelectTable(TableBase, SelectHelper):
    def __init__(self, db, table):
        TableBase.__init__(self, db)
        SelectHelper.__init__(self, dbo=self._conn, tables=table)

    def sql(self, is_auto_close=True, fill_args=True):
        return TableBase.sql(self, SelectHelper, is_auto_close, fill_args)

    def all(self, isdict=True):
        if not self._conn:
            self.open_conn()
        sql = self.sql(is_auto_close=False, fill_args=False)
        res = self._conn.query(sql, self._where_args or None, isdict=isdict)
        self.close_conn()
        return res

    def first(self, isdict=True):
        if not self._conn:
            self.open_conn()
        sql = self.sql(is_auto_close=False, fill_args=False)
        if sql.find('limit') == -1:
            sql += ' limit 1'
        res = self._conn.get(sql, self._where_args or None, isdict=isdict)
        self.close_conn()
        return res

class InsertTable(TableBase, InsertHelper):
    def __init__(self, db, table):
        TableBase.__init__(self, db)
        InsertHelper.__init__(self, dbo=self._conn, table=table)

    def sql(self, is_auto_close=True, fill_args=True):
        return TableBase.sql(self, InsertHelper, is_auto_close, fill_args)

    def execute(self):
        if not self._conn:
            self.open_conn()
        sql = self.sql(is_auto_close=False, fill_args=False)
        res = self._conn.execute_insert(sql, self._values_args or None)
        self.close_conn()
        return res

class UpdateTable(TableBase, UpdateHelper):
    def __init__(self, db, table):
        TableBase.__init__(self, db)
        UpdateHelper.__init__(self, dbo=self._conn, table=table)

    def sql(self, is_auto_close=True, fill_args=True):
        return TableBase.sql(self, UpdateHelper, is_auto_close, fill_args)

    def execute(self):
        if not self._conn:
            self.open_conn()
        sql = self.sql(is_auto_close=False, fill_args=False)
        args = self._values_args + self._where_args
        res = self._conn.execute(sql, args or None)
        self.close_conn()
        return res

class DeleteTable(TableBase, DeleteHelper):
    def __init__(self, db, table):
        TableBase.__init__(self, db)
        DeleteHelper.__init__(self, dbo=self._conn, table=table)

    def sql(self, is_auto_close=True, fill_args=True):
        return TableBase.sql(self, DeleteHelper, is_auto_close, fill_args)

    def execute(self):
        if not self._conn:
            self.open_conn()
        sql = self.sql(is_auto_close=False, fill_args=False)
        res = self._conn.execute(sql, self._where_args or None)
        self.close_conn()
        return res
