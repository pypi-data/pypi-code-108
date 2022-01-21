import jsonpath
import random
import requests,json
from aishu import setting
from aishu.datafaker.profession.entity import id
from aishu.datafaker.profession.entity import name,timestamp,zx
from aishu.public.db_select import select

class DataManage_Storage(object):
    #返回一个角色id，但是这个角色id被用户已经使用
    def RoleId_user1(self):
        url = 'http://{ip}/manager/role'.format(ip=setting.host)
        headers = setting.header
        data = {
            "roleName": str(random.choice(range(10, 999))) + '_' + str(random.choice(range(10, 999))),
            "permissions": [
                {
                    "permissionId": "ID_MAINPAGE",
                    "parentId": "",
                    "isLeaf": 1,
                    "name": "ID_MAINPAGE",
                    "checked": True
                },
                {
                    "permissionId": "ID_SYSTEM_MANAGER_SYSTEM_LICENSE",
                    "parentId": "ID_SYSTEM_MANAGER",
                    "isLeaf": 1,
                    "name": "ID_SYSTEM_MANAGER_SYSTEM_LICENSE",
                    "checked": False
                }
            ],
            "resource": {
                "logGroup": [
                    "fe5b7f96-443a-11e7-a467-000c29253e90"
                ],
                "desensitize": 0,
                "jobTemplate": [],
                "dashboard": {
                    "dashboardId": [],
                    "mainPageId": ""
                }
            },
            "description": "应用给用户的角色",
            "defaultLogGroupID": "fe5b7f96-443a-11e7-a467-000c29253e90"
        }
        res = requests.post(url, headers=headers, data=json.dumps(data))
        sql = 'select roleId from Role where description = "应用给用户的角色"'
        sqldata = select(sql)
        if not (sqldata):
            return False
        return sqldata[0]


    def RoleId_user(self):
        url = 'http://{ip}/manager/user'.format(ip=setting.host)
        headers = setting.header
        data ={
            "displayName": str(random.choice(range(10, 999))),
            "loginName": str(random.choice(range(10, 999))),
            "roleId": self.RoleId_user1(),
            "status": 1,
            "wechatStatus": 0,
            "emailVerifyStatus": 0,
            "description": "不能删除的用户"
        }
        res = requests.post(url, headers=headers, data=json.dumps(data))
        roleId = jsonpath.jsonpath(res.json(), '$..{name}'.format(name='roleId'))
        if isinstance(roleId,bool):
            return False
        else:
            return roleId

if __name__ == '__main__':
    setting.host = "192.168.84.132"
    setting.database = 'AnyRobot'
    setting.password = 'eisoo.com'
    setting.port = 30006
    setting.user = 'root'
    a = DataManage_Storage()
    #a.RoleId_user1()
    a.RoleId_user()