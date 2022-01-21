import jsonpath
import requests,json
from aishu import setting
from aishu.datafaker.profession.entity import id
from aishu.datafaker.profession.entity import name,timestamp,zx
from aishu.public.db_select import select


class search(object):
    def createSearchId(self):
        url = "http://{ip}/v1/search/submit".format(ip=setting.host)
        logGroup = id.date().getDefaultLogGroupID()
        startTime = timestamp.date().getLastHourTime()
        endTime = timestamp.date().getEndTime()
        payload = [
            {
                "logGroup": logGroup,
                "query": "*",
                "sort": [
                    {
                        "@timestamp": "desc"
                    }
                ],
                "size": 10,
                "needFieldList": True,
                "filters": {
                    "must": [
                        {
                            "@timestamp": {
                                "from": startTime,
                                "to": endTime
                            }
                        }
                    ],
                    "must_not": []
                }
            }
        ]
        headers = setting.header

        rsp = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        s_id = jsonpath.jsonpath(rsp.json(), '$..{name}'.format(name='id'))
        if isinstance(s_id,bool):
            return False
        else:
            return s_id[0]

    def createInspectionID(self):
        url = "http://{ip}/manager/inspections/inspection".format(ip=setting.host)
        assigned = id.date().getAdminID()
        number = name.date().getName()
        time = timestamp.date().getStartTime()
        payload = {
                "assign": assigned,
                "name": number,
                "info": "This is a test case by AT",
                "ctime": time
        }
        headers = setting.header

        rsp = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        InspectionID = jsonpath.jsonpath(rsp.json(), '$..{name}'.format(name='id'))
        if isinstance(InspectionID,bool):
            return False
        else:
            return InspectionID[0]

    def createInspectionTaskID(self):
        url = "http://{ip}/manager/inspections/task".format(ip=setting.host)
        InspectionID = zx.search().createInspectionID()
        number = name.date().getName()
        payload = {

                "name": number,
                "position": "localUpload",
                "info": "step one: find the target page ；step two：write the check result",
                "inspectionID": InspectionID
        }
        headers = setting.header

        rsp = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        InspectionTaskID = jsonpath.jsonpath(rsp.json(), '$..{name}'.format(name='id'))
        if isinstance(InspectionTaskID,bool):
            return False
        else:
            return InspectionTaskID[0]

    def createExportFileID(self):
        url = "http://{ip}/manager/export".format(ip=setting.host,id=zx.search().createSearchId())
        start = timestamp.date().getLastFiveYearTime()
        end = timestamp.date().getStartTime()
        user = id.date().getAdminID()
        loggroup = id.date().getDefaultLogGroupID()
        payload = {
                "logtype": "list",
                "filename": "列表",
                "timezone": 8,
                "user": user,
                "fileType": "txt",
                "fileCode": "UTF-8",
                "query": [
                    {
                        "logGroup": loggroup,
                        "query": "*",
                        "size": 207,
                        "needFieldList": True,
                        "filters": {
                            "must": [
                                {
                                    "@timestamp": {
                                        "from": start,
                                        "to": end
                                    }
                                }
                            ],
                            "must_not": []
                        }
                    }
                ],
                "fields": [
                    "_source"
                ],
                "indexs": [
                    "fe5b7f96-443a-11e7-a467-000c29253e90"
                ]
        }
        headers = setting.header
        rsp = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        ExportFileID = jsonpath.jsonpath(rsp.json(), '$..{name}'.format(name='id'))
        if isinstance(ExportFileID, bool):
            return False
        else:
            return ExportFileID[0]

    def getRepeatInspectionName(self):
        sql = 'select name from Inspection'
        sqldata = select(sql)
        if not (sqldata):
            return False

        return sqldata[0][0]

    # def getContextID(self):
    #     url = "http://{ip}/v1/search/fetch/{id}".format(ip=setting.host, id=zx.search().createSearchId())
    #     headers = setting.header
    #     time.sleep(10)
    #     rsp = requests.request("GET", url, headers=headers)
    #     print(rsp)
    #     ContextID = jsonpath.jsonpath(rsp.json(), '$..{name}'.format(name='_id'))
    #     if isinstance(ContextID, bool):
    #         return False
    #     else:
    #         return ContextID

    # def getOrdinaryID(self):
    #     sql = 'select userId from `User` where loginName!="admin"'
    #     sqldata = select(sql)
    #     if not (sqldata):
    #         return False
    #
    #     return sqldata[0][0]

if __name__ == '__main__':
    setting.host = "192.168.84.26"
    setting.database = 'AnyRobot'
    setting.password = 'eisoo.com'
    setting.port = 30006
    setting.user = 'root'
    date = search().createSearchId()
    print(date)