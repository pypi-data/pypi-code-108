# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-03 15:42:53
@LastEditTime: 2022-01-21 21:27:46
@LastEditors: HuangJianYi
@Description: 活动模块
"""
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.act_base_model import *
from seven_cloudapp_frame.models.seven_model import PageInfo


class ActTypeListHandler(ClientBaseHandler):
    """
    :description: 获取活动类型列表
    """
    def get_async(self):
        """
        :description: 获取活动类型列表
        :param marketing_id：营销方案标识
        :param is_act：当前类型是否创建过活动
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        is_act = int(self.get_param("is_act", 0))
        marketing_id = int(self.get_param("marketing_id", 0))
        condition = "market_ids LIKE '%," + str(marketing_id) + ",%'" if marketing_id > 0 else ""
        act_type_list = ActTypeModel(context=self).get_cache_list(where=condition)
        new_list = []
        for act_type in act_type_list:
            act_type.play_process_json = self.json_loads(act_type.play_process_json) if act_type.play_process_json else {}
            act_type.suit_behavior_json = self.json_loads(act_type.suit_behavior_json) if act_type.suit_behavior_json else {}
            act_type.market_function_json = self.json_loads(act_type.market_function_json) if act_type.market_function_json else {}
            act_type.type_desc = self.json_loads(act_type.type_desc) if act_type.type_desc else []
            act_type.task_asset_type_json = self.json_loads(act_type.task_asset_type_json) if act_type.task_asset_type_json else []
            if is_act > 0 and app_id:
                act_dict = ActInfoModel(context=self).get_cache_dict("app_id=%s and act_type=%s", limit="1", field="id", params=[app_id, act_type.id])
                if act_dict:
                    act_type.act_id = act_dict['id']
                else:
                    act_type.act_id = 0
            new_list.append(act_type.__dict__)
        return self.response_json_success(new_list)


class AddActInfoHandler(ClientBaseHandler):
    """
    :description: 添加活动信息
    """
    @filter_check_params("act_type")
    def get_async(self):
        """
        :description: 添加活动信息
        :param app_id：应用标识
        :param act_name: 活动名称
        :param act_type: 活动类型
        :param theme_id: 主题标识
        :param share_desc_json: 分享配置
        :param rule_desc_json: 规则配置
        :param close_word: 关闭文案
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_name = self.get_param("act_name")
        act_type = int(self.get_param("act_type", 0))
        theme_id = int(self.get_param("theme_id", 0))
        close_word = self.get_param("close_word","抱歉，程序维护中")
        share_desc_json = self.get_param("share_desc_json", "")
        rule_desc_json = self.get_param("rule_desc_json", "")

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        act_base_model = ActBaseModel(context=self)
        invoke_result_data = act_base_model.add_act_info(app_id, act_name, act_type, theme_id, share_desc_json, rule_desc_json, close_word)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.create_operation_log(OperationType.add.value, "act_info_tb", "AddActInfoHandler", None, self.json_dumps(invoke_result_data.data))
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data.id)


class UpdateActInfoHandler(ClientBaseHandler):
    """
    :description: 修改活动信息
    """
    @filter_check_params("act_id")
    def post_async(self):
        """
        :description: 修改活动信息
        :param app_id：应用标识
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
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        act_name = self.get_param("act_name", None)
        theme_id = int(self.get_param("theme_id", -1))
        is_share = int(self.get_param("is_share", -1))
        share_desc_json = self.get_param("share_desc_json", None)
        is_rule = int(self.get_param("is_rule", -1))
        rule_desc_json = self.get_param("rule_desc_json", None)
        is_release = int(self.get_param("is_release", -1))
        start_date = self.get_param("start_date", None)
        end_date = self.get_param("end_date", None)
        is_black = int(self.get_param("is_black", -1))
        refund_count = int(self.get_param("refund_count", -1))
        join_ways = int(self.get_param("join_ways", -1))
        is_fictitious = int(self.get_param("is_fictitious", -1))
        close_word = self.get_param("close_word", None)
        is_visit_store = int(self.get_param("is_visit_store", -1))
        store_url = self.get_param("store_url", None)
        i1 = int(self.get_param("i1", -1))
        i2 = int(self.get_param("i2", -1))
        i3 = int(self.get_param("i3", -1))
        i4 = int(self.get_param("i4", -1))
        i5 = int(self.get_param("i5", -1))
        s1 = self.get_param("s1", None)
        s2 = self.get_param("s2", None)
        s3 = self.get_param("s3", None)
        s4 = self.get_param("s4", None)
        s5 = self.get_param("s5", None)
        d1 = self.get_param("d1", None)
        d2 = self.get_param("d2", None)

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        act_base_model = ActBaseModel(context=self)
        invoke_result_data = act_base_model.update_act_info(app_id, act_id, act_name, theme_id, is_share, share_desc_json, is_rule, rule_desc_json, is_release, start_date, end_date, is_black, refund_count, join_ways, is_fictitious, close_word, store_url, i1, i2, i3, i4, i5, s1, s2, s3, s4, s5, d1, d2, is_visit_store)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.create_operation_log(OperationType.update.value, "act_info_tb", "UpdateActInfoHandler", self.json_dumps(invoke_result_data.data["old"]), self.json_dumps(invoke_result_data.data["new"]))
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()


class ActInfoListHandler(ClientBaseHandler):
    """
    :description: 活动列表
    """
    def get_async(self):
        """
        :description: 获取活动列表
        :param app_id：应用标识
        :param act_name: 活动名称
        :param is_del: 是否回收站1是0否
        :param page_size: 条数
        :param page_index: 页数
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        is_del = int(self.get_param("is_del", -1))
        act_name = self.get_param("act_name")

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})
        if not app_id:
            return self.response_json_success({"data": []})
        act_base_model = ActBaseModel(context=self)
        page_list, total = act_base_model.get_act_info_list(app_id, act_name, is_del, page_size, page_index,False)
        for page in page_list:
            page["online_url"] = self.get_online_url(page['id'], app_id)
            page["live_url"] = self.get_live_url(app_id)
        ref_params = {}
        page_info = PageInfo(page_index, page_size, total, self.business_process_executed(page_list, ref_params))
        return self.response_json_success(page_info)


class ActInfoHandler(ClientBaseHandler):
    """
    :description: 获取活动信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取活动信息
        :param app_id：应用标识
        :param act_id：活动标识
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        act_base_model = ActBaseModel(context=self)
        act_info_dict = act_base_model.get_act_info_dict(act_id, False, False)
        if act_info_dict:
            if act_info_dict["app_id"] != app_id:
                act_info_dict = {}
                return self.response_json_success(act_info_dict)
            act_info_dict["share_desc_json"] = self.json_loads(act_info_dict["share_desc_json"]) if act_info_dict["share_desc_json"] else {}
            act_info_dict["rule_desc_json"] = self.json_loads(act_info_dict["rule_desc_json"]) if act_info_dict["rule_desc_json"] else []
            act_info_dict["finish_menu_config_json"] = self.json_loads(act_info_dict["finish_menu_config_json"]) if act_info_dict["finish_menu_config_json"] else []
            act_info_dict['online_url'] = self.get_online_url(act_info_dict['id'], act_info_dict['app_id'])
            act_info_dict['live_url'] = self.get_live_url(act_info_dict['app_id'])
        ref_params = {}
        return self.response_json_success(self.business_process_executed(act_info_dict, ref_params))


class DeleteActInfoHandler(ClientBaseHandler):
    """
    :description: 删除活动
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 删除活动
        :param app_id：应用标识
        :param act_id：活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        act_base_model = ActBaseModel(context=self)
        invoke_result_data = act_base_model.update_act_info_status(app_id, act_id, 1)
        if invoke_result_data.success ==False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.create_operation_log(OperationType.delete.value, "act_info_tb", "DeleteActInfoHandler", None, act_id)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()


class ReviewActInfoHandler(ClientBaseHandler):
    """
    :description: 还原活动
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 还原活动
        :param app_id：应用标识
        :param act_id：活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        act_base_model = ActBaseModel(context=self)
        invoke_result_data = act_base_model.update_act_info_status(app_id, act_id, 0)
        if invoke_result_data.success ==False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.create_operation_log(OperationType.review.value, "act_info_tb", "DeleteActInfoHandler", None, act_id)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()


class ReleaseActInfoHandler(ClientBaseHandler):
    """
    :description: 上下架活动
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 上下架活动
        :param app_id：应用标识
        :param act_id：活动标识
        :param is_release: 是否发布 1-是 0-否
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        is_release = int(self.get_param("is_release", 0))
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        act_base_model = ActBaseModel(context=self)
        invoke_result_data = act_base_model.release_act_info(app_id, act_id, is_release)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()


class CreateActQrCodeHandler(ClientBaseHandler):
    """
    :description: 创建活动二维码
    """
    @filter_check_params("url")
    def get_async(self):
        """
        :description: 创建活动二维码
        :param act_id：活动标识
        :return: 活动二维码图片
        :last_editors: HuangJianYi
        """
        url = self.get_param("url")
        img, img_bytes = QRCodeHelper.create_qr_code(url, fill_color="black")
        img_base64 = base64.b64encode(img_bytes).decode()
        return self.response_json_success(f"data:image/jpeg;base64,{img_base64}")


class NextProgressHandler(ClientBaseHandler):
    """
    :description: 下一步配置
    """
    @filter_check_params("act_id,finish_key")
    def get_async(self):
        """
        :description: 下一步配置
        :param app_id：应用标识
        :param act_id：活动标识
        :param finish_key：完成key，由前端控制是否完成配置，完成时需传参数值finish_config 代表最后一步
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        finish_key = self.get_param("finish_key")

        act_base_model = ActBaseModel(context=self)
        invoke_result_data = act_base_model.next_progress(app_id, act_id, finish_key)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()