# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-09 09:24:43
@LastEditTime: 2022-01-24 19:01:28
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.user_base_model import UserBaseModel
from seven_cloudapp_frame.models.frame_base_model import FrameBaseModel
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.price_base_model import *
from seven_cloudapp_frame.models.asset_base_model import *
from seven_cloudapp_frame.models.db_models.act.act_module_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_order_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_order_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_pay_order_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *


class OrderBaseModel(FrameBaseModel):
    """
    :description: 订单和中奖记录相关业务模型
    """
    def __init__(self, context=None,logging_error=None, logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info
        super(OrderBaseModel,self).__init__(context)

    def _delete_prize_order_dependency_key(self, act_id, user_id):
        """
        :description: 删除订单依赖建
        :param act_id: 活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            dependency_key = f"prize_order_list:actid_{act_id}"
            if user_id:
                dependency_key += f"_userid_{user_id}"
            redis_init = SevenHelper.redis_init()
            redis_init.delete(dependency_key)
        except Exception as ex:
            pass

    def _delete_prize_roster_dependency_key(self, act_id, user_id):
        """
        :description: 删除中奖记录依赖建
        :param act_id: 活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            dependency_key = f"prize_roster_list:actid_{act_id}"
            if user_id:
                dependency_key += f"_userid_{user_id}"
            redis_init = SevenHelper.redis_init()
            redis_init.delete(dependency_key)
        except Exception as ex:
            pass

    def get_prize_order_list(self, app_id, act_id, user_id, open_id, nick_name, order_no, real_name, telephone, address, order_status, create_date_start, create_date_end, page_size=20, page_index=0, order_by="create_date desc", field="*", is_search_roster=False, is_cache=True, condition="", params=[], prize_roster_sub_table=None):
        """
        :description: 用户奖品订单列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param open_id：open_id
        :param order_no：订单号
        :param nick_name：用户昵称
        :param real_name：用户名字
        :param telephone：联系电话
        :param address：收货地址
        :param order_status：订单状态（-1未付款-2付款中0未发货1已发货2不予发货3已退款4交易成功）
        :param create_date_start：订单创建时间开始
        :param create_date_end：订单创建时间结束
        :param page_size：页大小
        :param page_index：页索引
        :param order_by：排序
        :param field：查询字段
        :param is_search_roster：是否查询订单关联中奖记录
        :param is_cache：是否缓存
        :param condition：条件
        :param params：参数化数组
        :param prize_roster_sub_table：奖品记录分表名称       
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        where = "app_id=%s and act_id=%s"
        params_list = [app_id,act_id]
        if condition:
            where += " AND " + condition
            params_list.extend(params)
        page_info = PageInfo(page_index, page_size, 0, [])

        if not app_id or not act_id:
            return page_info
        if user_id:
            where += " AND user_id=%s"
            params_list.append(user_id)
        if open_id:
            where += " AND open_id=%s"
            params_list.append(open_id)
        if order_no:
            where += " AND order_no=%s"
            params_list.append(order_no)
        if nick_name:
            where += " AND user_nick=%s"
            params_list.append(nick_name)
        if real_name:
            where += " AND real_name=%s"
            params_list.append(real_name)
        if telephone:
            where += " AND telephone=%s"
            params_list.append(telephone)
        if address:
            address = f"{address}%"
            where += " AND address like %s"
            params_list.append(address)
        if order_status >=-2:
            where += " AND order_status=%s"
            params_list.append(order_status)
        if create_date_start:
            where += " AND create_date>=%s"
            params_list.append(create_date_start)
        if create_date_end:
            where += " AND create_date<=%s"
            params_list.append(create_date_end)
        prize_order_model = PrizeOrderModel(context=self.context)
        if is_cache:
            dependency_key=f"prize_order_list:actid_{act_id}"
            if user_id:
                dependency_key += f"_userid_{user_id}"
            page_list, total = prize_order_model.get_cache_dict_page_list(field, page_index, page_size, where, "", order_by, params_list, dependency_key)
        else:
            page_list, total = prize_order_model.get_dict_page_list(field, page_index, page_size, where, "", order_by, params_list)
        if is_search_roster == True:
            prize_roster_model = PrizeRosterModel(context=self.context, sub_table=prize_roster_sub_table)
            if page_list and len(page_list)>0:
                order_no_list = [str(i['order_no']) for i in page_list]
                prize_roster_list_dict = prize_roster_model.get_dict_list(SevenHelper.get_condition_by_str_list("order_no",order_no_list))
                for i in range(len(page_list)):
                    roster_list = [prize_roster for prize_roster in prize_roster_list_dict if page_list[i]["order_no"] == prize_roster["order_no"]]
                    page_list[i]["roster_list"] = roster_list
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info

    def update_prize_order_status(self,app_id,prize_order_id,order_status,express_company="",express_no="",prize_roster_sub_table=None):
        """
        :description: 更新用户奖品订单状态
        :param app_id：应用标识
        :param prize_order_id：奖品订单标识
        :param order_status：订单状态
        :param express_company：快递公司
        :param express_no：快递单号
        :param prize_roster_sub_table：奖品记录分表名称
        :return: 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        now_datetime = SevenHelper.get_now_datetime()
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        prize_order_model = PrizeOrderModel(context=self.context, db_transaction=db_transaction)
        prize_roster_model = PrizeRosterModel(context=self.context, sub_table=prize_roster_sub_table, db_transaction=db_transaction)
        invoke_result_data = InvokeResultData()

        prize_order = prize_order_model.get_entity_by_id(prize_order_id)
        if not prize_order:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="奖品订单信息不存在-1"
            return invoke_result_data
        if prize_order.app_id != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="奖品订单信息不存在-2"
            return invoke_result_data
        try:
            db_transaction.begin_transaction()
            if order_status == 1:
                if not express_company and not express_no:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message ="快递公司或快递单号不能为空"
                    return invoke_result_data
                update_sql = "order_status=1,express_company=%s,express_no=%s,deliver_date=%s,modify_date=%s"
                params = [express_company, express_no, now_datetime, now_datetime, prize_order_id]
                prize_order_model.update_table(update_sql, "id=%s", params)
                prize_roster_model.update_table("logistics_status=1", "act_id=%s and order_no=%s", [prize_order.act_id,prize_order.order_no])
            elif order_status == 2:
                update_sql = "order_status=2,modify_date=%s"
                params = [now_datetime, prize_order_id]
                prize_order_model.update_table(update_sql, "id=%s", params)
                prize_roster_model.update_table("logistics_status=2", "act_id=%s and order_no=%s", [prize_order.act_id,prize_order.order_no])
            else:
                prize_order_model.update_table("order_status=%s,modify_date=%s", "id=%s", [order_status, now_datetime, prize_order_id])
            result = db_transaction.commit_transaction()
            if result == False:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message ="操作失败"
                return invoke_result_data

        except Exception as ex:
            if self.context:
                self.context.logging_link_error(traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error(traceback.format_exc())
            if db_transaction.is_transaction == True:
                db_transaction.rollback_transaction()
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="操作失败"
            return invoke_result_data

        return invoke_result_data

    def update_prize_order_seller_remark(self,app_id,prize_order_id,seller_remark):
        """
        :description: 更新用户奖品订单卖家备注
        :param app_id：应用标识
        :param prize_order_id：奖品订单标识
        :param seller_remark：卖家备注
        :return: 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        now_datetime = SevenHelper.get_now_datetime()
        prize_order_model = PrizeOrderModel(context=self.context)
        invoke_result_data = InvokeResultData()

        prize_order = prize_order_model.get_entity_by_id(prize_order_id)
        if not prize_order:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="奖品订单信息不存在-1"
            return invoke_result_data
        if prize_order.app_id!=app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="奖品订单信息不存在-2"
            return invoke_result_data
        prize_order_model.update_table("seller_remark=%s,modify_date=%s", "id=%s", [seller_remark, now_datetime, prize_order_id])
        return invoke_result_data

    def import_prize_order(self, app_id, act_id, content_type, content, ref_head_name='小程序订单号', prize_roster_sub_table=None):
        """
        :description: 
        :param app_id：应用标识
        :param act_id：活动标识
        :param content_type：内容类型 1-base64字符串内容 2-json字符串内容
        :param content：字符串内容
        :param ref_head_name：关联表头名称
        :param prize_roster_sub_table：奖品记录分表名称
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not act_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="无效活动,无法导入订单"
            return invoke_result_data
        prize_order_model = PrizeOrderModel(context=self.context)
        prize_roster_model = PrizeRosterModel(context=self.context, sub_table=prize_roster_sub_table)
        data = []
        total_num = 0
        if content_type == 1:
            data = base64.decodebytes(str(content).encode())
            if not os.path.exists("temp"):
                os.makedirs("temp")
            path = "temp/" + UUIDHelper.get_uuid() + ".xlsx"
            with open(path, 'ba') as f:
                buf = bytearray(data)
                f.write(buf)
            f.close()
            order_no_index = -1
            express_no_index = -1
            express_company_index = -1

            data = ExcelHelper.input(path)
            data_total = len(data)
            # 表格头部
            if data_total > 0:
                title_list = data[0]
                if ref_head_name in title_list:
                    order_no_index = title_list.index(ref_head_name)
                if "物流单号" in title_list:
                    express_no_index = title_list.index("物流单号")
                if "物流公司" in title_list:
                    express_company_index = title_list.index("物流公司")

            if order_no_index == -1 or express_no_index == -1 or express_company_index == -1:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message ="缺少必要字段，无法导入订单"
                return invoke_result_data
            # 数据导入
            for i in range(1, data_total):
                row = data[i]
                order_no = str(row[order_no_index]).strip()
                express_no = str(row[express_no_index]).strip()
                express_company = str(row[express_company_index]).strip()
                if order_no and express_no and express_company:
                    now_datetime = SevenHelper.get_now_datetime()
                    update_sql = "order_status=1,express_company=%s,express_no=%s,deliver_date=%s"
                    params = [express_company, express_no, now_datetime, app_id,act_id,order_no]
                    result = prize_order_model.update_table(update_sql, "app_id=%s and act_id=%s and order_no=%s", params)
                    if result == True:
                        prize_roster_model.update_table("logistics_status=1", "app_id=%s and act_id=%s and order_no=%s", [app_id,act_id,order_no])
                        total_num += 1
            os.remove(path)
        else:
            data = SevenHelper.json_loads(content)
            for row in data:
                order_no = str(row[ref_head_name]).strip()
                express_no = str(row['物流单号']).strip()
                express_company = str(row['物流公司']).strip()
                if order_no and express_no and express_company:
                    now_datetime = SevenHelper.get_now_datetime()
                    update_sql = "order_status=1,express_company=%s,express_no=%s,deliver_date=%s"
                    params = [express_company, express_no, now_datetime, app_id,act_id,order_no]
                    result = prize_order_model.update_table(update_sql, "app_id=%s and act_id=%s and order_no=%s", params)
                    if result == True:
                        prize_roster_model.update_table("logistics_status=1", "app_id=%s and act_id=%s and order_no=%s", [app_id,act_id,order_no])
                        total_num += 1
                else:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "缺少必要字段，无法导入订单"
                    return invoke_result_data
        invoke_result_data.data = {"total_num": total_num}
        return invoke_result_data

    def get_tao_pay_order_list(self,app_id,act_id,user_id,open_id,nick_name,pay_date_start,pay_date_end,page_size=20,page_index=0,field="*",order_by="pay_date desc",condition="",params=[]):
        """
        :description: 淘宝用户购买订单列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户唯一标识
        :param open_id：open_id
        :param nick_name：用户昵称
        :param pay_date_start：订单支付时间开始
        :param pay_date_end：订单支付时间结束
        :param page_size：页大小
        :param page_index：页索引
        :param field：查询字段
        :param order_by：排序
        :param condition：条件
        :param params：参数化数组
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        where = "app_id=%s and act_id=%s"
        params_list = [app_id,act_id]
        if condition:
            where += " AND " + condition
            params_list.extend(params)
        page_info = PageInfo(page_index, page_size, 0, [])

        if not act_id:
            return page_info
        if user_id:
            where += " AND user_id=%s"
            params_list.append(user_id)
        if open_id:
            where += " AND open_id=%s"
            params_list.append(open_id)
        if nick_name:
            where += " AND user_nick=%s"
            params_list.append(nick_name)
        if pay_date_start:
            where += " AND pay_date>=%s"
            params_list.append(pay_date_start)
        if pay_date_end:
            where += " AND pay_date<=%s"
            params_list.append(pay_date_end)
        page_list, total = TaoPayOrderModel(context=self.context).get_dict_page_list(field, page_index, page_size, where, "", order_by, params_list)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info

    def select_prize_order(self,app_id,act_id,user_id,login_token,prize_ids,real_name,telephone,province,city,county,street,address):
        """
        :description: 选择奖品进行下单
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param login_token:用户访问令牌
        :param prize_ids:用户奖品id串，逗号分隔（为空则将所有未下单的奖品进行下单）
        :param real_name:用户名
        :param telephone:电话
        :param province:省
        :param city:市
        :param county:区县
        :param street:街道
        :param address:地址
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not act_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="无效活动,无法创建订单"
            return invoke_result_data
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        prize_roster_model = PrizeRosterModel(db_transaction=db_transaction, context=self)
        prize_order_model = PrizeOrderModel(db_transaction=db_transaction, context=self)
        prize_ids_list = []
        if prize_ids:
            prize_ids_list = prize_ids.split(',')
            for prize_id in prize_ids_list:
                try:
                    prize_id = int(prize_id)
                except Exception as ex:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message ="存在无法识别的奖品标识"
                    return invoke_result_data

        #获取用户信息
        user_info_dict = user_info_model.get_dict("act_id=%s and user_id=%s", limit="1", params=[act_id, user_id])
        if not user_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "用户不存在"
            return invoke_result_data
        if user_info_dict["login_token"] != login_token:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "已在另一台设备登录,无法操作"
            return invoke_result_data
        if int(user_info_dict["user_state"]) == 1:
            invoke_result_data.success = False
            invoke_result_data.error_code = "user_exception"
            invoke_result_data.error_message = "账号异常,请联系客服处理"
            return invoke_result_data

        acquire_lock_name = f"create_prize_order_queue_{act_id}_{user_id}"
        acquire_lock_status, identifier = SevenHelper.redis_acquire_lock(acquire_lock_name)
        if acquire_lock_status == False:
            invoke_result_data.success = False
            invoke_result_data.error_code = "acquire_lock"
            invoke_result_data.error_message = "请求超时,请稍后再试"
            SevenHelper.redis_release_lock(acquire_lock_name, identifier)
            return invoke_result_data
        #用户奖品列表
        if len(prize_ids_list)>0:
            prize_roster_list = prize_roster_model.get_list("act_id=%s and id in (" + prize_ids + ") and prize_status=0",params=[act_id])
            if len(prize_roster_list) == 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "对不起,所选下单奖品不存在"
                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                return invoke_result_data
        else:
            prize_roster_list = prize_roster_model.get_list("act_id=%s and prize_status=0")

        prize_order_model = PrizeOrderModel(context=self.context)
        now_date = SevenHelper.get_now_datetime()
        prize_order = PrizeOrder()
        prize_order.app_id = app_id
        prize_order.user_id = user_id
        prize_order.user_nick = user_info_dict["user_nick"]
        prize_order.open_id = user_info_dict["open_id"]
        prize_order.act_id = act_id
        prize_order.real_name = real_name
        prize_order.telephone = telephone
        prize_order.province = province
        prize_order.city = city
        prize_order.county = county
        prize_order.street = street
        prize_order.address = address
        prize_order.order_status = 0
        prize_order.create_date = now_date
        prize_order.modify_date = now_date
        prize_order.order_no = SevenHelper.create_order_id()

        for prize_roster in prize_roster_list:
            prize_roster.order_no = prize_order.order_no
            prize_roster.prize_status = 1
        try:
            db_transaction.begin_transaction()
            prize_order_model.add_entity(prize_order)
            prize_roster_model.update_list(prize_roster_list, "order_no,prize_status")
            result = db_transaction.commit_transaction()
            if result == False:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "对不起,下单失败"
                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                return invoke_result_data
        except Exception as ex:
            if db_transaction.is_transaction == True:
                db_transaction.rollback_transaction()
            if self.context:
                self.context.logging_link_error("create_prize_order:" + traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error("create_prize_order:" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起,下单失败"
            SevenHelper.redis_release_lock(acquire_lock_name, identifier)
            return invoke_result_data

        SevenHelper.redis_release_lock(acquire_lock_name, identifier)
        self._delete_prize_order_dependency_key(act_id,user_id)
        self._delete_prize_roster_dependency_key(act_id, user_id)
        invoke_result_data.data = prize_order.__dict__
        return invoke_result_data

    def _get_pay_order_no_list(self,app_id,user_id):
        """
        :description: 获取已获取奖励的订单子编号列表
        :param app_id:应用标识
        :param user_id:用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        redis_init = SevenHelper.redis_init()
        pay_order_cache_key = f"sub_pay_order_no_list:appid_{app_id}_userid_{user_id}"
        pay_order_no_list = redis_init.lrange(pay_order_cache_key,0,-1)
        pay_order_list = []
        is_add = False
        if not pay_order_no_list or len(pay_order_no_list)<=0:
            tao_pay_order_model = TaoPayOrderModel(context=self.context)
            pay_order_list = tao_pay_order_model.get_dict_list("app_id=%s and user_id=%s",field="sub_pay_order_no", params=[app_id,user_id])
            is_add = True

        if len(pay_order_list) >0:
            for item in pay_order_list:
                pay_order_no_list.append(item["sub_pay_order_no"])
                if is_add == True:
                    redis_init.lpush(pay_order_cache_key,item["sub_pay_order_no"])
                    redis_init.expire(pay_order_cache_key, 30 * 24 * 3600)
        return pay_order_no_list,redis_init,pay_order_cache_key

    def sync_tao_pay_order(self,app_id,act_id,module_id,user_id,login_token,handler_name,request_code,asset_type=3,goods_id="",sku_id="",ascription_type=1,app_key="",app_secret="",is_log=False,check_user_nick=True,continue_request_expire=5):
        """
        :description: 同步淘宝支付订单给用户加资产
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param handler_name:接口名称
        :param request_code:请求代码
        :param asset_type:资产类型(1-次数2-积分3-价格档位)
        :param goods_id:商品ID（资产类型为3-价格档位 无需填写）
        :param sku_id:sku_id (资产类型为3-价格档位 无需填写)
        :param ascription_type:归属类型（0-抽奖次数订单1-邮费次数订单2-任务订单）
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log:是否记录top请求日志
        :param check_user_nick:是否校验昵称为空
        :param continue_request_expire:连续请求过期时间，为0不进行校验，单位秒
        :return 
        :last_editors: HuangJianYi
        """
        acquire_lock_name = f"sync_tao_pay_order:{act_id}_{module_id}_{user_id}"
        identifier = ""
        try:
            invoke_result_data = self.business_process_executing(app_id,act_id,module_id,user_id,login_token,handler_name,False,check_user_nick,continue_request_expire,acquire_lock_name)
            if invoke_result_data.success == True:
                act_info_dict = invoke_result_data.data["act_info_dict"]
                act_module_dict = invoke_result_data.data["act_module_dict"]
                user_info_dict = invoke_result_data.data["user_info_dict"]
                identifier = invoke_result_data.data["identifier"]

                # 获取订单
                app_info_dict = AppBaseModel(context=self.context).get_app_info_dict(app_id)
                access_token = app_info_dict["access_token"] if app_info_dict else ""
                top_base_model = TopBaseModel(context=self.context)
                order_data = []
                if act_info_dict['start_date'] != "":
                    invoke_result_data = top_base_model.get_buy_order_list(user_info_dict["open_id"], access_token,app_key,app_secret, act_info_dict['start_date'],is_log=is_log)
                    if invoke_result_data.success == True:
                        order_data = invoke_result_data.data
                else:
                    invoke_result_data = top_base_model.get_buy_order_list(user_info_dict["open_id"], access_token,app_key,app_secret,is_log=is_log)
                    if invoke_result_data.success == True:
                        order_data = invoke_result_data.data
                if len(order_data)>0:
                    pay_order_no_list,redis_init,pay_order_cache_key = self._get_pay_order_no_list(app_id,user_id)

                    goods_ids_list = []
                    #满足奖励条件的订单
                    reward_order_list = []
                    #所有相关商品订单
                    all_order_list = []
                    if asset_type == 3:
                        price_base_model = PriceBaseModel(context=self.context)
                        price_gear_dict_list = price_base_model.get_price_gear_list(app_id,act_id,100,0).data
                        for price_gear_dict in price_gear_dict_list:
                            goods_ids_list.append(price_gear_dict["goods_id"])
                    else:
                        goods_ids_list.append(str(goods_id))

                    for item in order_data:
                        for order in item["orders"]["order"]:
                            if str(order["num_iid"]) in goods_ids_list:
                                if order["status"] in self.rewards_status():
                                    order["pay_time"] = item["pay_time"]
                                    order["tid"] = item["tid"]
                                    reward_order_list.append(order)
                                if "pay_time" in item:
                                    order["tid"] = item["tid"]
                                    order["pay_time"] = item["pay_time"]
                                    all_order_list.append(order)

                    pay_price = 0
                    pay_num = 0
                    buy_num = 0
                    tao_pay_order_list = []
                    for order in reward_order_list:
                        try:
                            #判断是否已经加过奖励
                            if order["oid"] not in pay_order_no_list:
                                asset_object_name = ""
                                asset_object_id = ""
                                payment = round(decimal.Decimal(order["payment"] if order["payment"] else decimal.Decimal(order["price"]) * int(order["num"])), 2)
                                if asset_type == 3:
                                    now_price_gear_dict = None
                                    for price_gear_dict in price_gear_dict_list:
                                        if (price_gear_dict["effective_date"] == '1900-01-01 00:00:00' or TimeHelper.format_time_to_datetime(price_gear_dict["effective_date"]) < TimeHelper.format_time_to_datetime(order["pay_time"])) and price_gear_dict["goods_id"] == str(order["num_iid"]):
                                            #关联类型：1商品skuid关联2商品id关联
                                            if price_gear_dict["relation_type"] == 1 and price_gear_dict["sku_id"] != str(order["sku_id"]):
                                                continue
                                            now_price_gear_dict = price_gear_dict
                                    if not now_price_gear_dict:
                                        continue
                                    asset_object_id = now_price_gear_dict["id"]
                                    asset_object_name = now_price_gear_dict["price_gear_name"]
                                else:
                                    if str(goods_id) != str(order["num_iid"]):
                                        continue
                                    if sku_id and str(sku_id) != str(order["sku_id"]):
                                        continue

                                tao_pay_order = TaoPayOrder()
                                tao_pay_order.app_id = app_id
                                tao_pay_order.act_id = act_id
                                tao_pay_order.ascription_type = ascription_type
                                tao_pay_order.user_id = user_id
                                tao_pay_order.open_id = user_info_dict["open_id"]
                                tao_pay_order.user_nick = user_info_dict["user_nick"]
                                tao_pay_order.main_pay_order_no = order['tid']
                                tao_pay_order.sub_pay_order_no = order['oid']
                                tao_pay_order.goods_code = order['num_iid']
                                tao_pay_order.goods_name = order['title']
                                if "sku_id" in order.keys():
                                    tao_pay_order.sku_id = order['sku_id']
                                    sku_invoke_result_data = top_base_model.get_sku_name(int(order['num_iid']), int(order['sku_id']), access_token,app_key, app_secret,is_log)
                                    tao_pay_order.sku_name = sku_invoke_result_data.data if sku_invoke_result_data.success == True else ""
                                tao_pay_order.buy_num = order['num']
                                tao_pay_order.pay_price = order['payment']
                                tao_pay_order.order_status = order['status']
                                tao_pay_order.create_date = SevenHelper.get_now_datetime()
                                tao_pay_order.asset_type = asset_type
                                tao_pay_order.asset_object_id = asset_object_id
                                tao_pay_order.asset_object_name = asset_object_name
                                tao_pay_order.surplus_count = order['num']
                                tao_pay_order.pay_date = order['pay_time']
                                tao_pay_order_list.append(tao_pay_order)

                                pay_price = decimal.Decimal(pay_price) + payment
                                pay_num = pay_num + 1
                                buy_num = buy_num + order['num']
                        except Exception as ex:
                            if self.context:
                                self.context.logging_link_info(str(order) + "【同步淘宝支付订单】" + traceback.format_exc())
                            elif self.logging_link_info:
                                self.logging_link_info(str(order) + "【同步淘宝支付订单】" + traceback.format_exc())
                            continue
                    if len(tao_pay_order_list) > 0:
                        result = TaoPayOrderModel(context=self.context).add_list(tao_pay_order_list)
                        if result == True and buy_num > 0:
                            asset_base_model = AssetBaseModel(context=self.context)
                            invoke_result_data.data = {}
                            invoke_result_data.data["asset_list"] = []
                            for item in tao_pay_order_list:
                                only_id = str(item.sub_pay_order_no)
                                asset_invoke_result_data = asset_base_model.update_user_asset(app_id,act_id,module_id,user_id,user_info_dict["open_id"],user_info_dict["user_nick"],asset_type,item.buy_num,item.asset_object_id,1,"","","购买",only_id,handler_name,request_code,info_json={})
                                if asset_invoke_result_data.success == False:
                                    invoke_result_data.success = False
                                    invoke_result_data.error_code = "error"
                                    invoke_result_data.error_message = "变更资产失败"
                                else:
                                    redis_init.lpush(pay_order_cache_key,item.sub_pay_order_no)
                                    redis_init.expire(pay_order_cache_key, 30 * 24 * 3600)
                                    data = {}
                                    data["asset_type"] = asset_type
                                    data["asset_object_id"] = item.asset_object_id
                                    data["buy_num"] = item.buy_num
                                    invoke_result_data.data["asset_list"].append(data)
                            invoke_result_data.data["buy_num"] = buy_num
                            invoke_result_data.data["pay_price"] = pay_price
                            invoke_result_data.data["pay_num"] = pay_num
                        else:
                            invoke_result_data.success = False
                            invoke_result_data.error_code = "error"
                            invoke_result_data.error_message = "没有匹配订单"
                    else:
                        invoke_result_data.success = False
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = "没有匹配订单"
                    if len(all_order_list) >0:
                        user_base_model = UserBaseModel(context=self.context)
                        black_status = user_base_model.check_pull_black(user_info_dict,act_info_dict["is_black"],act_info_dict["refund_count"],all_order_list)
                        if black_status == True:
                            invoke_result_data.data = {} if not invoke_result_data.data else invoke_result_data.data
                            invoke_result_data.data["user_state"] = 1
                else:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "没有订单"
        except Exception as ex:
            if self.context:
                self.context.logging_link_error("【同步淘宝支付订单】" + traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error("【同步淘宝支付订单】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = "系统繁忙,请稍后再试"
        finally:
            self.business_process_executed(act_id,module_id,user_id,handler_name,acquire_lock_name,identifier)

        return invoke_result_data

    def get_prize_roster_list(self,app_id,act_id,module_id,user_id,open_id="",user_nick="",order_no="",goods_type=-1,prize_type=-1,logistics_status=-1,prize_status=-1,pay_status=-1,page_size=20,page_index=0,create_date_start="",create_date_end="",order_by="create_date desc",field="*",condition="",params=[],is_cache=True):
        """
        :description: 用户中奖记录列表
        :description: 如果有进行数据缓存，创建中奖记录时需清掉依赖建
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param user_id：用户标识
        :param open_id：open_id
        :param user_nick：用户昵称
        :param order_no：订单号
        :param goods_type：物品类型（1虚拟2实物）
        :param prize_type：奖品类型(1现货2优惠券3红包4参与奖5预售)
        :param logistics_status：物流状态（0未发货1已发货2不予发货）
        :param prize_status：奖品状态（0未下单（未领取）1已下单（已领取）2已回购10已隐藏（删除）11无需发货）
        :param pay_status：支付状态(0未支付1已支付2已退款3处理中)
        :param page_size：页大小
        :param page_index：页索引
        :param create_date_start：开始时间
        :param create_date_end：结束时间
        :param order_by：排序
        :param field：查询字段
        :param condition：条件
        :param params：参数化数组
        :param is_cache：是否缓存
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        where = "app_id=%s AND act_id=%s"
        params_list = [app_id,act_id]
        if condition:
            where += " AND " + condition
            params_list.extend(params)
        page_info = PageInfo(page_index, page_size, 0, [])

        if not app_id or not act_id:
            return page_info
        if module_id:
            where += " AND module_id=%s"
            params_list.append(module_id)
        if user_id:
            where += " AND user_id=%s"
            params_list.append(user_id)
        if open_id:
            where += " AND open_id=%s"
            params_list.append(open_id)
        if user_nick:
            where += " AND user_nick=%s"
            params_list.append(user_nick)
        if order_no:
            where += " AND order_no=%s"
            params_list.append(order_no)
        if goods_type !=-1:
            where += " AND goods_type=%s"
            params_list.append(goods_type)
        if prize_type !=-1:
            where += " AND prize_type=%s"
            params_list.append(prize_type)
        if logistics_status !=-1:
            where += " AND logistics_status=%s"
            params_list.append(logistics_status)
        if prize_status !=-1:
            where += " AND prize_status=%s"
            params_list.append(prize_status)
        if pay_status !=-1:
            where += " AND pay_status=%s"
            params_list.append(pay_status)
        if create_date_start:
            where += " AND create_date>=%s"
            params_list.append(create_date_start)
        if create_date_end:
            where += " AND create_date<=%s"
            params_list.append(create_date_end)

        prize_roster_model = PrizeRosterModel(context=self.context)
        if is_cache:
            dependency_key = f"prize_roster_list:actid_{act_id}"
            if user_id:
                dependency_key += f"_userid_{user_id}"
            page_list, total = prize_roster_model.get_cache_dict_page_list(field, page_index, page_size, where, "", order_by, params_list,dependency_key)
        else:
            page_list, total = prize_roster_model.get_dict_page_list(field, page_index, page_size, where, "", order_by, params_list)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info

    def get_horseracelamp_list(self, act_id, module_id, is_search_module=False, condition="", params=[], page_size=30):
        """
        :description: 获取跑马灯奖品列表
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param is_search_module:是否查询活动模块
        :param condition：条件
        :param params：参数数组
        :param page_size：页大小
        :return list
        :last_editors: HuangJianYi
        """
        condition_where = ConditionWhere()
        condition_where.add_condition("act_id=%s")
        params_list = [act_id]
        if is_search_module == True and module_id:
            condition_where.add_condition("module_id=%s")
            params_list.append(module_id)
        if condition:
            condition_where.add_condition(condition)
            params_list.extend(params)
        act_prize_list_dict = ActPrizeModel(context=self.context).get_cache_dict_list("act_id=%s and is_prize_notice=0 and is_del=0", params=[act_id],cache_expire=60)
        if act_prize_list_dict:
            prize_id_list = [str(i["id"]) for i in act_prize_list_dict]
            if len(prize_id_list) > 0:
                prize_ids = ",".join(prize_id_list)
                condition_where.add_condition("prize_id not in (" + prize_ids + ")")
        prize_roster_model = PrizeRosterModel(context=self.context)
        prize_roster_list = prize_roster_model.get_cache_dict_list(condition_where.to_string(), "", "create_date desc", str(page_size), "user_nick,prize_name,tag_id,module_name", params_list, cache_expire=60)
        total = int(len(prize_roster_list))
        if total == 0:
            prize_roster_list = []
        else:
            for i in range(len(prize_roster_list)):
                if prize_roster_list[i]["user_nick"]:
                    length = len(prize_roster_list[i]["user_nick"])
                    if length > 2:
                        user_nick = prize_roster_list[i]["user_nick"][0:length - 2] + "**"
                    else:
                        user_nick = prize_roster_list[i]["user_nick"][0:1] + "*"
                    prize_roster_list[i]["user_nick"] = user_nick
        act_module_list = []
        if total < page_size:
            add_num = page_size - total
            act_prize_model = ActPrizeModel(context=self.context)
            prize_condition = "act_id=%s and is_prize_notice=1"
            prize_params = [act_id]

            if is_search_module == True:
                module_condition = "act_id=%s and is_fictitious=1"
                module_params = [act_id]
                if module_id >0:
                    module_condition += " and id=%s"
                    module_params = [act_id, module_id]
                act_module_list = ActModuleModel(context=self.context).get_cache_list(module_condition, params=module_params,cache_expire=60)
                if len(act_module_list) > 0:
                    module_id_list = [str(i.id) for i in act_module_list]
                    module_ids = ",".join(module_id_list)
                    prize_condition += " and module_id in (" + module_ids + ")"
            false_act_prize_list = act_prize_model.get_cache_list(prize_condition, order_by="probability desc,chance desc", limit="30", params=prize_params,cache_expire=60)
            if len(false_act_prize_list) > 0 and add_num > 0:
                now_datetime = TimeHelper.add_hours_by_format_time(hour=-random.randint(0, 1000))
                user_info_list_dict = UserInfoModel(context=self.context).get_dict_list("act_id<%s and create_date>%s", params=[act_id,now_datetime], limit=str(add_num))

                for i in range(len(user_info_list_dict)):
                    false_act_prize = false_act_prize_list[random.randint(0, len(false_act_prize_list)-1)]
                    if not false_act_prize:
                        continue
                    prize_roster = {}
                    if user_info_list_dict[i]["user_nick"]:
                        length = len(user_info_list_dict[i]["user_nick"])
                        if length > 2:
                            user_nick = user_info_list_dict[i]["user_nick"][0:length - 2] + "**"
                        else:
                            user_nick = user_info_list_dict[i]["user_nick"][0:1] + "*"
                    prize_roster["user_nick"] = user_nick
                    prize_roster["prize_name"] = false_act_prize.prize_name
                    prize_roster["tag_id"] = false_act_prize.tag_id
                    act_module_filter = [act_module for act_module in act_module_list if false_act_prize.module_id == act_module.id]
                    prize_roster["module_name"] = act_module_filter[0].module_name if len(act_module_filter) > 0 else ""
                    prize_roster_list.append(prize_roster)

        return prize_roster_list
