import random
from aishu.datafaker.anyrobot.sqlMapping import sql
from aishu.public.db_select import select

class AnyRobotDataServer(object):
    def __init__(self,key):
        self.key = key
        self.sql = sql(self.key)

    def getValue(self):
        ar_id_list = []
        if isinstance(self.sql,bool):
            return False

        date = select(self.sql)
        if isinstance(date,bool):
            return False

        if len(date) == 0:
            return False

        for value in date:
            ar_id_list.append(value[0])
        return random.choice(ar_id_list)