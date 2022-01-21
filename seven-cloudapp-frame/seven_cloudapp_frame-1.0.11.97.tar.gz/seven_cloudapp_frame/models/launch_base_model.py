from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.act_base_model import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *
from seven_cloudapp_frame.models.db_models.launch.launch_goods_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *

class LaunchBaseModel():
    """
    :description: 淘宝商品投放业务模型
    """
    def __init__(self, context=None, logging_error=None, logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def add_launch_goods(self, app_id, act_id, goods_id, old_goods_id, source_types):
        """
        :description: 添加商品投放
        :param app_id：应用标识
        :param act_id：活动标识
        :param goods_id：投放商品ID
        :param old_goods_id：旧投放商品ID，投放商品ID和旧投放商品ID不同的话，改变原该投放商品的状态
        :param source_types：商品来源（1活动奖品2价格档位） 多个逗号,分隔
        :return 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        now_datetime = SevenHelper.get_now_datetime()
        act_base_model = ActBaseModel(context=self.context)
        launch_goods_model = LaunchGoodsModel(context=self.context)
        act_info_dict = act_base_model.get_act_info_dict(act_id)
        invoke_result_data = InvokeResultData()
        if act_info_dict and act_info_dict["is_launch"] == 0:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "无法进行投放"
            return invoke_result_data
        if not goods_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "投放商品ID不能为空或0"
            return invoke_result_data
        if goods_id != old_goods_id and old_goods_id:
            is_update = True
            if source_types:
                source_types = list(set(source_types.split(',')))
            for item in source_types:
                if int(item) == 1:
                    act_prize_total = ActPrizeModel(context=self.context).get_total("act_id=%s and goods_id=%s", params=[act_id, old_goods_id])
                    if act_prize_total > 0 :
                        is_update = False
                elif int(item) == 2:
                    price_gear_total = PriceGearModel(context=self.context).get_total("act_id=%s and goods_id=%s", params=[act_id, old_goods_id])
                    if price_gear_total > 0 :
                        is_update = False
            if is_update == True:
                launch_goods_model.update_table("is_launch=0,is_sync=0,launch_date=%s", "act_id=%s and goods_id=%s", params=[SevenHelper.get_now_datetime(), act_id, old_goods_id])

        total = launch_goods_model.get_total("act_id=%s and goods_id=%s", params=[act_id, goods_id])
        if total <= 0:
            launch_goods = LaunchGoods()
            launch_goods.app_id = app_id
            launch_goods.act_id = act_id
            launch_goods.goods_id = goods_id
            launch_goods.is_launch = 0
            launch_goods.is_sync = 0
            launch_goods.create_date = now_datetime
            launch_goods.launch_date = now_datetime
            launch_goods.sync_date = now_datetime
            launch_goods_model.add_entity(launch_goods)

        return invoke_result_data

    def update_launch_goods(self, act_id, goods_id, source_types):
        """
        :description: 修改投放商品为未投放未同步
        :param app_id：应用标识
        :param act_id：活动标识
        :param goods_id：投放商品ID
        :param source_types：商品来源（1活动奖品商品2价格档位商品） 多个逗号,分隔
        :return 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        act_base_model = ActBaseModel(context=self.context)
        launch_goods_model = LaunchGoodsModel(context=self.context)
        act_info_dict = act_base_model.get_act_info_dict(act_id)
        invoke_result_data = InvokeResultData()
        if act_info_dict and act_info_dict["is_launch"] == 0:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "无法进行投放"
            return invoke_result_data
        is_update = True
        if source_types:
            source_types = list(set(source_types.split(',')))
        for item in source_types:
            if int(item) == 1:
                act_prize_total = ActPrizeModel(context=self.context).get_total("act_id=%s and goods_id=%s", params=[act_id, goods_id])
                if act_prize_total > 0 :
                    is_update = False
            elif int(item) == 2:
                price_gear_total = PriceGearModel(context=self.context).get_total("act_id=%s and goods_id=%s", params=[act_id, goods_id])
                if price_gear_total > 0 :
                    is_update = False
        if is_update == True:
            launch_goods_model.update_table("is_launch=0,is_sync=0,launch_date=%s", "act_id=%s and goods_id=%s", params=[SevenHelper.get_now_datetime(), act_id, goods_id])
        return invoke_result_data

    def init_launch_goods(self, app_id, act_id, source_types, online_url):
        """
        :description: 初始化活动投放,用于创建活动时调用
        :param app_id:应用标识
        :param act_id:活动标识
        :param source_types：商品来源（1活动奖品商品2价格档位商品） 多个逗号,分隔
        :param online_url:投放地址
        :return 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        act_base_model = ActBaseModel(context=self.context)
        act_info_dict = act_base_model.get_act_info_dict(act_id)
        if not act_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "活动不存在"
            return invoke_result_data
        goods_id_list = []
        if source_types:
            source_types = list(set(source_types.split(',')))
        for item in source_types:
            if int(item) == 1:
                prize_goods_id_list = ActPrizeModel(context=self.context).get_dict_list("act_id=%s and goods_id!='' and is_del=0", field="goods_id", params=[act_id])
                if len(prize_goods_id_list) > 0:
                    goods_id_list += [str(goods_id["goods_id"]) for goods_id in prize_goods_id_list]
            elif int(item) == 2:
                gear_goods_id_list = PriceGearModel(context=self.context).get_dict_list("act_id=%s and goods_id!='' and is_del=0", field="goods_id", params=[act_id])
                if len(gear_goods_id_list) > 0:
                    goods_id_list += [str(goods_id["goods_id"]) for goods_id in gear_goods_id_list]
        goods_id_list = list(set(goods_id_list))
        if len(goods_id_list) == 0:
            result_data = {"url": online_url, "act_name": act_info_dict['act_name'], "goods_list": []}
            invoke_result_data.data = result_data
            return invoke_result_data

        launch_goods_model = LaunchGoodsModel(context=self.context)
        goods_exist_list = launch_goods_model.get_dict_list("act_id<>%s and " + SevenHelper.get_condition_by_str_list("goods_id",goods_id_list), field="goods_id", params=act_id)
        goods_id_exist_list = [str(i["goods_id"]) for i in goods_exist_list]
        goods_list = []
        now_datetime = SevenHelper.get_now_datetime()
        for goods_id in goods_id_list:
            launch_goods = LaunchGoods()
            launch_goods.app_id = app_id
            launch_goods.act_id = act_id
            launch_goods.goods_id = goods_id
            if goods_id in goods_id_exist_list:
                launch_goods.is_launch = 0
                launch_goods.is_sync = 0
            else:
                launch_goods.is_launch = 1
                launch_goods.is_sync = 1

            launch_goods.create_date = now_datetime
            launch_goods.launch_date = now_datetime
            launch_goods.sync_date = now_datetime
            goods_list.append(launch_goods)

        launch_goods_model.add_list(goods_list)
        result_data = {"url": online_url, "act_name": act_info_dict['act_name'], "goods_list": goods_id_list}
        invoke_result_data.data = result_data
        return invoke_result_data

    def async_launch_goods(self, app_id, act_id, online_url, access_token, app_key, app_secret, is_log=False):
        """
        :description: 同步投放商品（小程序投放-商品绑定/解绑）
        :param app_id：应用标识
        :param act_id：活动标识
        :param online_url:投放地址
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log：是否记录返回信息
        :return 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        act_base_model = ActBaseModel(context=self.context)
        act_info_dict = act_base_model.get_act_info_dict(act_id)
        if not act_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "活动不存在"
            return invoke_result_data
        top_base_model = TopBaseModel(context=self.context)
        launch_goods_model = LaunchGoodsModel(context=self.context)
        launch_goods_list = launch_goods_model.get_list("app_id=%s and act_id=%s and is_sync=0 and is_launch=1", params=[app_id,act_id])
        no_launch_goods_list = launch_goods_model.get_list("app_id=%s and act_id=%s and is_sync=0 and is_launch=0", params=[app_id,act_id])
        # 同步不投放的商品
        if len(no_launch_goods_list) > 0:

            no_launch_goods_id_list = [str(no_launch_goods.goods_id) for no_launch_goods in no_launch_goods_list]
            no_launch_goods_id_list = list(set(no_launch_goods_id_list))
            no_launch_goods_ids = ",".join(no_launch_goods_id_list)

            update_no_launch_goods_list = []
            # 淘宝top接口
            invoke_result_data = top_base_model.miniapp_distribution_items_bind(no_launch_goods_ids, online_url, 'false',access_token,app_key, app_secret, is_log)
            if invoke_result_data.success == False:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "活动不存在"
                return invoke_result_data
            resp = invoke_result_data.data
            if "error_message" in resp.keys():
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = resp["error_message"]
                return invoke_result_data
            async_result = resp["miniapp_distribution_items_bind_response"]["model_list"]["distribution_order_bind_target_entity_open_result_dto"][0]["bind_result_list"]["distribution_order_bind_base_dto"]
            for async_result_info in async_result:
                no_launch_goods = [no_launch_goods for no_launch_goods in no_launch_goods_list if str(no_launch_goods.goods_id) == async_result_info["target_entity_id"]]
                if len(no_launch_goods) > 0:
                    if async_result_info["success"] == True:
                        no_launch_goods[0].is_sync = 1
                        no_launch_goods[0].sync_date = SevenHelper.get_now_datetime()
                    else:
                        no_launch_goods[0].error_message = async_result_info["fail_msg"]
                    update_no_launch_goods_list.append(no_launch_goods[0])

            launch_goods_model.update_list(update_no_launch_goods_list)

        # 同步投放的商品
        if len(launch_goods_list) > 0:
            launch_goods_id_list = [str(launch_goods.goods_id) for launch_goods in launch_goods_list]
            launch_goods_id_list = list(set(launch_goods_id_list))
            launch_goods_ids = ",".join(launch_goods_id_list)

            update_launch_goods_list = []
            # 淘宝top接口
            invoke_result_data = top_base_model.miniapp_distribution_items_bind(launch_goods_ids, online_url, 'true',access_token,app_key, app_secret, is_log)
            if invoke_result_data.success == False:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "活动不存在"
                return invoke_result_data
            resp = invoke_result_data.data
            if "error_message" in resp.keys():
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = resp["error_message"]
                return invoke_result_data
            async_result = resp["miniapp_distribution_items_bind_response"]["model_list"]["distribution_order_bind_target_entity_open_result_dto"][0]["bind_result_list"]["distribution_order_bind_base_dto"]
            for async_result_info in async_result:
                launch_goods = [launch_goods for launch_goods in launch_goods_list if str(launch_goods.goods_id) == async_result_info["target_entity_id"]]
                if len(launch_goods) > 0:
                    if async_result_info["success"] == True:
                        launch_goods[0].is_sync = 1
                        launch_goods[0].sync_date = SevenHelper.get_now_datetime()
                    else:
                        launch_goods[0].is_launch = 0
                        launch_goods[0].is_sync = 1
                        launch_goods[0].error_message = async_result_info["fail_msg"]
                    update_launch_goods_list.append(launch_goods[0])

            launch_goods_model.update_list(update_launch_goods_list)

        return invoke_result_data

    def get_launch_goods_list(self, app_id, act_id, page_size, page_index, access_token, app_key, app_secret):
        """
        :description: 获取投放商品列表
        :param app_id:应用标识
        :param act_id:活动标识
        :param page_size:条数
        :param page_index:页数
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :return 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        act_base_model = ActBaseModel(context=self.context)
        act_info_dict = act_base_model.get_act_info_dict(act_id)
        if not act_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "活动不存在"
            return invoke_result_data
        launch_goods_model = LaunchGoodsModel(context=self.context)
        launch_goods_list, total = launch_goods_model.get_dict_page_list("*", page_index, page_size, "app_id=%s and act_id=%s", "", "id desc", params=[app_id,act_id])

        top_base_model = TopBaseModel(context=self.context)
        #获取商品信息
        goods_list = []
        if len(launch_goods_list) > 0:
            goods_ids = ",".join([str(launch_goods["goods_id"]) for launch_goods in launch_goods_list])

            invoke_result_data = top_base_model.get_goods_list_by_goodsids(goods_ids, access_token,app_key,app_secret)
            if invoke_result_data.success == False:
                return invoke_result_data
            resq = invoke_result_data.data
            if "items_seller_list_get_response" in resq.keys():
                if "item" in resq["items_seller_list_get_response"]["items"].keys():
                    goods_list = resq["items_seller_list_get_response"]["items"]["item"]
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code = resq["error_code"]
                invoke_result_data.error_message = resq["error_message"]
                return invoke_result_data
        if len(goods_list)>0:
            launch_goods_list = SevenHelper.merge_dict_list(launch_goods_list, "goods_id", goods_list, "num_iid", "pic_url,title")
        page_info = PageInfo(page_index, page_size, total, launch_goods_list)
        invoke_result_data.data = {"is_launch": act_info_dict['is_launch'], "page_info": page_info.__dict__}
        return invoke_result_data