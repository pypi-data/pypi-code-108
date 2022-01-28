# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 14:25:02
@LastEditTime: 2021-11-29 16:39:56
@LastEditors: HuangJianYi
@Description: 价格档位模块
"""
from seven_cloudapp_frame.models.price_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *


class SavePriceGearHandler(ClientBaseHandler):
    """
    :description: 保存价格档位信息
    """
    @filter_check_params("act_id,price")
    def get_async(self):
        """
        :description: 保存价格档位
        :param app_id：应用标识
        :param act_id：活动标识
        :param price_gear_id：价格档位标识
        :param relation_type：关联类型：1商品skuid关联2商品id关联
        :param price_gear_name：档位名称
        :param price_gear_pic：档位图片
        :param price：价格
        :param goods_id：商品ID
        :param sku_id：sku_id
        :param remark：备注
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        price_gear_id = int(self.get_param("price_gear_id", 0))
        relation_type = int(self.get_param("relation_type", 1))
        price = self.get_param("price")
        price_gear_name = self.get_param("price_gear_name")
        price_gear_pic = self.get_param("price_gear_pic")
        goods_id = self.get_param("goods_id")
        sku_id = self.get_param("sku_id")
        remark = self.get_param("remark")

        price_base_model = PriceBaseModel(context=self)
        invoke_result_data = price_base_model.save_price_gear(app_id, act_id, price_gear_id, relation_type, price_gear_name, price_gear_pic, price, goods_id, sku_id,remark)
        if invoke_result_data.success ==False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if invoke_result_data.data["is_add"] == True:
            # 记录日志
            self.create_operation_log(OperationType.add.value, invoke_result_data.data["new"].__str__(), "SavePriceGearHandler", None, self.json_dumps(invoke_result_data.data["new"]), self.get_open_id(), self.get_user_nick())
        else:
            self.create_operation_log(OperationType.update.value, invoke_result_data.data["new"].__str__(), "SavePriceGearHandler", self.json_dumps(invoke_result_data.data["old"]), self.json_dumps(invoke_result_data.data["new"]), self.get_open_id(), self.get_user_nick())

        return self.response_json_success(invoke_result_data.data["new"].id)


class PriceGearListHandler(ClientBaseHandler):
    """
    :description: 获取价格档位列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取价格档位列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param page_index：页索引
        :param page_size：页大小
        :param is_del：是否回收站1是0否
        :return: list
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        is_del = int(self.get_param("is_del", 0))

        return self.response_json_success(PriceBaseModel(context=self).get_price_gear_list(app_id, act_id, page_size, page_index,is_del=is_del,is_cache=False))


class DeletePriceGearHandler(ClientBaseHandler):
    """
    :description: 删除档位
    """
    @filter_check_params("price_gear_id")
    def get_async(self):
        """
        :description: 删除档位
        :param app_id：应用标识
        :param act_id：活动标识
        :param price_gear_id：价格档位标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        price_gear_id = int(self.get_param("price_gear_id", 0))

        price_base_model = PriceBaseModel(context=self)
        invoke_result_data = price_base_model.update_price_gear_status(app_id, act_id, price_gear_id, 1)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.create_operation_log(OperationType.delete.value, "price_gear_tb", "DeletePriceGearHandler", None, price_gear_id)
        return self.response_json_success()


class ReviewPriceGearHandler(ClientBaseHandler):
    """
    :description: 恢复价格档位
    """
    @filter_check_params("price_gear_id")
    def get_async(self):
        """
        :description: 恢复价格档位
        :param app_id：应用标识
        :param act_id：活动标识
        :param price_gear_id：价格档位标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        price_gear_id = int(self.get_param("price_gear_id", 0))

        price_base_model = PriceBaseModel(context=self)
        invoke_result_data = price_base_model.update_price_gear_status(app_id, act_id, price_gear_id, 0)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        self.create_operation_log(OperationType.review.value, "price_gear_tb", "ReviewPriceGearHandler", None, price_gear_id)
        return self.response_json_success()


class CheckPriceGearHandler(ClientBaseHandler):
    """
    :description: 验证价格档位
    """
    @filter_check_params("act_id,goods_id")
    def get_async(self):
        """
        :description: 验证价格档位
        :param app_id：应用标识
        :param act_id：活动标识
        :param price_gear_id：价格档位标识
        :param goods_id：商品ID
        :param sku_id：sku_id
        :return: response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        price_gear_id = int(self.get_param("price_gear_id", 0))
        goods_id = self.get_param("goods_id")
        sku_id = self.get_param("sku_id")

        price_base_model = PriceBaseModel(context=self)
        invoke_result_data = price_base_model.check_price_gear(app_id, act_id, price_gear_id, goods_id, sku_id)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()
