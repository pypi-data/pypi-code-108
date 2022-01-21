import random
from aishu.public.db_select import select

class date(object):

    def getIndexId(self):
        #查询数据库所有的索引表。
        sql = 'SELECT id from IndexParams;'
        sqldata = select(sql)
        indexIds=[]
        if not (sqldata):
            return False

        #将查询到的数据规范化，规范为一个list。
        for index  in sqldata:
            for indexId in index:
                indexIds.append(indexId)

        if not (indexIds):
            return False
        return indexIds[random.randint(0,len(indexIds)-1)]

    def getIndexName(self):
        sql = 'SELECT indexName from IndexParams;'
        sqldata = select(sql)
        indexNames=[]
        if not (sqldata):
            return False

        #将查询到的数据规范化，规范为一个list。
        for index  in sqldata:
            for indexName in index:
                indexNames.append(indexName)

        if not (indexNames):
            return False
        return indexNames[random.randint(0,len(indexNames)-1)]

    def getIndexTypeAs(self):
        indexNames = []

        #从数据库查找对应的索引名字
        sql = 'SELECT indexName from IndexParams where dataType="as";'
        sqldata = select(sql)

        if not (sqldata):
            return False

        #从返回元组中提取indexName
        for index  in sqldata:
            for indexName in index:
                indexNames.append(indexName)

        if not (indexNames):
            return False

        return indexNames
