# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-28 09:54:51
@LastEditTime: 2022-01-13 14:48:28
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.seven_model import *

from seven_cloudapp_frame.models.db_models.base.base_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_type_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *


class ActBaseModel():
    """
    :description: 活动信息业务模型
    """
    def __init__(self,context=None,logging_error=None,logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def _delete_act_info_dependency_key(self,app_id,act_id):
        """
        :description: 删除活动信息依赖建
        :param app_id: 应用标识
        :param act_id: 活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            redis_init = SevenHelper.redis_init()
            if act_id:
                redis_init.delete(f"act_info:actid_{act_id}")
            if app_id:
                redis_init.delete(f"act_info_list:appid_{app_id}")
        except Exception as ex:
            pass
        
    def get_act_info_dict(self,act_id,is_cache=True,is_filter=True):
        """
        :description: 获取活动信息
        :param act_id: 活动标识
        :param is_cache: 是否缓存
        :param is_filter: 是否过滤未发布或删除的数据
        :return: 返回活动信息
        :last_editors: HuangJianYi
        """
        act_info_model = ActInfoModel(context=self.context)
        if is_cache:
            dependency_key = f"act_info:actid_{act_id}"
            act_info_dict = act_info_model.get_cache_dict_by_id(act_id,dependency_key=dependency_key)
        else:
            act_info_dict = act_info_model.get_dict_by_id(act_id)
        if is_filter == True:
            if not act_info_dict or act_info_dict["is_release"] == 0 or act_info_dict["is_del"] == 1:
                return None
        return act_info_dict

    def get_act_info_list(self,app_id,act_name,is_del,page_size,page_index,is_cache=True):
        """
        :description: 获取活动信息列表
        :param app_id: 应用标识
        :param act_name: 活动名称
        :param is_del: 是否回收站1是0否
        :param page_size: 条数
        :param page_index: 页数
        :param is_cache: 是否缓存
        :return: 
        :last_editors: HuangJianYi
        """
        order_by = "id asc"
        condition = "app_id=%s"
        params = [app_id]
        if is_del !=-1:
            condition += " and is_del=%s"
            params.append(is_del)
        if act_name:
            condition += " and act_name=%s"
            params.append(act_name)
        if is_cache:
            page_list, total = ActInfoModel(context=self.context).get_cache_dict_page_list(field="*", page_index=page_index, page_size=page_size, where=condition, group_by="", order_by=order_by, params=params,dependency_key=f"act_info_list:appid_{app_id}")
        else:
            page_list, total = ActInfoModel(context=self.context).get_dict_page_list(field="*", page_index=page_index, page_size=page_size, where=condition, group_by="", order_by=order_by, params=params)    
        for page in page_list:
            page["share_desc_json"] = SevenHelper.json_loads(page["share_desc_json"]) if page["share_desc_json"] else {}
            page["rule_desc_json"] = SevenHelper.json_loads(page["rule_desc_json"]) if page["rule_desc_json"] else []
            page["finish_menu_config_json"] = SevenHelper.json_loads(page["finish_menu_config_json"]) if page["finish_menu_config_json"] else []
            page["finish_status"] = page["is_finish"]
        return page_list, total

    def add_act_info(self,app_id,act_name,act_type,theme_id,share_desc_json,rule_desc_json,close_word="抱歉，程序维护中"):
        """
        :description: 添加活动信息
        :param app_id: 应用标识
        :param act_name: 活动名称
        :param act_type: 活动类型
        :param theme_id: 主题标识
        :param share_desc_json: 分享配置
        :param rule_desc_json: 规则配置
        :param close_word: 关闭文案
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data
        if not act_name:
            base_info_model = BaseInfoModel(context=self.context)
            base_info_dict = base_info_model.get_cache_dict()
            if not base_info_dict:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "基础信息不存在"
                return invoke_result_data
        act_type_model = ActTypeModel(context=self.context)
        act_type_info = act_type_model.get_entity("id=%s", params=act_type)
        if not act_type_info:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "活动类型信息不存在"
            return invoke_result_data

        now_datetime = SevenHelper.get_now_datetime()
        act_info_model = ActInfoModel(context=self.context)
        act_count = act_info_model.get_total("app_id=%s", params=[app_id])

        act_info = ActInfo()
        act_info.app_id = app_id
        act_info.act_name = base_info_dict["product_name"] + "_" + str(act_count + 1) if not act_name else act_name
        act_info.act_type = act_type
        act_info.theme_id = theme_id
        act_info.close_word = close_word
        act_info.share_desc_json = share_desc_json if share_desc_json else {}
        act_info.rule_desc_json = rule_desc_json if rule_desc_json else []
        act_info.start_date = now_datetime
        act_info.end_date = "2900-01-01 00:00:00"
        act_info.task_asset_type_json = act_type_info.task_asset_type_json
        act_info.is_release = 1
        act_info.release_date = now_datetime
        act_info.create_date = now_datetime
        act_info.modify_date = now_datetime
        act_info.id = act_info_model.add_entity(act_info)
        invoke_result_data.data = act_info
        self._delete_act_info_dependency_key(app_id,act_info.id)
        return invoke_result_data

    def update_act_info(self,app_id,act_id,act_name,theme_id,is_share,share_desc_json,is_rule,rule_desc_json,is_release,start_date,end_date,is_black,refund_count,join_ways,is_fictitious,close_word="抱歉，程序维护中",store_url=None,i1=-1,i2=-1,i3=-1,i4=-1,i5=-1,s1=None,s2=None,s3=None,s4=None,s5=None,d1=None,d2=None,is_visit_store=-1):
        """
        :description: 修改活动信息
        :param app_id: 应用标识
        :param act_id：活动标识
        :param act_name：活动名称
        :param is_release：是否发布
        :param theme_id: 主题标识
        :param is_share: 是否开启分享
        :param share_desc_json: 分享配置
        :param is_rule: 是否开启规则
        :param rule_desc_json: 规则配置
        :param start_date: 开始时间
        :param end_date: 结束时间
        :param close_word: 关闭文案
        :param is_black：是否开启退款惩罚
        :param refund_count：退款成功次数
        :param join_ways: 活动参与条件（0所有1关注店铺2加入会员3指定用户）
        :param is_fictitious: 是否开启虚拟中奖（1是0否）
        :param i1: i1
        :param i2: i2
        :param i3: i3
        :param i4: i4
        :param i5: i5
        :param s1: s1
        :param s2: s2
        :param s3: s3
        :param s4: s4
        :param s5: s5
        :param d1: d1
        :param d2: d2
        :param is_visit_store: 是否开启访问店铺
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        act_info_model = ActInfoModel(context=self.context)
        act_info = act_info_model.get_entity_by_id(act_id)
        if not act_info or act_info.app_id != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "no_act"
            invoke_result_data.error_message = "活动信息不存在"
            return invoke_result_data
        old_act_info = deepcopy(act_info)
        now_datetime = SevenHelper.get_now_datetime()
        if act_name !=None:
            act_info.act_name = act_name
        if is_release !=-1:
            act_info.is_release = is_release
        if theme_id !=-1:
            act_info.theme_id = theme_id
        if is_share !=-1:
            act_info.is_share = is_share
        if share_desc_json !=None:
            act_info.share_desc_json = share_desc_json
        if is_rule !=-1:
            act_info.is_rule = is_rule
        if rule_desc_json !=None:
            act_info.rule_desc_json = rule_desc_json
        if is_release !=-1:
            act_info.is_release = is_release
            act_info.release_date = now_datetime
        if start_date !=None:
            act_info.start_date = start_date
        if end_date !=None:
            act_info.end_date = end_date
        if is_black !=-1:
            act_info.is_black = is_black
        if refund_count !=-1:
            act_info.refund_count = refund_count
        if join_ways !=-1:
            act_info.join_ways = join_ways
        if is_fictitious !=-1:
            act_info.is_fictitious = is_fictitious
        if close_word !=None:
            act_info.close_word = close_word
        if is_visit_store !=-1:
            act_info.is_visit_store = is_visit_store
        if store_url !=None:
            act_info.store_url = store_url
        if i1 !=-1:
            act_info.i1 = i1
        if i2 !=-1:
            act_info.i2 = i2
        if i3 !=-1:
            act_info.i3 = i3
        if i4 !=-1:
            act_info.i4 = i4
        if i5 !=-1:
            act_info.i5 = i5
        if s1 !=None:
            act_info.s1 = s1
        if s2 !=None:
            act_info.s2 = s2
        if s3 !=None:
            act_info.s3 = s3
        if s4 !=None:
             act_info.s4 = s4
        if s5 !=None:
             act_info.s5 = s5
        if d1 !=None:
             act_info.d1 = d1
        if d2 !=None:
             act_info.d2 = d2
        act_info.modify_date = now_datetime
        act_info_model.update_entity(act_info,exclude_field_list="finish_menu_config_json,is_finish,task_asset_type_json,is_launch")
        result = {}
        result["old"] = old_act_info
        result["new"] = act_info
        invoke_result_data.data = result
        self._delete_act_info_dependency_key(app_id,act_info.id)
        return invoke_result_data
    
    def update_act_info_status(self,app_id,act_id,is_del):
        """
        :description: 删除或者还原活动
        :param app_id：应用标识
        :param act_id：活动标识
        :param is_del：0-还原，1-删除
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        act_info_model = ActInfoModel(context=self.context)
        act_info_dict = act_info_model.get_dict_by_id(act_id)
        if not act_info_dict or act_info_dict["app_id"]!=app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "no_act"
            invoke_result_data.error_message = "活动信息不存在"
            return invoke_result_data
        is_release = 0 if is_del == 1 else 1
        modify_date = SevenHelper.get_now_datetime()
        invoke_result_data.success = act_info_model.update_table("is_del=%s,is_release=%s,release_date=%s,modify_date=%s", "id=%s", [is_del, is_release, modify_date, modify_date, act_id])
        self._delete_act_info_dependency_key(app_id,act_id)
        return invoke_result_data

    def release_act_info(self,app_id,act_id,is_release):
        """
        :description: ip上下架
        :param app_id：应用标识
        :param act_id：活动标识
        :param is_release: 是否发布 1-是 0-否
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        act_info_model = ActInfoModel(context=self.context)
        act_info_dict = act_info_model.get_dict_by_id(act_id)
        if not act_info_dict or act_info_dict["app_id"]!=app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "no_act"
            invoke_result_data.error_message = "活动信息不存在"
            return invoke_result_data
        invoke_result_data.success = act_info_model.update_table("release_date=%s,is_release=%s", "id=%s", [SevenHelper.get_now_datetime(), is_release, act_id])
        self._delete_act_info_dependency_key(app_id,act_id)
        return invoke_result_data

    def next_progress(self,app_id,act_id,finish_key):
        """
        :description: 下一步配置
        :param app_id：应用标识
        :param finish_key：完成key，由前端控制是否完成配置，完成时需传参数值finish_config 代表最后一步
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        base_info_model = BaseInfoModel(context=self.context)
        base_info = base_info_model.get_entity()
        if not base_info:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "基础信息不存在"
            return invoke_result_data
        act_info_model = ActInfoModel(context=self.context)
        act_info = act_info_model.get_dict_by_id(act_id)
        if not act_info:
            invoke_result_data.success = False
            invoke_result_data.error_code = "no_act"
            invoke_result_data.error_message = "活动信息不存在"
            return invoke_result_data
        menu_config_json = SevenHelper.json_loads(base_info.menu_config_json)
        menu = [menu for menu in menu_config_json if menu["key"] == finish_key]
        if len(menu) == 0:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起，无此菜单"
            return invoke_result_data
        if act_info["finish_menu_config_json"] != "" and finish_key in act_info["finish_menu_config_json"]:
            return invoke_result_data
        if act_info["finish_menu_config_json"] == "":
            act_info["finish_menu_config_json"] = "[]"
        finish_menu_config_json = SevenHelper.json_loads(act_info["finish_menu_config_json"])
        finish_menu_config_json.append(finish_key)

        result_finish_menu_config_json = []
        for item in finish_menu_config_json:
            is_exist = [item2 for item2 in menu_config_json if item2["key"] == item]
            if len(is_exist) > 0:
                result_finish_menu_config_json.append(item)
        is_finish = 0
        if finish_key == "finish_config" and act_info["is_finish"] == 0:
            is_finish = 1
        result_finish_menu_config_json = SevenHelper.json_dumps(result_finish_menu_config_json)
        act_info_model.update_table("finish_menu_config_json=%s,is_finish=%s", "id=%s", [result_finish_menu_config_json, is_finish, act_id])
        app_id = self.get_app_id()
        if is_finish == 1 and app_id:
            app_info_model = AppInfoModel(context=self.context)
            app_info_model.update_table("is_setting=1", "app_id=%s", [app_id])
        return invoke_result_data
  
    