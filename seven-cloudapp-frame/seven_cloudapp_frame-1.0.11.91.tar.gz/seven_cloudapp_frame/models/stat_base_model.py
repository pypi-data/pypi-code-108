# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 09:39:08
@LastEditTime: 2022-01-13 14:57:43
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.frame_base_model import FrameBaseModel
from seven_cloudapp_frame.models.db_models.stat.stat_queue_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_report_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_orm_model import *

class StatBaseModel(FrameBaseModel):
    """
    :description: 统计上报业务模型
    """
    def __init__(self, context=None,logging_error=None, logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info
        super(StatBaseModel,self).__init__(context)

    def add_stat(self, app_id, act_id, module_id, user_id, open_id, key_name, key_value):
        """
        :description: 添加上报
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param user_id：用户标识
        :param open_id：open_id
        :param key_name：统计key
        :param key_value：统计value
        :return:
        :last_editors: HuangJianYi
        """
        stat_queue = StatQueue()
        stat_queue.app_id = app_id
        stat_queue.act_id = act_id
        stat_queue.module_id = module_id
        stat_queue.user_id = user_id
        stat_queue.open_id = open_id
        stat_queue.key_name = key_name
        stat_queue.key_value = key_value
        stat_queue.create_date = SevenHelper.get_now_datetime()
        stat_queue.process_date = SevenHelper.get_now_datetime()

        stat_process_ways = config.get_value("stat_process_ways","mysql")
        if stat_process_ways == "mysql":
            sub_table = SevenHelper.get_sub_table(act_id,config.get_value("stat_sub_table_count",0))
            stat_queue_model = StatQueueModel(sub_table=sub_table, context=self.context)
            stat_queue_model.add_entity(stat_queue)
        else:
            redis_init = SevenHelper.redis_init()
            redis_init.rpush(f"stat_queue_list:{str(user_id % 10)}", SevenHelper.json_dumps(stat_queue))

    def add_stat_list(self, app_id, act_id, module_id, user_id, open_id, key_list_dict):
        """
        :description: 添加上报
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param user_id：用户标识
        :param open_id：open_id
        :param key_list_dict:键值对字典
        :return:
        :last_editors: HuangJianYi
        """
        stat_queue_list = []
        for key,value in key_list_dict.items():
            stat_queue = StatQueue()
            stat_queue.app_id = app_id
            stat_queue.act_id = act_id
            stat_queue.module_id = module_id
            stat_queue.user_id = user_id
            stat_queue.open_id = open_id
            stat_queue.key_name = key
            stat_queue.key_value = value
            stat_queue.create_date = SevenHelper.get_now_datetime()
            stat_queue.process_date = SevenHelper.get_now_datetime()
            stat_queue_list.append(stat_queue)

        stat_process_ways = config.get_value("stat_process_ways","mysql")
        if stat_process_ways == "mysql":
            sub_table = SevenHelper.get_sub_table(act_id,config.get_value("stat_sub_table_count",0))
            stat_queue_model = StatQueueModel(sub_table=sub_table, context=self.context)
            return stat_queue_model.add_list(stat_queue_list)
        else:
            redis_init = SevenHelper.redis_init()
            for stat_queue in stat_queue_list:
                redis_init.rpush(f"stat_queue_list:{str(user_id % 10)}", SevenHelper.json_dumps(stat_queue))

    def get_stat_report_list(self, app_id, act_id, module_id, start_date, end_date, order_by="sort_index asc", is_only_module=False):
        """
        :description: 报表数据列表(表格)
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param order_by：排序
        :param is_only_module：是否只取module的数据
        :return list
        :last_editors: HuangJianYi
        """
        condition = "app_id=%s and act_id=%s and module_id=%s"
        params = [app_id,act_id,module_id]
        if start_date != "":
            condition += " and create_date>=%s"
            params.append(start_date)
        if end_date != "":
            condition += " and create_date<%s"
            params.append(end_date)
        if is_only_module == True:
            stat_orm_list = StatOrmModel(context=self.context).get_list("act_id=%s and module_id=%s and is_show=1", order_by=order_by, params=[act_id, module_id])
        else:
            stat_orm_list = StatOrmModel(context=self.context).get_list("((act_id=%s and module_id=%s) or (act_id=0 and module_id=0)) and is_show=1", order_by=order_by, params=[act_id,module_id])
        if len(stat_orm_list)<=0:
            return []
        key_name_s = ','.join(["'%s'" % str(stat_orm.key_name) for stat_orm in stat_orm_list])
        condition += f" and key_name in({key_name_s})"
        stat_report_model = StatReportModel(context=self.context)
        behavior_report_list = stat_report_model.get_dict_list(condition, group_by="key_name", field="key_name,SUM(key_value) AS key_value",params=params)
        #公共映射组（未去重）
        common_groups_1 = [orm.group_name for orm in stat_orm_list]
        #公共映射组(去重)
        common_groups = list(set(common_groups_1))
        common_groups.sort(key=common_groups_1.index)

        common_group_data_list = []

        for common_group in common_groups:
            group_data = {}
            group_data["group_name"] = common_group
            data_list = []

            # 无子节点
            orm_list = [orm for orm in stat_orm_list if orm.group_name == common_group and orm.group_sub_name == '']
            for orm in orm_list:
                data = {}
                data["title"] = orm.key_value
                data["name"] = orm.key_name
                data["value"] = 0
                for behavior_report in behavior_report_list:
                    if behavior_report["key_name"] == orm.key_name:
                        if orm.value_type == 2:
                            data["value"] = behavior_report["key_value"]
                        else:
                            data["value"] = int(behavior_report["key_value"])
                data_list.append(data)
            if len(data_list) > 0:
                group_data["data_list"] = data_list

            # 有子节点
            orm_list_sub = [orm for orm in stat_orm_list if orm.group_name == common_group and orm.group_sub_name != '']
            if orm_list_sub:
                groups_sub_name = [orm.group_sub_name for orm in orm_list_sub]
                #公共映射组(去重)
                sub_names = list(set(groups_sub_name))
                sub_names.sort(key=groups_sub_name.index)
                sub_group_data_list = []
                for sub_name in sub_names:
                    sub_group_data = {}
                    sub_group_data["group_name"] = sub_name
                    sub_data_list = []

                    # 无子节点
                    orm_list_1 = [orm for orm in stat_orm_list if orm.group_sub_name == sub_name]
                    for orm in orm_list_1:
                        data = {}
                        data["title"] = orm.key_value
                        data["name"] = orm.key_name
                        data["value"] = 0
                        for behavior_report in behavior_report_list:
                            if behavior_report["key_name"] == orm.key_name:
                                if orm.value_type == 2:
                                    data["value"] = behavior_report["key_value"]
                                else:
                                    data["value"] = int(behavior_report["key_value"])
                        sub_data_list.append(data)
                    sub_group_data["data_list"] = sub_data_list
                    sub_group_data_list.append(sub_group_data)
                group_data["sub_data_list"] = sub_group_data_list

            common_group_data_list.append(group_data)

        return common_group_data_list

    def get_trend_report_list(self, app_id, act_id, module_id, start_date, end_date, order_by="sort_index asc", is_only_module=False):
        """
        :description: 报表数据列表(趋势图)
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param order_by：排序
        :param is_only_module：是否只取module的数据
        :return list
        :last_editors: HuangJianYi
        """
        condition = "app_id=%s and act_id=%s and module_id=%s"
        params = [app_id,act_id,module_id]
        if start_date != "":
            condition += " and create_date>=%s"
            params.append(start_date)
        if end_date != "":
            condition += " and create_date<%s"
            params.append(end_date)
        if is_only_module == True:
            stat_orm_list = StatOrmModel(context=self.context).get_list("act_id=%s and module_id=%s and is_show=1", order_by=order_by, params=[act_id, module_id])
        else:
            stat_orm_list = StatOrmModel(context=self.context).get_list("((act_id=%s and module_id=%s) or (act_id=0 and module_id=0)) and is_show=1", order_by=order_by, params=[act_id,module_id])
        if len(stat_orm_list)<=0:
            return []
        key_name_s = ','.join(["'%s'" % str(stat_orm.key_name) for stat_orm in stat_orm_list])
        condition += f" and key_name in({key_name_s})"
        stat_report_model = StatReportModel(context=self.context)
        stat_report_list = stat_report_model.get_dict_list(condition, field="key_name,key_value,DATE_FORMAT(create_date,'%%Y-%%m-%%d') AS create_date",params=params)
        date_list = SevenHelper.get_date_list(start_date, end_date)
        #公共映射组（未去重）
        common_groups_1 = [orm.group_name for orm in stat_orm_list]
        #公共映射组(去重)
        common_groups = list(set(common_groups_1))
        common_groups.sort(key=common_groups_1.index)

        common_group_data_list = []

        for common_group in common_groups:
            group_data = {}
            group_data["group_name"] = common_group
            data_list = []

            # 无子节点
            orm_list = [orm for orm in stat_orm_list if orm.group_name == common_group and orm.group_sub_name == '']
            for orm in orm_list:
                data = {}
                data["title"] = orm.key_value
                data["name"] = orm.key_name
                data["value"] = []
                for date_day in date_list:
                    behavior_date_report = {}
                    for behavior_report in stat_report_list:
                        if behavior_report["key_name"] == orm.key_name and behavior_report["create_date"] == date_day:
                            if orm.value_type != 2:
                                behavior_report["key_value"] = int(behavior_report["key_value"])
                            behavior_date_report = {"title": orm.key_value, "date": date_day, "value": behavior_report["key_value"]}
                            break
                    if not behavior_date_report:
                        behavior_date_report = {"title": orm.key_value, "date": date_day, "value": 0}
                    data["value"].append(behavior_date_report)
                data_list.append(data)
            if len(data_list) > 0:
                group_data["data_list"] = data_list

            # 有子节点
            orm_list_sub = [orm for orm in stat_orm_list if orm.group_name == common_group and orm.group_sub_name != '']
            if orm_list_sub:
                groups_sub_name = [orm.group_sub_name for orm in orm_list_sub]
                #公共映射组(去重)
                sub_names = list(set(groups_sub_name))
                sub_names.sort(key=groups_sub_name.index)
                sub_group_data_list = []
                for sub_name in sub_names:
                    sub_group_data = {}
                    sub_group_data["group_name"] = sub_name
                    sub_data_list = []

                    # 无子节点
                    orm_list_1 = [orm for orm in stat_orm_list if orm.group_sub_name == sub_name]
                    for orm in orm_list_1:
                        data = {}
                        data["title"] = orm.key_value
                        data["name"] = orm.key_name
                        data["value"] = []
                        for date_day in date_list:
                            behavior_date_report = {}
                            for behavior_report in stat_report_list:
                                if behavior_report["key_name"] == orm.key_name and behavior_report["create_date"] == date_day:
                                    if orm.value_type != 2:
                                        behavior_report["key_value"] = int(behavior_report["key_value"])
                                    behavior_date_report = {"title": orm.key_value, "date": date_day, "value": behavior_report["key_value"]}
                                    break
                            if not behavior_date_report:
                                behavior_date_report = {"title": orm.key_value, "date": date_day, "value": 0}
                            data["value"].append(behavior_date_report)
                        sub_data_list.append(data)
                    sub_group_data["data_list"] = sub_data_list
                    sub_group_data_list.append(sub_group_data)
                group_data["sub_data_list"] = sub_group_data_list

            common_group_data_list.append(group_data)

        return common_group_data_list

    def process_invite_report(self,app_id,act_id,module_id,user_id,open_id,login_token,invite_user_id,handler_name,check_user_nick=True,continue_request_expire=5,is_stat=True):
        """
        :description: 处理邀请进入上报
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param open_id:open_id
        :param login_token:访问令牌
        :param invite_user_id:邀请人用户标识
        :param handler_name:接口名称
        :param check_user_nick:是否校验昵称为空
        :param continue_request_expire:连续请求过期时间，为0不进行校验，单位秒
        :param is_stat:是否统计上报
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        acquire_lock_name = f"process_invite_report:{act_id}_{module_id}_{user_id}"
        identifier = ""
        try:
            invoke_result_data = InvokeResultData()
            if user_id == invite_user_id:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "无效邀请"
                return invoke_result_data
            stat_base_model = StatBaseModel(context=self.context)
            key_list_dict = {}
            invoke_result_data = self.business_process_executing(app_id,act_id,module_id,user_id,login_token,handler_name,True,check_user_nick,continue_request_expire,acquire_lock_name)
            if invoke_result_data.success == True:
                act_info_dict = invoke_result_data.data["act_info_dict"]
                act_module_dict = invoke_result_data.data["act_module_dict"]
                user_info_dict = invoke_result_data.data["user_info_dict"]
                identifier = invoke_result_data.data["identifier"]
                if is_stat == True:
                    key_list_dict["AddBeInvitedUserCount"] = 1 #从分享进入新增用户数
            if is_stat == True:
                key_list_dict["BeInvitedUserCount"] = 1  #从分享进入用户数
                key_list_dict["BeInvitedCount"] = 1  #从分享进入次数
                stat_base_model.add_stat_list(app_id, act_id, module_id, user_id, open_id, key_list_dict)
        except Exception as ex:
            if self.context:
                self.context.logging_link_error("【处理邀请上报】" + traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error("【处理邀请上报】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = "系统繁忙,请稍后再试"

        self.business_process_executed(act_id,module_id,user_id,handler_name,acquire_lock_name,identifier)

        return invoke_result_data

    def process_share_report(self,app_id,act_id,module_id,user_id,login_token,handler_name,check_user_nick=True,continue_request_expire=5,is_stat=True):
        """
        :description: 处理分享上报
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param handler_name:接口名称
        :param check_user_nick:是否校验昵称为空
        :param continue_request_expire:连续请求过期时间，为0不进行校验，单位秒
        :param is_stat:是否统计上报
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        acquire_lock_name = f"process_share_report:{act_id}_{module_id}_{user_id}"
        identifier = ""
        try:
            invoke_result_data = self.business_process_executing(app_id,act_id,module_id,user_id,login_token,handler_name,False,check_user_nick,continue_request_expire,acquire_lock_name)
            if invoke_result_data.success == True:
                user_info_dict = invoke_result_data.data["user_info_dict"]
                identifier = invoke_result_data.data["identifier"]
                if is_stat == True:
                    stat_base_model = StatBaseModel(context=self.context)
                    key_list_dict = {}
                    key_list_dict["ShareUserCount"] = 1 #分享用户数
                    key_list_dict["ShareCount"] = 1 #分享次数
                    stat_base_model.add_stat_list(app_id, act_id, module_id, user_info_dict["user_id"], user_info_dict["open_id"], key_list_dict)

        except Exception as ex:
            if self.context:
                self.context.logging_link_error("【处理分享上报】" + traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error("【处理分享上报】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = "系统繁忙,请稍后再试"

        self.business_process_executed(act_id,module_id,user_id,handler_name,acquire_lock_name,identifier)

        return invoke_result_data