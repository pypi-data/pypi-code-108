import uuid
from aishu.public.db_select import select

class date(object):
    def getUUid(self):
        uuidStr = uuid.uuid4()
        return str(uuidStr)

    def getAsLogWareID(self):
        sql='select id from LogWareHouse where dataType="as访问日志"'
        sqldata = select(sql)
        if len(sqldata) != 1:
            return False

        return sqldata[0][0]

    def getDefaultLogGroupID(self):
        sql = 'select groupId from `LogGroup` where groupName="所有日志"'
        sqldata = select(sql)
        if isinstance(sqldata,bool):
            return False

        if  len(sqldata) !=1:
            return False

        return sqldata[0][0]


    def getAdminID(self):
        sql = 'select userId from `User` where loginName="admin"'
        sqldata = select(sql)
        if not (sqldata):
            return False

        return sqldata[0][0]
