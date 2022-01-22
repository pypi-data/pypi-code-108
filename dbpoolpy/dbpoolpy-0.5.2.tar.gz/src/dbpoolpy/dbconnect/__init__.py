# ConnectionBase

import time
from contextlib import contextmanager

class DBConnection():
    dbtype = ""

    def __init__(self, name, engine, lasttime, status, role='master', *args, **kwargs):
        self._name = name                       # 连接池名称
        self._engine = engine                   # 数据库连接引擎，满足DB API 2.0规范
        self._args, self._kwargs = args, kwargs # 数据库连接所传参数
        self._conn = None                       # 连接存储位置
        self._status = status                   # 连接状态
        self._lasttime = lasttime               # 连接创建时间
        self._server_id = None                  # 服务唯一id
        self._conn_id = 0                       # 连接唯一id
        self._transaction = False               # 是否正在执行事务
        self._role = role                       # 服务器在集群中的角色
        self.connect()

    def __str__(self):
        return '<%s %s:%d %s@%s>' % (
            self.dbtype,
            self._kwargs.get('host', ''),
            self._kwargs.get('port', 0),
            self._kwargs.get('user', ''),
            self._kwargs.get('database', 0)
        )

    def connect(self):
        self._conn = self._engine.connect(*self._args, **self._kwargs)
        self._transaction = False
        self._server_id = 0
        self._conn_id = 0
        print('server=%s|func=connect|id=%d|name=%s|user=%s|role=%s|addr=%s:%d|db=%s' % (
                 self.dbtype,
                 self._conn_id % 10000,
                 self._name,
                 self._kwargs.get('user', ''),
                 self._role,
                 self._kwargs.get('host', ''),
                 self._kwargs.get('port', 0),
                 self._kwargs.get('database', '')))

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def close(self):
        print('server=%s|func=close|id=%d' % (self.dbtype, self._conn_id % 10000))
        self._conn.close()
        self._conn = None

    def reconnect(self):
        '''重新连接'''
        try:
            self.close()
        except:
            pass
        self.connect()
    
    def begin(self):
        self._transaction = True

    def commit(self):
        self._transaction = False
        self._conn.commit()

    def rollback(self):
        self._transaction = False
        self._conn.rollback()

    def cancel(self):
        cancel = self._conn.cancel
        cancel()

    def ping(self, *args, **kwargs):
        return self._conn.ping(*args, **kwargs)

    def escape(self, s):
        return self._conn.escape_string(s)

    def is_available(self):
        return self._status == 0

    def useit(self):
        self._status = 1
        self._lasttime = time.time()

    def releaseit(self):
        self._status = 0

    def alive(self):
        pass

    def last_insert_id(self):
        pass

    @contextmanager
    def connect_cur(self):
        cur = None
        try:
            cur = self.cursor()
            yield cur
            if not self._transaction:
                self.commit()
        except Exception as e:
            if not self._transaction:
                self.rollback()
            raise e
        finally:
            if cur is not None:
                cur.close()

    @contextmanager
    def transaction(self):
        if self._transaction:
            raise Exception('this connect is transaction now')
        self.begin()
        try:
            yield self
            self.commit()
        except Exception as e:
            self.rollback()
            raise e