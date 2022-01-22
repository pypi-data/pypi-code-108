import abc
from math import ceil
import datetime
from collections import namedtuple
from dbpoolpy.utils import timesql
from dbpoolpy import pager
from contextlib import contextmanager
from dbpoolpy.config import settings
from dbpoolpy.constants import DBTYPE
from typing import Union, List, Tuple, Dict

Page = namedtuple("Page", ["total", "pages", "page", "size", "data"])

class Base:

    def field2sql(self, field:str):
        ''' 字段名解析
        情况:'id','a.id','id as i', 'a.id as ai'
        '''
        # return '%s' % field.strip().replace('.', '.').replace(' as ', ' as ')
        return field

    def fields2sql(self, fields:Union[str, List[str], Tuple[str]]):
        ''' 解析fields
        情况: 'id, a.name, imlf.phone as ip',
              ['id', 'a.name', 'imlf.phone as ip'],
              ('id', 'a.name', 'imlf.phone as ip')
        '''
        # if isinstance(fields, str):
        #     fields = fields.strip()
        #     if fields == '*':
        #         return fields
        #     fields = fields.split(',')
        # return ','.join([self.field2sql(field) for field in fields])
        if isinstance(fields, str):
            return fields
        else:
            return ','.join(list(fields))


    def table2sql(self, table:str):
        ''' 字段名解析
        情况:'graphs','imlf.graphs','graphs as g', 'imlf.graphs as ig'
        '''
        return '%s' % table.strip().replace('.', '.').replace(' as ', ' as ')

    def tables2sql(self, tables:Union[str, List[str], Tuple[str]]):
        ''' 解析tables
        情况: 'graphs, imlf.nodes, imlf.graphs as ig',
               ['graphs', 'imlf.nodes', 'imlf.graphs as ig'],
               ('graphs', 'imlf.nodes', 'imlf.graphs as ig')
        '''
        if isinstance(tables, str):
            tables = tables.split(',')
        return ','.join([self.table2sql(table) for table in tables])

    def key2sql(self, k:str) -> str:
        ''' where中的key转sql语句
        情况: 'name', 'a.name'
        '''
        return '%s' % k.strip().replace('.', '.')

    def value2sql(self, v):
        ''' where中value为非tuple时
        情况: 'value', 'value "name"'
        '''
        if isinstance(v, str):
            return "'%s'" % self._dbo.escape(v)
        elif isinstance(v, (int, float)):
            return str(v)
        elif v == None:
            return 'NULL'
        else:
            return "'%s'" % str(v)

    def append_where_args(self, v):
        ''' 添加where_args值 '''
        self._where_args.append(v)
        return "%s"

    def append_values_args(self, v):
        ''' 添加values_args的值 '''
        self._values_args.append(v)
        return "%s"

    def where_value_tuple2sql(self, v:tuple) -> str:
        ''' where中value为tuple时
        情况: ('in', ['12', 1])
              ('not in', ['12', 1])
              ('between', ['time1', 'time2'])
              ('like', '%time1%')
              ('like', 'time1%')
        '''
        assert len(v) == 2
        op, item = v
        assert isinstance(op, str)
        op = op.strip()
        if op.endswith('in'):
            assert isinstance(item, (list, tuple))
            self._where_args.append(item)
            return op + ' %s'
        elif op == 'between':
            assert isinstance(item, (list, tuple)) and len(item) == 2
            self._where_args.append(item[0])
            self._where_args.append(item[1])
            return op + ' %s and %s'
        else:
            self._where_args.append(item)
            return op + ' %s'

    def where2sql(self, where:dict):
        '''where值解析'''
        kv = lambda k,v: self.key2sql(k)+' '+self.where_value_tuple2sql(v) \
            if isinstance(v, tuple) else self.key2sql(k)+'='+self.append_where_args(v)
        return ' and '.join([kv(k, v) for k, v in where.items()])

    def on2sql(self, where:Dict[str, str]):
        '''where值解析'''
        kv = lambda k,v: self.key2sql(k)+'='+self.key2sql(v)
        return ' and '.join([kv(k, v) for k, v in where.items()])

    def values2sql(self, values:dict):
        '''values值解析'''
        kv = lambda k, v:self.key2sql(k)+'='+self.append_values_args(v)
        return ','.join([kv(k, v) for k, v in values.items()])

    def other2sql(self, other:Union[tuple, str]):
        if isinstance(other, str):
            return other
        else:
            assert len(other) == 2
            op, item = other
            assert isinstance(op, str)
            op = op.strip()
            if op.endswith('limit'):
                if isinstance(item, int):
                    return op + ' %s' % item
                else:
                    assert isinstance(item, (list, tuple, set)) and len(item) == 2
                    return op+' %s,%s' % (tuple(item))
            elif op == 'order by':
                if isinstance(item, str):
                    return op+' %s' % self.key2sql(item)
                else:
                    assert isinstance(item, (list, tuple, set)) and len(item) == 2
                    assert item[-1] in ['asc', 'desc']
                    return op+ ' %s %s' % (self.key2sql(item[0]), item[1])
            elif op == 'group by':
                if isinstance(item, str):
                    return op+' %s' % self.key2sql(item)
                else:
                    assert isinstance(item, (list, tuple, set))
                    return op+' %s' % ','.join([self.key2sql(i) for i in item])
            elif op == 'sql':
                assert isinstance(item, str)
                return item

    def values2insert(self, values:dict) -> str:
        '''insert中的values转sql'''
        keys = list(values.keys())
        return '(%s) values (%s)' % (
            ','.join([self.key2sql(k) for k in keys]),
            ','.join([self.append_values_args(values[k]) for k in keys])
        )

    def valueslist2insert(self, values_list:List[dict]) -> str:
        '''批量insert转sql'''
        keys = list(values_list[0].keys())
        return '(%s) values (%s)' % (
            ','.join([self.key2sql(k) for k in keys]),
            '),('.join(
                [','.join([self.append_values_args(values[k]) for k in keys]) for values in values_list]
            )
        )

class WhereMixin:
    def where(self, **kwargs):
        self._where = kwargs
        return self

class ValuesMixin:
    def values(self, **kwargs):
        self._values = kwargs
        return self

class OtherMixin:
    def other(self, other):
        self._other = other
        return self


class SelectHelper(Base, WhereMixin, OtherMixin):
    def __init__(
        self,
        dbo,
        tables,
        fields='*',
        join_type='inner',
        join_table=None,
        on=None,
        where=None,
        where_args=None,
        group_by=None,
        order_by=None,
        limit=None,
        other=None):
        self._dbo = dbo
        self._tables = tables
        self._fields = fields
        self._join_type = join_type
        self._join_table = join_table
        self._on = on
        self._where = where
        self._where_args = where_args or list()
        self._group_by = group_by
        self._order_by = order_by
        self._limit = limit
        self._other = other


    def sql(self, fill_args=True):
        sql = "select %s from %s" % (
            self.fields2sql(self._fields),
            self.tables2sql(self._tables)
        )
        if self._join_table and self._on:
            sql += " %s join %s on %s" % (
                self._join_type,
                self.table2sql(self._join_table),
                self.on2sql(self._on)
            )
        if self._where:
            sql += " where %s" % self.where2sql(self._where)
        if self._group_by:
            sql += " group by %s" % self.fields2sql(self._group_by)
        if self._order_by:
            sql += " order by %s" % self.fields2sql(self._order_by)
        if self._limit:
            sql += " limit %s" % self.fields2sql(self._limit)
        if self._other:
            sql += ' %s' % self.other2sql(self._other)
        if fill_args:
            return self._dbo.mogrify(sql, self._where_args)
        return sql

    def fields(self, *args):
        self._fields = args
        return self

    def join(self, table, on, join_type=None):
        assert isinstance(on, dict), "'on' must be dict"
        self._on = on
        self._join_table = table
        if join_type:
            self._join_type = join_type
        return self

    def left_join(self, table, on):
        return self.join(table, on, join_type='left')

    def right_join(self, table, on):
        return self.join(table, on, join_type='right')

    def group_by(self, *args):
        self._group_by = args
        return self

    def order_by(self, *args):
        assert len(args) <= 2, "'order_by' accept 1 or 2 parameters"
        self._order_by = args
        return self

    def limit(self, *args):
        assert len(args) <= 2, "'limit' accept 1 or 2 parameters"
        self._limit = (str(i) for i in args)
        return self

    def all(self, isdict=True):
        sql = self.sql(fill_args=False)
        return self._dbo.query(sql, self._where_args or None, isdict=isdict)

    def first(self, isdict=True):
        sql = self.sql(fill_args=False)
        if sql.find('limit') == -1:
            sql += ' limit 1'
        return self._dbo.get(sql, self._where_args or None, isdict=isdict)
    
    def _count_sql(self, sql):
        backsql = sql[sql.find(" from "):]
        return f"select count(*) as total {backsql}"
    
    def page(self, page=1, size=20, isdict=True):
        assert page > 0 and isinstance(page, int)
        assert size > 0 and isinstance(size, int)
        sql = self.sql(fill_args=False)
        assert sql.find('limit') == -1, ValueError("page不能自定义limit")

        # 生成sql
        count_sql = self._count_sql(sql)
        sql += ' limit %s,%s' % ((page - 1) * size, size)

        # 获取数据
        count_data = self._dbo.get(count_sql, self._where_args or None, isdict=True)
        page_data = self._dbo.query(sql, self._where_args or None, isdict=isdict)
        pages = ceil(count_data["total"] / size)

        return Page(
            total=count_data["total"],
            pages=pages,
            page=page,
            size=size,
            data=page_data
        )


class InsertHelper(Base, ValuesMixin, OtherMixin):
    def __init__(self, dbo, table, values=None, values_args=None, many=None, other=None):
        self._dbo = dbo
        self._table = table
        self._values = values
        self._values_args = values_args or list()
        self._many = many
        self._other = other

    def many(self, _dict_list):
        self._many = _dict_list
        return self

    def sql(self, fill_args=True):
        assert not (self._values and self._many), \
            "'values' and 'many' cannot exist at the same time"
        assert self._values or self._many, \
            "'values' or 'many' must be used"
        sql = 'insert into %s %s' % (
            self.table2sql(self._table),
            self.values2insert(self._values) if self._values else self.valueslist2insert(self._many)
            )
        if self._other:
            sql += ' %s' % self.other2sql(self._other)
        if fill_args:
            return self._dbo.mogrify(sql, self._values_args)
        return sql

    def execute(self):
        sql = self.sql(fill_args=False)
        res = self._dbo.execute_insert(sql, self._values_args or None)
        return res

    def from_select(self):
        # TODO
        return self


class UpdateHelper(Base, WhereMixin, ValuesMixin, OtherMixin):
    def __init__(self, dbo, table, where=None, where_args=None, values=None, values_args=None, other=None):
        self._dbo = dbo
        self._table = table
        self._where = where
        self._where_args = where_args or list()
        self._values = values
        self._values_args = values_args or list()
        self._other = other

    def sql(self, fill_args=True):
        sql = 'update %s set %s' % (
            self.table2sql(self._table),
            self.values2sql(self._values)
            )
        if self._where:
            sql += " where %s" % self.where2sql(self._where)
        if self._other:
            sql += ' %s' % self.other2sql(self._other)
        if fill_args:
            return self._dbo.mogrify(sql, self._values_args)
        return sql

    def execute(self):
        sql = self.sql(fill_args=False)
        args = self._values_args + self._where_args
        self._dbo.execute(sql, args or None)

class DeleteHelper(Base, WhereMixin, OtherMixin):
    def __init__(self, dbo, table, where=None, where_args=None, other=None):
        self._dbo = dbo
        self._table = table
        self._where = where
        self._where_args = where_args or list()
        self._other= other

    def sql(self, fill_args=True):
        sql = 'delete from %s' % self.table2sql(self._table)
        if self._where:
            sql += " where %s" % self.where2sql(self._where)
        if self._other:
            sql += ' %s' % self.other2sql(self._other)
        if fill_args:
            return self._dbo.mogrify(sql, self._values_args)
        return sql

    def execute(self):
        sql = self.sql(fill_args=False)
        self._dbo.execute(sql, self._where_args or None)


class DBHelper:
    def __init__(self):
        self._conn = None

    def format_timestamp(self, ret, cur):
        '''将字段以_time结尾的格式化成datetime'''
        if not ret:
            return ret
        index = []
        for d in cur.description:
            if d[0].endswith('_time'):
                index.append(cur.description.index(d))

        res = []
        for i, t in enumerate(ret):
            if i in index and isinstance(t, int):
                res.append(datetime.datetime.fromtimestamp(t))
            else:
                res.append(t)
        return res

    #执行命令
    @timesql
    def execute(self, sql, args=None):
        '''执行单个sql命令'''
        with self.connect_cur() as cur:
            if args:
                if settings.DB_TYPE == DBTYPE.SQLITE3:
                    sql = sql.replace("%s", "?")
                if not isinstance(args, (dict, tuple, list)):
                    args = tuple([args])
                ret = cur.execute(sql, args)
            else:
                ret = cur.execute(sql)
            return ret

    # 执行插入命令
    @timesql
    def execute_insert(self, sql, args=None, isdict=True):
        '''执行单个sql命令'''
        with self.connect_cur() as cur:
            if settings.DB_TYPE == DBTYPE.POSTGRESQL:
                lower_sql = str(sql).lower()
                if lower_sql.find('returning') == -1:
                    sql = '%s returning *' % sql
            if args:
                if settings.DB_TYPE == DBTYPE.SQLITE3:
                    sql = sql.replace("%s", "?")
                if not isinstance(args, (dict, tuple, list)):
                    args = tuple([args])
                ret = cur.execute(sql, args)
            else:
                ret = cur.execute(sql)
            if settings.DB_TYPE == DBTYPE.POSTGRESQL:
                res = cur.fetchone()
                res = self.format_timestamp(res, cur)
                if res and isdict:
                    xkeys = [i[0] for i in cur.description]
                    return dict(zip(xkeys, res))
                else:
                    return res
            else:
                if cur.lastrowid:
                    return cur.lastrowid
                return ret

    @timesql
    def executemany(self, sql, args=None):
        '''调用executemany执行多条命令'''
        with self.connect_cur() as cur:
            if args:
                if settings.DB_TYPE == DBTYPE.SQLITE3:
                    sql = sql.replace("%s", "?")
                if not isinstance(args, (dict, tuple, list)):
                    args = tuple([args])
                ret = cur.executemany(sql, args)
            else:
                ret = cur.executemany(sql)
            return ret
    
    @timesql
    def query(self, sql, args=None, isdict=True, hashead=False):
        '''sql查询，返回查询结果
        sql: 要执行的sql语句
        args: 要传入的参数
        isdict: 返回值格式是否为dict, 默认True
        hashead: 如果isdict为Fasle, 返回的列表中是否包含列标题
        '''
        with self.connect_cur() as cur:
            if not args:
                cur.execute(sql)
            else:
                if settings.DB_TYPE == DBTYPE.SQLITE3:
                    sql = sql.replace("%s", "?")
                if not isinstance(args, (dict, tuple, list)):
                    args = tuple([args])
                cur.execute(sql, args)
            res = cur.fetchall()
            res = [self.format_timestamp(r, cur) for r in res]
            if res and isdict:
                ret = []
                xkeys = [i[0] for i in cur.description]
                for item in res:
                    ret.append(dict(zip(xkeys, item)))
            else:
                ret = res
                if hashead:
                    xkeys = [i[0] for i in cur.description]
                    ret.insert(0, xkeys)
            return ret

    @timesql
    def get(self, sql, args=None, isdict=True):
        '''sql查询，只返回一条
        sql: sql语句
        args: 传参
        isdict: 返回值是否是dict
        '''
        with self.connect_cur() as cur:
            if args:
                if settings.DB_TYPE == DBTYPE.SQLITE3:
                    sql = sql.replace("%s", "?")
                if not isinstance(args, (dict, tuple, list)):
                    args = tuple([args])
                cur.execute(sql, args)
            else:
                cur.execute(sql)
            res = cur.fetchone()
            res = self.format_timestamp(res, cur)
            if res and isdict:
                xkeys = [i[0] for i in cur.description]
                return dict(zip(xkeys, res))
            else:
                return res

    def insert_batch(self, table, data: List[dict], batch=2000):
        """分批插入数据库
        parameters:
            table: str, 表名
            data: List(dict), 要插入的数据
            batch: int, 每批的数量
        """
        assert data and isinstance(data, list)
        assert isinstance(batch, int) and batch > 0
        batch_datas = (data[i*batch:(i+1)*batch] for i in range(ceil(len(data) / batch)))
        with self.transaction() as db_trans:
            insert_many = lambda x: db_trans.insert(table).many(x).execute()
            list(map(insert_many, batch_datas))
        return 1

    def mogrify(self, sql, args=None):
        '''返回填充args后的sql语句
        sql: sql语句
        args: 传参
        '''
        with self.connect_cur() as cur:
            if args:
                if not isinstance(args, (dict, tuple, list)):
                    args = tuple([args])
                sql = cur.mogrify(sql, args)
                if isinstance(sql, str):
                    return sql
                else:
                    return str(sql, encoding='utf-8')
            else:
                return sql

    def escape(self, s):
        return s

    def select(self, tables, **kwargs):
        return SelectHelper(self, tables, **kwargs)

    def insert(self, table, **kwargs):
        return InsertHelper(self, table, **kwargs)

    def update(self, table, **kwargs):
        return UpdateHelper(self, table, **kwargs)

    def delete(self, table, **kwargs):
        return DeleteHelper(self, table, **kwargs)

    @abc.abstractmethod
    @contextmanager
    def connect_cur(self):
        cur = None
        try:
            yield cur
        except:
            pass
        finally:
            pass

    # def select_page(self, sql, pagecur=1, pagesize=20, count_sql=None, maxid=-1, isdict=True):
    #     page = pager.db_pager(self, sql, pagecur, pagesize, count_sql, maxid)
    #     if isdict:
    #         page.todict()
    #     else:
    #         page.tolist()
    #     return page

