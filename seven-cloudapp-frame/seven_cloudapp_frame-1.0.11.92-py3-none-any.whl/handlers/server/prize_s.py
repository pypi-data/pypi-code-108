# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-03 15:42:53
@LastEditTime: 2022-01-07 10:56:16
@LastEditors: HuangJianYi
@Description: 奖品模块
"""
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.act_base_model import *
from seven_cloudapp_frame.models.prize_base_model import *
from seven_cloudapp_frame.models.seven_model import PageInfo
from seven_cloudapp_frame.libs.customize.oss2_helper import *


class SaveActPrizeHandler(ClientBaseHandler):
    """
    :description: 保存活动奖品
    """
    @filter_check_params("act_id")
    def post_async(self):
        """
        :description: 保存活动奖品
        :param app_id：应用标识
        :param act_id: 活动标识
        :param module_id: 活动模块标识
        :param prize_id: 奖品标识
        :param prize_name: 奖品名称
        :param prize_title: 奖品子标题
        :param prize_pic: 奖品图
        :param prize_detail_json: 奖品详情图（json）
        :param goods_id: 商品ID
        :param goods_code: 商品编码
        :param goods_code_list: 多个sku商品编码
        :param goods_type: 物品类型（1虚拟2实物）
        :param prize_type: 奖品类型(1现货2优惠券3红包4参与奖、谢谢参与5预售)
        :param prize_price: 奖品价值
        :param probability: 奖品权重
        :param chance: 概率
        :param prize_limit: 中奖限制数
        :param is_prize_notice: 是否显示跑马灯(1是0否)
        :param prize_total: 奖品总数
        :param is_surplus: 是否显示奖品库存（1显示0-不显示）
        :param lottery_type: 出奖类型（1概率出奖 2强制概率）
        :param tag_name: 标签名称(奖项名称)
        :param tag_id: 标签ID(奖项标识)
        :param is_sku: 是否有SKU
        :param sku_json: sku详情json 注意：所有的参数只能是整形或字符串，如果是对象的参数必须先序列化
        :param sort_index: 排序
        :param is_release: 是否发布（1是0否）
        :param ascription_type: 奖品归属类型（0-活动奖品1-任务奖品）
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
        module_id = int(self.get_param("module_id", 0))
        prize_id = int(self.get_param("prize_id", 0))
        prize_name = self.get_param("prize_name")
        prize_title = self.get_param("prize_title")
        prize_pic = self.get_param("prize_pic")
        prize_detail_json = self.get_param("prize_detail_json")
        goods_id = self.get_param("goods_id")
        goods_code = self.get_param("goods_code")
        goods_code_list = self.get_param("goods_code_list")
        goods_type = int(self.get_param("goods_type", 0))
        prize_type = int(self.get_param("prize_type", 0))
        prize_price = self.get_param("prize_price")
        probability = self.get_param("probability")
        chance = self.get_param("chance")
        prize_limit = int(self.get_param("prize_limit", 0))
        is_prize_notice = int(self.get_param("is_prize_notice", 0))
        prize_total = int(self.get_param("prize_total", 0))
        is_surplus = int(self.get_param("is_surplus", 0))
        lottery_type = int(self.get_param("lottery_type", 0))
        tag_name = self.get_param("tag_name")
        tag_id = int(self.get_param("tag_id", 0))
        is_sku = int(self.get_param("is_sku", 0))
        sku_json = self.get_param("sku_json")
        ascription_type = int(self.get_param("ascription_type", 0))
        sort_index = int(self.get_param("sort_index", 0))
        is_release = int(self.get_param("is_release", 0))
        i1 = int(self.get_param("i1", 0))
        i2 = int(self.get_param("i2", 0))
        i3 = int(self.get_param("i3", 0))
        i4 = int(self.get_param("i4", 0))
        i5 = int(self.get_param("i5", 0))
        s1 = self.get_param("s1")
        s2 = self.get_param("s2")
        s3 = self.get_param("s3")
        s4 = self.get_param("s4")
        s5 = self.get_param("s5")
        d1 = self.get_param("d1", "1900-01-01 00:00:00")
        d2 = self.get_param("d2", "1900-01-01 00:00:00")

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        prize_total = invoke_result_data.data["prize_total"] if invoke_result_data.data.__contains__("prize_total") else prize_total
        prize_base_model = PrizeBaseModel(context=self)
        invoke_result_data = prize_base_model.save_act_prize(app_id, act_id, module_id, prize_id, prize_name, prize_title, prize_pic, prize_detail_json, goods_id, goods_code, goods_code_list, goods_type, prize_type, prize_price, probability, chance, prize_limit, is_prize_notice, prize_total, is_surplus, lottery_type, tag_name, tag_id, is_sku, sku_json, sort_index, is_release, ascription_type, i1, i2, i3, i4, i5, s1, s2, s3, s4, s5, d1, d2)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if invoke_result_data.data["is_add"] == True:
            # 记录日志
            self.create_operation_log(OperationType.add.value, invoke_result_data.data["new"].__str__(), "SaveActPrizeHandler", None, self.json_dumps(invoke_result_data.data["new"]), self.get_open_id(), self.get_user_nick())
        else:
            self.create_operation_log(OperationType.update.value, invoke_result_data.data["new"].__str__(), "SaveActPrizeHandler", self.json_dumps(invoke_result_data.data["old"]), self.json_dumps(invoke_result_data.data["new"]), self.get_open_id(), self.get_user_nick())
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data["new"].id)


class ActPrizeListHandler(ClientBaseHandler):
    """
    :description: 活动奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 活动奖品列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param prize_name：奖品名称
        :param is_del：是否回收站1是0否
        :param page_index：页索引
        :param page_size：页大小
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        prize_name = self.get_param("prize_name")
        is_del = int(self.get_param("is_del", -1))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        condition = invoke_result_data.data["condition"] if invoke_result_data.data.__contains__("condition") else ""
        params = invoke_result_data.data["params"] if invoke_result_data.data.__contains__("params") else []
        order_by = invoke_result_data.data["order_by"] if invoke_result_data.data.__contains__("order_by") else "sort_index desc,id asc"
        field = invoke_result_data.data["field"] if invoke_result_data.data.__contains__("field") else "*"
        if not app_id or not act_id:
            return self.response_json_success({"data": []})
        prize_base_model = PrizeBaseModel(context=self)
        page_list, total = prize_base_model.get_act_prize_list(app_id, act_id, module_id, prize_name, 0, is_del, page_size, page_index, order_by=order_by, condition=condition, params=params, field=field, is_cache=False)
        ref_params = {}
        page_info = PageInfo(page_index, page_size, total, self.business_process_executed(page_list, ref_params))
        return self.response_json_success(page_info)


class DeleteActPrizeHandler(ClientBaseHandler):
    """
    :description: 删除活动奖品
    """
    @filter_check_params("prize_id")
    def get_async(self):
        """
        :description: 删除活动奖品
        :param app_id：应用标识
        :param prize_id：奖品标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        prize_id = int(self.get_param("prize_id", 0))
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        prize_base_model = PrizeBaseModel(context=self)
        invoke_result_data = prize_base_model.update_act_prize_status(app_id, prize_id, 1)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.create_operation_log(OperationType.delete.value, "act_prize_tb", "DeleteActPrizeHandler", None, prize_id)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()


class ReviewActPrizeHandler(ClientBaseHandler):
    """
    :description: 还原活动奖品
    """
    @filter_check_params("prize_id")
    def get_async(self):
        """
        :description: 还原活动奖品
        :param app_id：应用标识
        :param prize_id：奖品标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        prize_id = int(self.get_param("prize_id", 0))
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        prize_base_model = PrizeBaseModel(context=self)
        invoke_result_data = prize_base_model.update_act_prize_status(app_id, prize_id, 0)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.create_operation_log(OperationType.review.value, "act_prize_tb", "ReviewActPrizeHandler", None, prize_id)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()


class ReleaseActPrizeHandler(ClientBaseHandler):
    """
    :description: 上下架活动奖品
    """
    @filter_check_params("prize_id")
    def get_async(self):
        """
        :description: 上下架活动奖品
        :param app_id：应用标识
        :param prize_id 奖品标识
        :param is_release: 是否发布 1-是 0-否
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        prize_id = int(self.get_param("prize_id", 0))
        is_release = int(self.get_param("is_release", 0))
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        prize_base_model = PrizeBaseModel(context=self)
        invoke_result_data = prize_base_model.release_act_prize(app_id, prize_id, is_release)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()


class ActPrizeExportHandler(ClientBaseHandler):
    """
    :description: 导出活动奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 导出活动奖品列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param prize_name：奖品名称
        :param is_del：是否回收站1是0否
        :param page_size：页大小
        :param page_index：页索引
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        prize_name = self.get_param("prize_name")
        is_del = int(self.get_param("is_del", -1))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 500))

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success("")
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        condition = invoke_result_data.data["condition"] if invoke_result_data.data.__contains__("condition") else ""
        params = invoke_result_data.data["params"] if invoke_result_data.data.__contains__("params") else []
        order_by = invoke_result_data.data["order_by"] if invoke_result_data.data.__contains__("order_by") else "create_date desc"
        field = invoke_result_data.data["field"] if invoke_result_data.data.__contains__("field") else "*"

        prize_base_model = PrizeBaseModel(context=self)
        act_prize_list_dict = []
        if page_size <= 500:
            act_prize_list_dict = prize_base_model.get_act_prize_list(app_id, act_id, module_id, prize_name, 0, is_del, page_size, page_index, order_by=order_by, condition=condition, params=params, field=field, is_cache=False).data
        else:
            max_page_size = 100
            repeat_count = page_size // max_page_size  # 循环次数
            begin_page_index = page_index * repeat_count  # 开始页码
            for i in range(repeat_count):
                list_dict = prize_base_model.get_act_prize_list(app_id, act_id, module_id, prize_name, 0, is_del, max_page_size, begin_page_index + i, order_by=order_by, condition=condition, params=params, field=field, is_cache=False).data
                if len(list_dict) <= 0:
                    break
                act_prize_list_dict.extend(list_dict)
        ref_params = {}
        result_data = self.business_process_executed(act_prize_list_dict, ref_params)
        resource_path = OSS2Helper.export_excel(result_data)
        return self.response_json_success(resource_path)

    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data:result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        result_list = []
        for act_prize_dict in result_data:
            data_row = {}
            data_row["奖品名称"] = act_prize_dict["prize_name"]
            data_row["奖品子标题"] = act_prize_dict["prize_title"]
            data_row["奖品图"] = act_prize_dict["prize_pic"]
            data_row["商品ID"] = act_prize_dict["goods_id"]
            data_row["商家编码"] = act_prize_dict["goods_code"]
            data_row["奖品类型"] = act_prize_dict["prize_type"]
            data_row["奖品价值"] = str(act_prize_dict["prize_price"])
            data_row["奖品库存"] = act_prize_dict["surplus"]
            data_row["奖品总库存"] = act_prize_dict["prize_total"]
            if act_prize_dict["prize_type"] == 1:
                data_row["奖品类型"] = "现货"
            elif act_prize_dict["prize_type"] == 2:
                data_row["奖品类型"] = "优惠券"
            elif act_prize_dict["prize_type"] == 3:
                data_row["奖品类型"] = "红包"
            elif act_prize_dict["prize_type"] == 4:
                data_row["奖品类型"] = "参与奖"
            else:
                data_row["奖品类型"] = "预售"
            data_row["创建时间"] = TimeHelper.datetime_to_format_time(act_prize_dict["create_date"])
            data_row["是否发布"] = "未发布"
            if act_prize_dict["is_release"] == 1:
                data_row["是否发布"] = "已发布"
            result_list.append(data_row)
        return result_list