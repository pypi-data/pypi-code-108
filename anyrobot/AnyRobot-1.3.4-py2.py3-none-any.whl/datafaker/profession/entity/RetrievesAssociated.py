#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/01/26 16:03
# @Author  : xiong.yuanzhou
import random,json
from aishu.datafaker.profession.entity import date
from aishu.datafaker.profession.entity.AssociationMapping import sql
from aishu.public.db_select import select

class ParaDateAnyRobotServer(object):
    def __init__(self,key):
        self.key = key
        self.sql = sql(self.key)

    def getSavedSearchId(self):
        ar_id_list = []
        if isinstance(self.sql, bool):
            return 0
        Id_date = select(self.sql)
        if len(Id_date) == 0:
            return 0
        for value in Id_date:
            ar_id_list.append(value[0])
        SavedSearch_Id = random.choice(ar_id_list)
        date.saved_search_Id_List.append(SavedSearch_Id)
        return date.saved_search_Id_List[0]


    def getSavedSearchNameId(self):
        # 查询id对应的Name
        if isinstance(self.sql, bool):
            return 0
        Name_date = select(self.sql)
        if len(Name_date) == 0:
            return 0
        return Name_date[0][0]


    def getSavedSearchLogGroupId(self):
        # 查询id对应的SavedSearchLogGroupId
        if isinstance(self.sql, bool):
            return 0
        date = select(self.sql)
        if len(date) == 0:
            return 0
        return date[0][0].replace("\"", "")


    def getSavedSearchLogLibraryId(self):
        # 查询对应的SavedSearchLogLibraryId
        if isinstance(self.sql, bool):
            return 0
        date = select(self.sql)
        if len(date) == 0:
            return 0
        return date[0][0].replace("\"", "")


    def getAlertRuleNamesId(self):
        ar_id_list = []
        date = select(self.sql)
        if len(date) == 0:
            return 0
        for value in date:
            ar_id_list.append(value[0])
        return random.choice(ar_id_list)


    def getAlertScenarioId(self):
        ar_id_list = []
        if isinstance(self.sql, bool):
            return 0
        Id_date = select(self.sql)
        if len(Id_date) == 0:
            return 0
        for value in Id_date:
            ar_id_list.append(value[0])
        SavedSearch_Id = random.choice(ar_id_list)
        date.AlertScenario_Id_List.append(SavedSearch_Id)
        return date.AlertScenario_Id_List[0]


    def getDeleteAlertRuleNamesId(self):
        # 查询场景策略id对应的规则策略名称
        if isinstance(self.sql, bool):
            return 0
        Name_date = select(self.sql)
        if len(Name_date) == 0:
            return 0
        filter = json.loads(Name_date[0][0])[0]
        return filter


    def getServiceId(self):
        ar_id_list = []
        if isinstance(self.sql, bool):
            return 0
        Id_date = select(self.sql)
        if len(Id_date) == 0:
            return 0
        for value in Id_date:
            ar_id_list.append(value[0])
        date.Service_Id_List.append(random.choice(ar_id_list))
        return date.Service_Id_List[0]


    def getKpiId(self):
        # 查询服务对应的KPIId
        if isinstance(self.sql, bool):
            return 0
        Name_date = select(self.sql)
        if len(Name_date) == 0:
            return 0
        return Name_date[0][0]
