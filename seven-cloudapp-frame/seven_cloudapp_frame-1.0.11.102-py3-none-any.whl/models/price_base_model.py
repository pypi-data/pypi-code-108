# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 14:26:29
@LastEditTime: 2022-01-13 14:56:01
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.act_base_model import *
from seven_cloudapp_frame.models.launch_base_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *


class PriceBaseModel():
    """
    :description: 价格档位业务模型
    """
    def __init__(self, context=None,logging_error=None, logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def _delete_price_gear_dependency_key(self,act_id):
        """
        :description: 删除价格档位依赖建
        :param act_id: 活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            redis_init = SevenHelper.redis_init()
            if act_id:
                redis_init.delete(f"price_gear_list:actid_{act_id}")
        except Exception as ex:
            pass

    def save_price_gear(self,app_id,act_id,price_gear_id,relation_type,price_gear_name,price_gear_pic,price,goods_id,sku_id,remark=""):
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
        invoke_result_data = InvokeResultData()
        price_gear = None
        old_price_gear = None
        price_gear_model = PriceGearModel(context=self.context)
        if price_gear_id > 0:
            price_gear = price_gear_model.get_entity_by_id(price_gear_id)
        is_add = False
        if not price_gear:
            is_add = True
            price_gear = PriceGear()
        else:
            old_price_gear = deepcopy(price_gear)
        try:
            price = decimal.Decimal(price)
        except Exception as ex:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "参数price类型错误"
            return invoke_result_data

        if goods_id != "":
            price_gear_goodsid = price_gear_model.get_entity("act_id!=%s and goods_id=%s", params=[act_id, goods_id])
            if price_gear_goodsid:
                act_info_dict = ActInfoModel(context=self.context).get_dict_by_id(price_gear_goodsid.act_id)
                act_name = act_info_dict["act_name"] if act_info_dict else ""
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = f"此商品ID已关联活动{act_name},无法使用"
                return invoke_result_data

        price_gear.app_id = app_id
        price_gear.act_id = act_id
        price_gear.relation_type = relation_type
        price_gear.price = price
        price_gear.price_gear_name = price_gear_name
        price_gear.price_gear_pic = price_gear_pic
        price_gear.goods_id = goods_id
        price_gear.sku_id = sku_id
        price_gear.remark = remark
        price_gear.modify_date = SevenHelper.get_now_datetime()

        if is_add:
            if sku_id != "":
                price_gear_goodsid_skuid = price_gear_model.get_total("sku_id=%s", params=[sku_id])
                if price_gear_goodsid_skuid:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = f"当前SKUID已绑定价格档位,请更换"
                    return invoke_result_data
            price_gear.create_date = SevenHelper.get_now_datetime()
            price_gear.effective_date = SevenHelper.get_now_datetime()
            price_gear.id = price_gear_model.add_entity(price_gear)
        else:
            if sku_id != "":
                price_gear_goodsid_skuid = price_gear_model.get_total("id!=%s and sku_id=%s", params=[price_gear.id, sku_id])
                if price_gear_goodsid_skuid:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = f"当前SKUID已绑定价格档位,请更换"
                    return invoke_result_data
            price_gear_model.update_entity(price_gear)

        launch_goods_id = price_gear.goods_id if price_gear else ''
        old_goods_id = old_price_gear.goods_id if old_price_gear else ''
        launch_base_model = LaunchBaseModel(context=self.context)
        launch_base_model.add_launch_goods(app_id,act_id, launch_goods_id, old_goods_id,"2")

        result = {}
        result["is_add"] = is_add
        result["new"] = price_gear
        result["old"] = old_price_gear
        invoke_result_data.data = result
        self._delete_price_gear_dependency_key(act_id)
        return invoke_result_data

    def get_price_gear_list(self,app_id,act_id,page_size,page_index,order_by="id desc",is_del=0,is_cache=True):
        """
        :description: 获取价格档位列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param page_index：页索引
        :param page_size：页大小
        :param order_by：排序
        :param is_del：是否回收站1是0否
        :param is_cache：是否缓存
        :return: list
        :last_editors: HuangJianYi
        """
        condition = "app_id=%s and act_id=%s"
        if is_del == 1:
            condition+=" and is_del=1"
        else:
            condition+=" and is_del=0"

        params = [app_id,act_id]
        price_gear_model = PriceGearModel(context=self.context)
        if is_cache == True:
            page_list, total = price_gear_model.get_cache_dict_page_list(field="*", page_index=page_index, page_size=page_size, where=condition, group_by="", order_by=order_by,params=params,dependency_key=f"price_gear_list:actid_{act_id}")
        else:
            page_list, total = price_gear_model.get_dict_page_list(field="*", page_index=page_index, page_size=page_size, where=condition, group_by="", order_by=order_by,params=params)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info

    def update_price_gear_status(self,app_id,act_id,price_gear_id,is_del):
        """
        :description: 删除或恢复价格档位
        :param app_id：应用标识
        :param act_id：活动标识
        :param price_gear_id：价格档位标识
        :param is_del：1删除0恢复
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        price_gear_model = PriceGearModel(context=self.context)
        price_gear_dict = price_gear_model.get_dict_by_id(price_gear_id)
        if not price_gear_dict or price_gear_dict["act_id"] != act_id or price_gear_dict["app_id"] != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "价格档位信息不存在"
            return invoke_result_data
        goods_id =  price_gear_dict["goods_id"]
        invoke_result_data.success = price_gear_model.update_table("is_del=%s,goods_id='',sku_id=''", "id=%s", [is_del, price_gear_id])
        if invoke_result_data.success ==True and is_del == 1:
            launch_base_model = LaunchBaseModel(context=self.context)
            launch_base_model.update_launch_goods(act_id, goods_id,"2")
        self._delete_price_gear_dependency_key(act_id)
        return invoke_result_data

    def check_price_gear(self,app_id,act_id,price_gear_id,goods_id,sku_id):
        """
        :description: 验证价格档位
        :param app_id：应用标识
        :param act_id：活动标识
        :param price_gear_id：价格档位标识
        :param goods_id：商品ID
        :param sku_id：sku_id
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        price_gear_model = PriceGearModel(context=self.context)
        condtion = "app_id=%s and goods_id=%s"
        params = [app_id, goods_id]
        if price_gear_id > 0:
            condtion += " and id!=%s"
            params.append(price_gear_id)
        price_gear_dict_list = price_gear_model.get_dict_list(condtion, params=params)
        is_fail = False
        bind_act_id = 0
        if price_gear_dict_list:
            if not sku_id:
                is_fail = True
                bind_act_id = price_gear_dict_list[0]["act_id"]
            else:
                for price_gear_dict in price_gear_dict_list:
                    if price_gear_dict["relation_type"] == 1 or price_gear_dict["sku_id"] == sku_id:
                        is_fail = True
                        bind_act_id = int(price_gear_dict["act_id"])
                        break
        #验证失败
        if is_fail == True:
            if act_id == bind_act_id:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "对不起,该商品已绑定其他价格档位"
                return invoke_result_data
            else:
                act_info = ActInfoModel(context=self.context).get_cache_entity_by_id(bind_act_id)
                if act_info:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "对不起,该商品已绑定" + act_info.act_name + "活动"
                    return invoke_result_data
        return invoke_result_data
