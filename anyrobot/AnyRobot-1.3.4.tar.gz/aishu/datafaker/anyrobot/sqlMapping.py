from aishu import setting
from aishu.datafaker.profession.entity import ip
def sql(key):
    """
    对应数据服务的sql语句注册
    :param key:
    :return:
    """
    switcher = {
        'UserID':{'sql':'select userId from User where loginName = "admin";','database':'AnyRobot'},
        'MLID': {'sql': "select id from MLJob ;", 'database': 'AnyRobotML'},
        'entityID': {'sql': "select id from KAIEntity;", 'database': 'AnyRobot'},
        'groupID': {'sql': "select id from KAIEntityGroup;", 'database': 'AnyRobot'},
        'AlertRuleID': {'sql': "select id from RuleEngineAlert;", 'database': 'AnyRobot'},
        'kpiID': {'sql': "select id from KAIKpi;", 'database': 'AnyRobot'},
        'LogTypeID': {'sql': "select dataType from LogWareHouse;", 'database': 'AnyRobot'},
        'AddEntityID': {
            'sql': "select entityId from KAIEntityCondition where conditionValues = '192.168.84.26' AND conditionKeys = 'host';",
            'database': 'AnyRobot'},
        'KpiTemplateID': {'sql': "select id from KAIKpiTemplate;", 'database': 'AnyRobot'},
        'KpiTemplateID1': {'sql': "select id from KAIKpiTemplate;", 'database': 'AnyRobot'},
        'KpiTemplateID2': {'sql': "select id from KAIKpiTemplate;", 'database': 'AnyRobot'},
        'logWareHouseID': {'sql': "SELECT id From LogWareHouse where LENGTH(id)!=8;", 'database': 'AnyRobot'},
        'logWareHouseId': {'sql': "SELECT id From LogWareHouse where LENGTH(id)!=8;", 'database': 'AnyRobot'},
        'wareHouseName': {'sql': "SELECT wareHouseName From LogWareHouse;", 'database': 'AnyRobot'},
        'dataType': {'sql': "SELECT dataType From LogWareHouse where LENGTH(id)!=8;", 'database': 'AnyRobot'},
        'indexID': {'sql': "SELECT id From IndexParams;", 'database': 'AnyRobot'},
        'indexName': {'sql': "SELECT indexName From IndexParams;", 'database': 'AnyRobot'},
        'StreamId': {'sql': "SELECT id From DataStream;", 'database': 'AnyRobot'},
        'LogGroupIdPare': {'sql': 'SELECT groupId From LogGroup where GroupName!="所有日志";', 'database': 'AnyRobot'},
        'RoleId': {'sql': 'SELECT roleId From Role where roleName ="admin";', 'database': 'AnyRobot'},
        'RoleId_Notadmin': {'sql': 'SELECT roleId From Role where roleName != "admin" AND roleName != "user";', 'database': 'AnyRobot'},
        'tagGroupID': {'sql': "SELECT id From TagGroup;", 'database': 'AnyRobot'},
        'tagID': {'sql': "SELECT id From Tag;", 'database': 'AnyRobot'},
        'HostID': {'sql': "SELECT id From AgentHost;", 'database': 'AnyRobot'},
        'HostIp': {'sql': "SELECT ip From AgentHost;", 'database': 'AnyRobot'},
        'openapiID': {'sql': "SELECT id From OpenAPIManager;", 'database': 'AnyRobotOpenLog'},
        'UserID_Notadmin': {'sql': 'select userId from User where loginName != "admin" AND status != 0;', 'database': 'AnyRobot'},
        'JDBCCollectorId': {
            'sql': "select collectorId from JDBCCollectorConfig where JDBCCollectorConfig.type='mysqljdbc' AND JDBCCollectorConfig.`sql`='select * from AgentHost';",
            'database': 'AnyRobot'},
        'vSphereID': {
            'sql': "SELECT collectorId FROM CollectorConfig WHERE collectorType='vSphere' AND config LIKE '%hlaio.aishu.cn%';",
            'database': 'AnyRobot'},
        'vcenterCollectorId': {
            'sql': "SELECT collectorId FROM CollectorConfig WHERE collectorType='vCenter' AND config LIKE '%hlaio.aishu.cn%';",
            'database': 'AnyRobot'},
        'MySQLCollectorId': {'sql': "SELECT collectorId FROM CollectorConfig WHERE collectorType='MySQL Performance';",
                             'database': 'AnyRobot'},
        'OracleCollectorId': {
            'sql': "SELECT collectorId FROM CollectorConfig WHERE collectorType='Oracle Performance';",
            'database': 'AnyRobot'},
        'AIXCollectorId': {'SQL': "SELECT collectorId FROM CollectorConfig WHERE collectorType='AIX Errpt';",
                           'database': 'AnyRobot'},
        'CMDCollectorId': {'sql': "SELECT collectorId FROM CollectorConfig WHERE collectorType='Command Result';",
                           'database': 'AnyRobot'},
        'CollectorId': {'sql': "SELECT collectorId FROM CollectorConfig;", 'database': 'AnyRobot'},
        'DBConnectID': {'sql': "SELECT id FROM DBConnect;", 'database': 'AnyRobot'},
        'AuthID': {'sql': "SELECT id FROM AgentHostAuth;", 'database': 'AnyRobot'},
        'authName': {'sql': "SELECT `name` FROM AgentHostAuth;", 'database': 'AnyRobot'},
        'TemplateID': {'sql': "SELECT id FROM AgentConfigTemplate;", 'database': 'AnyRobot'},
        'AgentInputTemplateID': {'sql': "SELECT id FROM AgentConfigTemplate WHERE category='input';",
                                 'database': 'AnyRobot'},
        'AgentOutTemplateID': {'sql': "SELECT id FROM AgentConfigTemplate WHERE category='output';",
                               'database': 'AnyRobot'},
        'InputTemplateName': {'sql': "SELECT `name` FROM AgentConfigTemplate WHERE category='input';",
                              'database': 'AnyRobot'},
        'OutputTemplateName': {'sql': "SELECT `name` FROM AgentConfigTemplate WHERE category='output';",
                               'database': 'AnyRobot'},
        'AgentGroupID': {'sql': "SELECT id FROM AgentGroup;", 'database': 'AnyRobot'},
        'AgentJobTemplateID': {'sql': "SELECT id FROM AgentJobTemplate", 'database': 'AnyRobot'},
        'JobID': {'sql': "SELECT id FROM AgentJobInfo;", 'database': 'AnyRobot'},
        'uploadID': {'sql': "SELECT id FROM Upload;", 'database': 'AnyRobot'},
        'uninstallHostID': {'sql':"SELECT id From AgentHost WHERE ip='{ip}';".format(ip=ip.date().getAentHostIp()),'database': 'AnyRobot'},
        'entitygroupId': {'sql':"SELECT id From KAIEntityGroup ;",'database': 'AnyRobot'},
        'serviceKpiId': {'sql':"SELECT id From KAIKpi ;",'database': 'AnyRobot'},
        'serviceHeathId': {'sql':"SELECT serviceId From KAIHealth ;",'database': 'AnyRobot'},
        'KAIAlertId': {'sql':"SELECT id From KAIAlert ;",'database': 'AnyRobot'},
        'KAIBusinessId': {'sql':"SELECT id From KAIBusiness ;",'database': 'AnyRobot'},
        'graphName': {'sql':"SELECT graph_name From graph ;",'database': 'AnyRobot'},
        'ScheduleTaskId': {'sql':"SELECT id From ScheduleTask ;",'database': 'AnyRobot'},
        'ScheduleTaskId1': {'sql':"SELECT id From ScheduleTask ;",'database': 'AnyRobot'},
        'UserId': {'sql':"SELECT userId From User ;",'database': 'AnyRobot'},
        'UserId2': {'sql':"SELECT userId From User ;",'database': 'AnyRobot'},
        'alertLogId': {'sql':"SELECT alert_scenario_rule_id From RuleEngineAlertLog ;",'database': 'AnyRobot'},
        'RuleEngineEnableId': {'sql':"SELECT id From RuleEngineAlertScenario Where status = 1;",'database': 'AnyRobot'},
        'RuleEngineDisableId': {'sql':"SELECT id From RuleEngineAlertScenario Where status = 0;",'database': 'AnyRobot'},
        'KAIAlertEnableId': {'sql':"SELECT id From KAIAlert Where status = 1 ;",'database': 'AnyRobot'},
        'KAIAlertDisableId': {'sql':"SELECT id From KAIAlert Where status = 0 ;",'database': 'AnyRobot'},
        'ScheduleTaskEnableId': {'sql':"SELECT id From ScheduleTask Where status = 1 ;",'database': 'AnyRobot'},
        'ScheduleTaskDisableId': {'sql':"SELECT id From ScheduleTask Where status = 0 ;",'database': 'AnyRobot'},
        'ReprotId': {'sql': "SELECT report_id From report WHERE is_share_allowed = 1;", 'database': 'AnyRobot'},
        'ReprotIdDisable': {'sql': "SELECT report_id From report WHERE is_share_allowed = 0;", 'database': 'AnyRobot'},
        'ReprotName': {'sql': "SELECT `name` From report ;", 'database': 'AnyRobot'},
        'ReprotType': {'sql': "SELECT `type` From report ;", 'database': 'AnyRobot'},
        'CorrelationSearchesId': {'sql': "SELECT `id` From correlate_search ;", 'database': 'AnyRobot'}
    }

    if switcher.get(key) is not None:
        if switcher[key].get('database') is not None:
            if len(switcher[key]['database']) == 0:
                setting.database = 'AnyRobot'
            else:
                setting.database = switcher[key]['database']

        return switcher[key]['sql']
    else:
        return False
