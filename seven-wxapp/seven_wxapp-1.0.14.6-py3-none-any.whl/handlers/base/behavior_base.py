# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2020-06-05 17:10:27
:LastEditTime: 2021-05-13 08:58:21
:LastEditors: HuangJingCan
@Description: 统计相关
"""
import decimal

from seven_wxapp.models.db_models.behavior.behavior_log_model import *
from seven_wxapp.models.db_models.behavior.behavior_orm_model import *
from seven_wxapp.models.db_models.behavior.behavior_report_model import *


class BehaviorModel():
    """
    :description: 统计相关
    """
    def __init__(self, context=None):
        self.context = context

    def report_behavior_log(self, act_id, user_id, behavior_key, behavior_value):
        """
        :description: 新统计上报,数据库表(behavior_report_tb)加唯一索引（act_id,key_name,create_day)）,避免重复数据
        :param act_id：活动id
        :param user_id:user_id
        :param behavior_key：统计key
        :param behavior_value：统计值
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            self.process_behavior(act_id, user_id, behavior_key, behavior_value)
        except Exception as ex:
            if str(ex).__contains__("Duplicate entry"):
                self.process_behavior(act_id, user_id, behavior_key, behavior_value)

    def process_behavior(self, act_id, user_id, behavior_key, behavior_value):
        """
        :description: 上报行为记录
        :param act_id：活动id
        :param user_id：user_id
        :param behavior_key：统计key
        :param behavior_value：统计值
        :return: 
        :last_editors: HuangJianYi
        """
        add_hours = config.get_value("add_hours", 0)
        create_date_str = TimeHelper.add_hours_by_format_time(hour=add_hours)
        create_date = TimeHelper.format_time_to_datetime(create_date_str)
        now_month_int = int(TimeHelper.datetime_to_format_time(create_date, "%Y%m"))
        now_day_int = int(TimeHelper.datetime_to_format_time(create_date, "%Y%m%d"))

        behavior_orm_model = BehaviorOrmModel()
        behavior_log_model = BehaviorLogModel()
        behavior_report_model = BehaviorReportModel()
        orm = None
        behavior_log = None
        orm = behavior_orm_model.get_entity("((act_id=%s and is_common=0) or is_common=1) and key_name=%s", params=[act_id, behavior_key])
        if not orm:
            return "NotOrm"
        if orm.is_repeat == 1:
            if orm.repeat_type == 2:
                behavior_log = behavior_log_model.get_entity("orm_id=%s and act_id=%s and user_id=%s", params=[orm.id, act_id, user_id])
            else:
                behavior_log = behavior_log_model.get_entity("orm_id=%s and act_id=%s and user_id=%s and create_day=%s", params=[orm.id, act_id, user_id, now_day_int])
            if not behavior_log:
                behavior_report = behavior_report_model.get_entity("act_id=%s and key_name=%s and create_day=%s", params=[act_id, behavior_key, now_day_int])
                if not behavior_report:
                    behavior_report = BehaviorReport()
                    behavior_report.act_id = act_id
                    behavior_report.key_name = behavior_key
                    behavior_report.key_value = behavior_value
                    behavior_report.create_date = create_date
                    behavior_report.create_year = create_date.year
                    behavior_report.create_month = now_month_int
                    behavior_report.create_day = now_day_int
                    behavior_report_model.add_entity(behavior_report)

                else:
                    behavior_report.key_value = decimal.Decimal(behavior_report.key_value) + behavior_value
                    behavior_report_model.update_entity(behavior_report)
        else:
            behavior_report = behavior_report_model.get_entity("act_id=%s and key_name=%s and  create_day=%s", params=[act_id, behavior_key, now_day_int])
            if not behavior_report:
                behavior_report = BehaviorReport()
                behavior_report.act_id = act_id
                behavior_report.key_name = behavior_key
                behavior_report.key_value = behavior_value
                behavior_report.create_date = create_date
                behavior_report.create_year = create_date.year
                behavior_report.create_month = now_month_int
                behavior_report.create_day = now_day_int
                behavior_report_model.add_entity(behavior_report)
            else:
                behavior_report.key_value = decimal.Decimal(behavior_report.key_value) + decimal.Decimal(behavior_value)
                behavior_report_model.update_entity(behavior_report)

        new_behavior_log = BehaviorLog()
        new_behavior_log.act_id = act_id
        new_behavior_log.user_id = user_id
        new_behavior_log.orm_id = orm.id
        new_behavior_log.inc_value = behavior_value
        new_behavior_log.create_day = now_month_int
        new_behavior_log.create_date = create_date

        behavior_log_model.add_entity(new_behavior_log)

    def save_orm(self, orm_infos, act_id):
        """
        :description: 保存Orm
        :param orm_infos：orm_infos
        :param act_id：活动id
        :return: 
        :last_editors: CaiYouBin
        """
        delete_orm_ids = []
        behavior_orm_model = BehaviorOrmModel()
        behavior_orm_list = behavior_orm_model.get_list('act_id=%s', params=act_id)
        for behavior_orm_item in behavior_orm_list:
            if behavior_orm_item.key_name.find(orm_infos[0].key_name) != -1:
                delete_orm_ids.append(str(behavior_orm_item.id))
            if behavior_orm_item.key_name.find(orm_infos[1].key_name) != -1:
                delete_orm_ids.append(str(behavior_orm_item.id))
        if len(delete_orm_ids) > 0:
            behavior_orm_model.del_entity('id in (' + ','.join(delete_orm_ids) + ')')

        behavior_orm_model.add_list(orm_infos)