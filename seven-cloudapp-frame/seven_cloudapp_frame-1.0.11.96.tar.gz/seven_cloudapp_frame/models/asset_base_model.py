# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-05-12 20:11:48
@LastEditTime: 2022-01-13 14:31:54
@LastEditors: HuangJianYi
:description: 
"""
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.db_models.asset.asset_log_model import *
from seven_cloudapp_frame.models.db_models.asset.asset_only_model import *
from seven_cloudapp_frame.models.db_models.user.user_asset_model import *
from seven_cloudapp_frame.models.db_models.asset.asset_warn_notice_model import *
from seven_cloudapp_frame.models.seven_model import *


class AssetBaseModel():
    """
    :description: 资产管理业务模型
    """
    def __init__(self,context=None,logging_error=None,logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info


    def _delete_asset_dependency_key(self,act_id,user_id):
        """
        :description: 删除资产依赖建
        :param act_id: 活动标识
        :param user_id: 用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            redis_init = SevenHelper.redis_init()
            if act_id and user_id:
                redis_init.delete(f"asset_log_list:actid_{act_id}_userid_{user_id}")
        except Exception as ex:
            pass

    def _add_onlyid_warn_stat(self,handler_name):
        """
        :description: 添加唯一标识预警拦截计数
        :param handler_name：接口名称
        :return: 
        :last_editors: HuangJianYi
        """
        if handler_name:
            handler_name = str(handler_name).lower()
            redis_init = SevenHelper.redis_init()

            hash_name_1 = f"warn_handler_list_{str(SevenHelper.get_now_int(fmt='%Y%m%d'))}"
            hash_key_1 = f"handlername_{handler_name}"
            if not redis_init.hexists(hash_name_1, hash_key_1):
                redis_init.hset(hash_name_1,hash_key_1,SevenHelper.json_dumps({"app_id":'',"handler_name":handler_name}))
                redis_init.expire(hash_name_1, 24 * 3600)

            hash_name_2 = f"{hash_name_1}:{hash_key_1}"
            redis_init.hincrby(hash_name_2, str(SevenHelper.get_now_int(fmt='%Y%m%d%H%M')), 1)
            redis_init.expire(hash_name_2, 24 * 3600)

    def get_user_asset_id_md5(self, act_id, user_id, asset_type, asset_object_id):
        """
        :description: 生成用户资产唯一标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :param asset_object_id：对象标识
        :return: 用户资产唯一标识
        :last_editors: HuangJianYi
        """
        if not act_id or not user_id or not asset_type:
            return 0
        return CryptoHelper.md5_encrypt_int(f"{act_id}_{user_id}_{asset_type}_{asset_object_id}")

    def get_asset_check_code(self, id_md5, asset_value, sign_key):
        """
        :description: 生成用户资产校验码
        :param 用户资产唯一标识
        :param id_md5：id_md5
        :param asset_value：当前资产值
        :param sign_key：签名key,目前使用app_id作为签名key
        :return: 用户资产校验码
        :last_editors: HuangJianYi
        """
        if not id_md5 or not asset_value:
            return ""
        return CryptoHelper.md5_encrypt(f"{id_md5}_{asset_value}", sign_key)

    def update_user_asset(self, app_id, act_id, module_id, user_id, open_id, user_nick, asset_type, asset_value, asset_object_id, source_type, source_object_id, source_object_name, log_title, only_id="",handler_name="",request_code="", info_json={}):
        """
        :description: 变更资产
        :param act_id：活动标识
        :param module_id：模块标识，没有填0
        :param user_id：用户标识
        :param open_id：open_id
        :param user_nick：昵称
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :param asset_value：变动的资产值，算好差值传入
        :param asset_object_id：资产对象标识
        :param source_type：来源类型（1-购买2-任务3-手动配置4-抽奖5-回购）
        :param source_object_id：来源对象标识(比如来源类型是任务则对应任务类型)
        :param source_object_name：来源对象名称(比如来源类型是任务则对应任务名称)
        :param log_title：资产流水标题
        :param only_id:唯一标识(用于并发操作时校验避免重复操作)由业务方定义传入
        :param handler_name:接口名称
        :param request_code:请求唯一标识，从seven_framework框架获取对应request_code
        :param info_json：资产流水详情，用于存放业务方自定义字典
        :return: 返回实体InvokeResultData
        :last_editors: HuangJianYi
        """

        invoke_result_data = InvokeResultData()

        if not act_id or not user_id or not asset_type or not asset_value:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data

        if int(asset_type) == 3 and not asset_object_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "资产类型为价格档位,参数asset_object_id不能为空或等于0"
            return invoke_result_data
        asset_value = int(asset_value)
        user_asset_id_md5 = self.get_user_asset_id_md5(act_id, user_id, asset_type, asset_object_id)
        if user_asset_id_md5 == 0:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "修改失败"
            return invoke_result_data
        #如果only_id已经存在，直接在redis进行拦截,减少数据库的请求，时限1天
        redis_init = SevenHelper.redis_init()
        only_cache_key = ""
        if only_id:
            only_cache_key = f"asset_only_list:{act_id}_{SevenHelper.get_now_day_int()}"
            if redis_init.hexists(only_cache_key, only_id):
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "only_id已经存在"
                #添加唯一标识预警拦截计数,用于控制台跑数据进行并发预警
                self._add_onlyid_warn_stat(handler_name)
                return invoke_result_data
        sub_table = SevenHelper.get_sub_table(act_id,config.get_value("asset_sub_table_count",0))
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        user_asset_model = UserAssetModel(db_transaction=db_transaction, sub_table=sub_table, context=self.context)
        asset_log_model = AssetLogModel(db_transaction=db_transaction, sub_table=sub_table, context=self.context)
        asset_only_model = AssetOnlyModel(db_transaction=db_transaction, sub_table=sub_table, context=self.context)

        acquire_lock_name = f"userasset:{user_asset_id_md5}"
        acquire_lock_status, identifier = SevenHelper.redis_acquire_lock(acquire_lock_name)
        if acquire_lock_status == False:
            invoke_result_data.success = False
            invoke_result_data.error_code = "acquire_lock"
            invoke_result_data.error_message = "系统繁忙,请稍后再试"
            return invoke_result_data

        try:
            now_day_int = SevenHelper.get_now_day_int()
            now_datetime = SevenHelper.get_now_datetime()
            old_user_asset_id = 0
            history_asset_value = 0

            user_asset = user_asset_model.get_entity("id_md5=%s",params=[user_asset_id_md5])
            if user_asset:
                if user_asset.asset_value + asset_value < 0:
                    SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "no_enough"
                    invoke_result_data.error_message = "变更后的资产不能为负数"
                    return invoke_result_data
                if user_asset.asset_value + asset_value > 2147483647:
                    SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "no_enough"
                    invoke_result_data.error_message = "变更后的资产不能大于整形的最大值"
                    return invoke_result_data

                old_user_asset_id = user_asset.id
                history_asset_value = user_asset.asset_value
            else:
                if asset_value < 0:
                    SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "no_enough"
                    invoke_result_data.error_message = "资产不能为负数"
                    return invoke_result_data
                user_asset = UserAsset()
                user_asset.id_md5 = user_asset_id_md5
                user_asset.app_id = app_id
                user_asset.act_id = act_id
                user_asset.user_id = user_id
                user_asset.open_id = open_id
                user_asset.user_nick = user_nick
                user_asset.asset_type = asset_type
                user_asset.asset_object_id = asset_object_id
                user_asset.create_date = now_datetime

            user_asset.asset_value += asset_value
            user_asset.asset_check_code = self.get_asset_check_code(user_asset_id_md5, user_asset.asset_value, app_id)
            user_asset.modify_date = now_datetime

            asset_log = AssetLog()
            asset_log.app_id = app_id
            asset_log.act_id = act_id
            asset_log.module_id = module_id
            asset_log.user_id = user_id
            asset_log.open_id = open_id
            asset_log.user_nick = user_nick
            asset_log.log_title = log_title
            asset_log.info_json = info_json if info_json else {}
            asset_log.asset_type = asset_type
            asset_log.asset_object_id = asset_object_id
            asset_log.source_type = source_type
            asset_log.source_object_id = source_object_id
            asset_log.source_object_name = source_object_name
            asset_log.only_id = only_id
            asset_log.operate_type = 0 if asset_value > 0 else 1
            asset_log.operate_value = asset_value
            asset_log.history_value = history_asset_value
            asset_log.now_value = user_asset.asset_value
            asset_log.handler_name = handler_name
            asset_log.request_code = request_code
            asset_log.create_date = now_datetime
            asset_log.create_day = now_day_int

            if only_id:
                asset_only = AssetOnly()
                asset_only.id_md5 = CryptoHelper.md5_encrypt_int(f"{act_id}_{user_id}_{only_id}")
                asset_only.app_id = app_id
                asset_only.act_id = act_id
                asset_only.user_id = user_id
                asset_only.open_id = open_id
                asset_only.only_id = only_id
                asset_only.create_date = now_datetime

            db_transaction.begin_transaction()

            if old_user_asset_id != 0:
                user_asset_model.update_entity(user_asset, "asset_value,asset_check_code,modify_date")
            else:
                user_asset_model.add_entity(user_asset)
            if only_id:
                asset_only_model.add_entity(asset_only)
            asset_log_model.add_entity(asset_log)

            result = db_transaction.commit_transaction()
            if not result:
                if only_id:
                    #添加唯一标识预警拦截计数,用于控制台跑数据进行并发预警
                    self._add_onlyid_warn_stat(handler_name)
                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                invoke_result_data.success = False
                invoke_result_data.error_code = "fail"
                invoke_result_data.error_message = "系统繁忙,请稍后再试"
                return invoke_result_data

            if only_id:
                redis_init.hset(only_cache_key, only_id, 1)
                redis_init.expire(only_cache_key, 24 * 3600)
            self._delete_asset_dependency_key(act_id,user_id)

            asset_queue = {}
            asset_queue["app_id"] = app_id
            asset_queue["act_id"] = act_id
            asset_queue["open_id"] = open_id
            asset_queue["user_nick"] = user_nick
            asset_queue["user_id"] = user_id
            asset_queue["asset_type"] = asset_type
            asset_queue["asset_object_id"] = asset_object_id
            asset_queue["now_value"] = user_asset.asset_value
            asset_queue["operate_value"] = asset_value
            asset_queue["history_asset_value"] = history_asset_value
            asset_queue["now_day_int"] = now_day_int
            asset_queue["create_date"] = now_datetime
            redis_init.rpush(f"asset_queue_list:{str(user_id % 10)}",SevenHelper.json_dumps(asset_queue))

            invoke_result_data.data = {"user_asset":user_asset.__dict__}

        except Exception as ex:
            if self.context:
                self.context.logging_link_error("【变更资产】" + traceback.format_exc())
            elif self.logging_link_error:
                self.logging_link_error("【变更资产】" + traceback.format_exc())
            if db_transaction.is_transaction == True:
                db_transaction.rollback_transaction()
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = "系统繁忙,请稍后再试"
        finally:
            SevenHelper.redis_release_lock(acquire_lock_name, identifier)

        return invoke_result_data

    def get_user_asset_list(self, app_id, act_id, user_ids, asset_type=0):
        """
        :description: 获取用户资产列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_ids：用户标识 多个逗号,分隔
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :return: 返回list
        :last_editors: HuangJianYi
        """
        if not act_id or not user_ids:
            return []
        condition = "act_id=%s"
        params = [act_id]
        if asset_type > 0:
            condition+= " AND asset_type=%s"
            params.append(asset_type)
        if user_ids:
            if ',' in str(user_ids):
                condition += f" AND user_id in ({user_ids})"
            elif isinstance(user_ids,list):
                condition+=" AND " + SevenHelper.get_condition_by_int_list("user_id",user_ids)
            else:
                condition += " AND user_id=%s"
                params.append(user_ids)
        sub_table = SevenHelper.get_sub_table(act_id,config.get_value("asset_sub_table_count",0))
        user_asset_model = UserAssetModel(sub_table=sub_table, context=self.context)
        user_asset_dict_list = user_asset_model.get_dict_list(condition, params=params)
        if len(user_asset_dict_list) > 0:
            for user_asset_dict in user_asset_dict_list:
                if user_asset_dict["app_id"] != str(app_id):
                    user_asset_dict["asset_value"] = 0
                if self.get_asset_check_code(user_asset_dict["id_md5"], user_asset_dict["asset_value"], app_id) != user_asset_dict["asset_check_code"]:
                    user_asset_dict["asset_value"] = 0
        return user_asset_dict_list

    def get_user_asset(self, app_id, act_id, user_id, asset_type, asset_object_id):
        """
        :description: 获取具体的用户资产
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :param asset_object_id：资产对象标识,没有传空
        :return: 返回list
        :last_editors: HuangJianYi
        """
        if not act_id or not user_id or not asset_type:
            return None
        sub_table = SevenHelper.get_sub_table(act_id,config.get_value("asset_sub_table_count",0))
        user_asset_model = UserAssetModel(sub_table=sub_table, context=self.context)
        user_asset_id_md5 = self.get_user_asset_id_md5(act_id, user_id, asset_type, asset_object_id)
        user_asset_dict = user_asset_model.get_dict("id_md5=%s",params=[user_asset_id_md5])
        if user_asset_dict:
            if user_asset_dict["app_id"] != str(app_id):
                user_asset_dict["asset_value"] = 0
            if self.get_asset_check_code(user_asset_dict["id_md5"], user_asset_dict["asset_value"], app_id) != user_asset_dict["asset_check_code"]:
                user_asset_dict["asset_value"] = 0
        return user_asset_dict

    def get_asset_log_list(self, app_id, act_id, asset_type, page_size=20, page_index=0, user_id=0, asset_object_id="", start_date="", end_date="", user_nick="", open_id="", source_type=0, source_object_id=None, field="*", is_cache=True, operate_type=-1):
        """
        :description: 获取用户资产流水记录
        :param app_id：应用标识
        :param act_id：活动标识
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :param page_size：条数
        :param page_index：页数
        :param user_id：用户标识
        :param asset_object_id：资产对象标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param user_nick：昵称
        :param open_id：open_id
        :param source_type：来源类型（1-购买2-任务3-手动配置4-抽奖5-回购）
        :param source_object_id：来源对象标识(比如来源类型是任务则对应任务类型)
        :param field：查询字段
        :param is_cache：是否缓存
        :param operate_type：操作类型 （0累计 1消耗）
        :return: 返回PageInfo
        :last_editors: HuangJianYi
        """
        page_info = PageInfo(page_index, page_size, 0, [])
        if not act_id or asset_type <= 0:
            return page_info

        condition = "act_id=%s AND asset_type=%s"
        params = [act_id, asset_type]

        if app_id:
            condition += " AND app_id=%s"
            params.append(app_id)
        if user_id != 0:
            condition += " AND user_id=%s"
            params.append(user_id)
        if open_id:
            condition += " AND open_id=%s"
            params.append(open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if asset_object_id:
            condition += " AND asset_object_id=%s"
            params.append(asset_object_id)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)
        if source_type != 0:
            condition += " AND source_type=%s"
            params.append(source_type)
        if operate_type != -1:
            condition += " AND operate_type=%s"
            params.append(operate_type)
        if source_object_id:
            if type(source_object_id) == str:
                condition += " AND " + SevenHelper.get_condition_by_str_list("source_object_id",source_object_id.split(","))
            elif type(source_object_id) == list:
                condition += " AND " + SevenHelper.get_condition_by_str_list("source_object_id",source_object_id)
            else:
                condition += " AND source_object_id=%s"
                params.append(source_object_id)
        sub_table = SevenHelper.get_sub_table(act_id,config.get_value("asset_sub_table_count",0))
        asset_log_model = AssetLogModel(sub_table=sub_table, context=self.context)
        if is_cache:
            page_list, total = asset_log_model.get_cache_dict_page_list(field, page_index, page_size, condition, order_by="create_date desc", params=params,dependency_key=f"asset_log_list:actid_{act_id}_userid_{user_id}")
        else:
            page_list, total = asset_log_model.get_dict_page_list(field, page_index, page_size, condition, order_by="create_date desc", params=params)
        if len(page_list) > 0:
            for item in page_list:
                item["create_day"] = TimeHelper.format_time_to_datetime(str(item["create_date"])).strftime('%Y-%m-%d')
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info

    def get_asset_warn_list(self, app_id, act_id,  asset_type, page_size=20, page_index=0,user_id=0,asset_object_id="", start_date="", end_date="", user_nick="", open_id="", field="*"):
        """
        :description: 获取资产预警记录
        :param app_id：应用标识
        :param act_id：活动标识
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :param page_size：条数
        :param page_index：页数
        :param user_id：用户标识
        :param asset_object_id：资产对象标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param user_nick：昵称
        :param open_id：open_id
        :param field：查询字段
        :return: 返回PageInfo
        :last_editors: HuangJianYi
        """
        page_info = PageInfo(page_index, page_size, 0, [])
        if not act_id:
            return page_info

        condition = "act_id=%s and asset_type=%s"
        params = [act_id, asset_type]
        if app_id:
            condition += " AND app_id=%s"
            params.append(app_id)
        if asset_type != 0:
            condition += " AND asset_type=%s"
            params.append(asset_type)
        if asset_object_id:
            condition += " AND asset_object_id=%s"
            params.append(asset_object_id)
        if user_id != 0:
            condition += " AND user_id=%s"
            params.append(user_id)
        if open_id:
            condition += " AND open_id=%s"
            params.append(open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)

        page_list, total = AssetWarnNoticeModel(context=self.context).get_dict_page_list(field, page_index, page_size, condition, order_by="id desc", params=params)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info