from aishu.datafaker.anyrobot.getSqlVaule import AnyRobotDataServer
from aishu.datafaker.profession.getFiledValue import filed
from aishu import setting

class faker():
    def __init__(self,host,port,user,password,database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        setting.host = self.host
        setting.port = self.port
        setting.user = self.user
        setting.password = self.password
        setting.database = self.database

    def route(self,key,result=[]):
        date = AnyRobotDataServer(key).getValue()
        if isinstance(date, bool):
            date = filed(key, result)
            return date
        else:
            return date

if __name__ == '__main__':
    host = ''
    key = ''
    port = 3306
    user = ''
    password = ''
    database = ''
    date1 = faker(host,port,user,password,database).route(key)
    print(date1)