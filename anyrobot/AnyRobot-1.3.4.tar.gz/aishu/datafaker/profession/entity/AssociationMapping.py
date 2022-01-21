from aishu import setting
from aishu.datafaker.profession.entity import date


def sql(key):
    """
    对应数据服务的sql语句注册
    :param key:
    :return:
    """
    switcher = {
        'SavedSearchID': {'sql':"select id from Kibana where type = 'search';",'database':'AnyRobot'},
        'SavedSearchNameID': {'sql':"select title from Kibana where id = '{id}';".format(id="" if not date.saved_search_Id_List else date.saved_search_Id_List[0]),'database':'AnyRobot'},
        'serviceID': {'sql':"select id from KAIService;",'database':'AnyRobot'},
        'KpiID': {'sql':"select id from KAIKpi where serviceId = '{id}';".format(id="" if not date.Service_Id_List else date.Service_Id_List[0]),'database':'AnyRobot'},
        'SavedSearchLogGroupID': {'sql':"select json_extract(json_extract(json_extract(searchSourceJSON,'$.filter[0]'),'$.meta'),'$.index') from Kibana where id = '{id}';".format(id="" if not date.saved_search_Id_List else date.saved_search_Id_List[0]),'database':'AnyRobot'},
        'SavedSearchLogLibraryID': {'sql':"select json_extract(json_extract(json_extract(searchSourceJSON,'$.filter[0]'),'$.meta'),'$.value') from Kibana where id = '{id}';".format(id="" if not date.saved_search_Id_List else date.saved_search_Id_List[0]),'database':'AnyRobot'},
        'AlertRuleNamesID': {'sql':"select alert_rule_name from RuleEngineAlert;",'database':'AnyRobot'},
        'AlertScenarioID': {'sql':"select id from RuleEngineAlertScenario;",'database':'AnyRobot'},
        'DeleteAlertRuleNamesID': {'sql':"select alert_rule_names from RuleEngineAlertScenario where id = '{id}';".format(id="" if not date.AlertScenario_Id_List else date.AlertScenario_Id_List[0]),'database':'AnyRobot'}
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
