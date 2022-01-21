# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-10 10:05:38
@LastEditTime: 2021-11-29 16:40:32
@LastEditors: HuangJianYi
@Description: 任务模块
"""

from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.task_base_model import *
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.models.db_models.task.task_info_model import *


class TaskInfoListHandler(ClientBaseHandler):
    """
    :description: 获取任务列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取任务列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param is_release：是否发布
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        is_release = int(self.get_param("is_release", -1))
        task_base_model = TaskBaseModel(context=self)
        return self.response_json_success(task_base_model.get_task_info_dict_list(app_id, act_id, module_id,is_release,False))


class SaveTaskInfoHandler(ClientBaseHandler):
    """
    :description 保存任务
    """
    @filter_check_params("act_id,task_list")
    def post_async(self):
        """
        :description: 保存任务
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param task_list：任务列表
        :return response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        task_list = self.get_param("task_list")
        try:
            task_list = SevenHelper.json_loads(task_list)
        except Exception as ex:
            task_list = []
        task_base_model = TaskBaseModel(context=self)
        task_info_model = TaskInfoModel(context=self)
        for item in task_list:
            if not item.__contains__("task_type"):
                continue
            task_name = str(item["task_name"]) if item.__contains__("task_name") else ""
            complete_type = int(item["complete_type"]) if item.__contains__("complete_type") else 1
            sort_index = int(item["sort_index"]) if item.__contains__("sort_index") else 0
            is_release = int(item["is_release"]) if item.__contains__("is_release") else 0
            config_json = SevenHelper.json_dumps(item["config_json"]) if item.__contains__("config_json") else {}
            if "id" in item.keys():
                task_info = task_info_model.get_entity_by_id(int(item["id"]))
                if task_info:
                    old_task_info = deepcopy(task_info)
                    task_info.task_type = int(item["task_type"])
                    task_info.task_name = task_name
                    task_info.complete_type = complete_type
                    task_info.config_json = config_json
                    task_info.sort_index = sort_index
                    task_info.is_release = is_release
                    task_info.modify_date = SevenHelper.get_now_datetime()
                    task_info_model.update_entity(task_info, "complete_type,task_name,sort_index,is_release,config_json,modify_date")
                    task_base_model._delete_task_info_dependency_key(0,task_info.id)
                    self.create_operation_log(OperationType.update.value, task_info.__str__(), "SaveTaskInfoHandler", SevenHelper.json_dumps(old_task_info.__dict__), SevenHelper.json_dumps(task_info.__dict__))
                    ref_params = {}
                    self.business_process_executed(task_info, ref_params)
            else:
                task_info = TaskInfo()
                task_info.app_id = app_id
                task_info.act_id = act_id
                task_info.module_id = module_id
                task_info.task_type = int(item["task_type"])
                task_info.task_name = task_name
                task_info.complete_type = complete_type
                task_info.config_json = config_json
                task_info.sort_index = sort_index
                task_info.is_release = is_release
                task_info.create_date = SevenHelper.get_now_datetime()
                task_info.modify_date = SevenHelper.get_now_datetime()
                task_info_model.add_entity(task_info)
                self.create_operation_log(OperationType.add.value, task_info.__str__(), "SaveTaskInfoHandler", None, SevenHelper.json_dumps(task_info))
                ref_params = {}
                self.business_process_executed(task_info, ref_params)

        task_base_model._delete_task_info_dependency_key(act_id)

        return self.response_json_success()

