from aishu import setting
from aishu.datafaker.profession.entity import name, switch, ip, timestamp, ml, kai, objectManager, index, agent ,id ,port, DataManage
from aishu.datafaker.profession.entity import zx,testMail, arPort
from aishu.datafaker.profession.entity.ParaDateFiled import ParaDateFiledServer
from aishu.datafaker.profession.entity.RetrievesAssociated import ParaDateAnyRobotServer
from aishu.datafaker.profession.entity import CreateTestPort

def filed(key,inquire=[]):
    """
    :param key:
    :return:
    """
    SERVICE_KPI_ = {
        'AnyRobotNameID': name.date().getName,
        'AnyRobotOtherNameID': name.date().getName,
        'Closed': switch.date().getSwClosed,
        'Open': switch.date().getSwOpen,
        'UUid': id.date().getUUid,
        'IpVR': ip.date().getIpVR,
        'IPError': ip.date().getIpError,
        'startTime': timestamp.date().getStartTime,
        'endTime': timestamp.date().getEndTime,
        'lastHourTime': timestamp.date().getLastHourTime,
        'last24HourTime': timestamp.date().getLast24HourTime,
        'lastTime':timestamp.date().getLastTime,
        'getEtlPortOld': port.date().getEtlPortOld,
        'getEtlPortNew': port.date().getEtlPortNew,
        'getEtlPortIll': port.date().getEtlPortIll,
        'enity': ml.machine(inquire).inquire,
        'entityHost': kai.machine(inquire).inquireEntity,
        'serviceKpiId': kai.machine(inquire).inquireServiceKpi,
        'businessKpiIdAndServiceId':kai.machine(inquire).inquireBusinessKPIAndServiceId,
        'ServiceBusinessID':kai.machine(inquire).ServiceBusiness,
        'pensInfo':kai.machine(inquire).inquirePens,
        'testHostIP':ip.date().getTestHostIP,
        'service_host_ip': ip.date().get_host_ip,
        'service_host_name': ip.date().get_host_name,
        'rarserRuleName': objectManager.date().getRuleNameId,
        'dashboardId': objectManager.date().getDashboardId,
        'searchId': objectManager.date().getSearchId,
        'visualizationId': objectManager.date().getVisualizationId,
        'indexId':index.date().getIndexId,
        'indexList':index.date().getIndexName,
        'indexList_as':index.date().getIndexTypeAs,
        'DateTime':timestamp.date().getDateTime,
        'agentPort': agent.machine(inquire).getAgentPort,
        'AlertAgentPort': agent.machine(inquire).getIntPort,
        'intPort':agent.machine(inquire).getIntPort,
        'adminID':id.date().getAdminID,
        'DefaultLogGroupID':id.date().getDefaultLogGroupID,
        'asLogWareID':id.date().getAsLogWareID,
        'httpUrl':kai.machine(inquire).getAlertHttpUrl,
        'lastFiveYearTime':timestamp.date().getLastFiveYearTime,
        'alertmergeID': ParaDateFiledServer().getUUid,
        'fromID': ParaDateFiledServer().getFromTime,
        'ToID': ParaDateFiledServer().getToTime,
        'StartDateID': ParaDateFiledServer().getStartDate,
        'EndDateID': ParaDateFiledServer().getEndDate,
        'TimeRangeID': ParaDateFiledServer().getTimeRangeId,
        'RangeUnitID': ParaDateFiledServer().getRangeUnitId,
        'TimeLabelID': ParaDateFiledServer().getTimeLabelId,
        'serviceID': ParaDateAnyRobotServer(key).getServiceId,
        'KpiID': ParaDateAnyRobotServer(key).getKpiId,
        'kpiNameID': ParaDateFiledServer().getkpiNameID,
        'kpiNameId': ParaDateFiledServer().kpiNameId,
        'SavedSearchID': ParaDateAnyRobotServer(key).getSavedSearchId,
        'SavedSearchNameID': ParaDateAnyRobotServer(key).getSavedSearchNameId,
        'SavedSearchLogGroupID': ParaDateAnyRobotServer(key).getSavedSearchLogGroupId,
        'SavedSearchLogLibraryID': ParaDateAnyRobotServer(key).getSavedSearchLogLibraryId,
        'AlertRuleNamesID': ParaDateAnyRobotServer(key).getAlertRuleNamesId,
        'AlertScenarioID': ParaDateAnyRobotServer(key).getAlertScenarioId,
        'DeleteAlertRuleNamesID': ParaDateAnyRobotServer(key).getDeleteAlertRuleNamesId,
        'UpdateTimeID': ParaDateFiledServer().getUpdateTime,
        'UtcStartID': ParaDateFiledServer().getUtcStartTime,
        'UtcEndID': ParaDateFiledServer().getUtcEndTime,
        's_id': zx.search().createSearchId,
        'InspectionID': zx.search().createInspectionID,
        'InspectionTaskID': zx.search().createInspectionTaskID,
        'ExportFileID': zx.search().createExportFileID,
        'RepeatInspectionName': zx.search().getRepeatInspectionName,
        'agentDeployIp': ip.date().getAentHostIp,
        'http_port': CreateTestPort.Port().httpport,
        'syslog_port': CreateTestPort.Port().syslogPort,
        'FutureTime': ParaDateFiledServer().getFutureTime,
        'RoleId_user': DataManage.DataManage_Storage().RoleId_user,
        'mailUser': testMail.date().getMailUser,
        'mailPass': testMail.date().getMailPass,
        'm_id': arPort.inputs().createarPortId,
        'now_times': ParaDateFiledServer().now_time,
        'five_feature_times': ParaDateFiledServer().five_feature_time
    }

    switcher = SERVICE_KPI_
    if switcher.get(key) is not None:
        return switcher[key]()
    else:
        return False

if __name__ == '__main__':
    setting.host = ""
    setting.database = ''
    setting.password = ''
    setting.port = 3306
    setting.user = ''
    date = filed("")
    print(date)