# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-27 10:52:51
@LastEditTime: 2021-12-21 10:27:54
@LastEditors: HuangJianYi
@Description: 用户模块
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.user_base_model import *
from seven_cloudapp_frame.models.asset_base_model import *
from seven_cloudapp_frame.libs.customize.oss2_helper import *
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_login_log_model import *


class LoginHandler(ClientBaseHandler):
    """
    :description: 登录处理
    """
    @filter_check_params("open_id")
    def get_async(self):
        """
        :description: 登录日志入库
        :param open_id：用户唯一标识
        :param user_nick：用户昵称
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_open_id()
        user_nick = self.get_user_nick()

        request_params = str(self.request_params)

        if user_nick == "":
            return self.response_json_success()

        tao_login_log_model = TaoLoginLogModel(context=self)
        tao_login_log = tao_login_log_model.get_entity("open_id=%s", params=open_id)

        is_add = False
        if not tao_login_log:
            is_add = True
            tao_login_log = TaoLoginLog()

        tao_login_log.open_id = open_id
        tao_login_log.user_nick = user_nick
        if user_nick.__contains__(":"):
            tao_login_log.store_user_nick = user_nick.split(":")[0]
            tao_login_log.is_master = 0
        else:
            tao_login_log.store_user_nick = user_nick
            tao_login_log.is_master = 1
        tao_login_log.request_params = request_params
        tao_login_log.modify_date = self.get_now_datetime()

        try:
            if is_add:
                tao_login_log.create_date = tao_login_log.modify_date
                tao_login_log.id = tao_login_log_model.add_entity(tao_login_log)
            else:
                tao_login_log_model.update_entity(tao_login_log)

            #更新登录时间到app_info
            app_id = self.get_app_id()
            if app_id:
                AppInfoModel(context=self).update_table("modify_date=%s", "app_id=%s", [tao_login_log.modify_date, app_id])
        except:
            pass

        return self.response_json_success()


class UpdateUserStatusHandler(ClientBaseHandler):
    """
    :description: 更新用户状态
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 更新用户状态
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param user_state：用户状态（0正常1黑名单）
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id"))
        user_id = self.get_user_id()
        user_state = int(self.get_param("user_state"))
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.update_user_state(app_id, act_id, user_id, user_state)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code,invoke_result_data.error_message)
        return self.response_json_success()


class UpdateUserStatusByBlackHandler(ClientBaseHandler):
    """
    :description: 用户拉入黑名单(黑名单管理模式)
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 用户拉入黑名单
        :param app_id：应用标识
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id"))
        user_id = self.get_user_id()
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.update_user_state_by_black(app_id, act_id, user_id)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code,invoke_result_data.error_message)
        ref_params = {}
        self.business_process_executed(invoke_result_data, ref_params)
        return self.response_json_success()


class AuditUserBlackHandler(ClientBaseHandler):
    """
    :description 审核黑名单状态
    """
    @filter_check_params("black_id,audit_status")
    def get_async(self):
        """
        :description: 审核黑名单状态
        :param black_id：用户黑名单管理标识
        :param audit_status：审核状态(0黑名单1申请中2同意3拒绝)
        :param audit_remark：审核备注
        :return: response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        black_id = int(self.get_param("black_id", 0))
        audit_status = int(self.get_param("audit_status", 0))
        audit_remark = self.get_param("audit_remark")

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.audit_user_black(app_id, black_id, audit_status, audit_remark)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code,invoke_result_data.error_message)
        ref_params = {}
        self.business_process_executed(invoke_result_data, ref_params)
        return self.response_json_success()


class UpdateAuditRemarkHandler(ClientBaseHandler):
    """
    :description 修改审核备注
    """
    @filter_check_params("black_id,audit_status")
    def get_async(self):
        """
        :description: 修改审核备注
        :param black_id：用户黑名单管理标识
        :param audit_remark：审核备注
        :return: response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        black_id = int(self.get_param("black_id", 0))
        audit_remark = self.get_param("audit_remark")
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.update_audit_remark(app_id, black_id, audit_remark)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success()


class UserBlackListHandler(ClientBaseHandler):
    """
    :description: 获取黑名单管理列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取黑名单管理列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param audit_status：审核状态(0黑名单1申请中2同意3拒绝)
        :param user_id：用户标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param nick_name：用户昵称
        :param user_open_id：open_id
        :param page_size：条数
        :param page_index：页数
        :return: list
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        audit_status = int(self.get_param("audit_status", -1))
        user_id = self.get_user_id()
        user_nick = self.get_param("nick_name")
        open_id = self.get_param("user_open_id")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        page_size = int(self.get_param("page_size", 20))
        page_index = int(self.get_param("page_index", 0))

        user_base_model = UserBaseModel(context=self)
        return self.response_json_success(user_base_model.get_black_list(app_id, act_id, page_size, page_index, audit_status, user_id, start_date, end_date, user_nick, open_id))


class UpdateUserAssetHandler(ClientBaseHandler):
    """
    :description: 变更资产
    """
    @filter_check_params("act_id,tb_user_id,asset_type,asset_value")
    def post_async(self):
        """
        :description: 变更资产
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param asset_type：资产类型
        :param asset_value：变更的资产值
        :param asset_object_id：资产对象标识
        :return: response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        asset_type = int(self.get_param("asset_type", 0))
        asset_value = int(self.get_param("asset_value", 0))
        asset_object_id = self.get_param("asset_object_id")

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code,invoke_result_data.error_message)

        user_base_model = UserBaseModel(context=self)
        user_info_dict = user_base_model.get_user_info_dict(app_id, act_id, user_id)
        if not user_info_dict:
            return self.response_json_error("error","用户信息不存在")

        asset_base_model = AssetBaseModel(context=self)
        invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, 0, user_id, user_info_dict["open_id"], user_info_dict["user_nick"], asset_type, asset_value, asset_object_id, 3, "", "手动配置", "手动配置")
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code,invoke_result_data.error_message)
        ref_params = {}
        self.business_process_executed(invoke_result_data, ref_params)
        return self.response_json_success()


class BatchUpdateUserAssetHandler(ClientBaseHandler):
    """
    :description: 批量变更资产
    """
    @filter_check_params("act_id,tb_user_id,asset_object_json")
    def post_async(self):
        """
        :description: 批量变更资产
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param asset_object_json：变更的资产值列表
        :return: response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        #{"asset_type":0,"asset_object_id":"","asset_value":0}
        asset_object_json = self.get_param("asset_object_json")

        user_base_model = UserBaseModel(context=self)
        user_info_dict = user_base_model.get_user_info_dict(app_id, act_id, user_id)
        if not user_info_dict:
            return self.response_json_error("error", "用户信息不存在")

        asset_base_model = AssetBaseModel(context=self)
        asset_object_json = SevenHelper.json_loads(asset_object_json)
        asset_object_ids = ""
        for asset_object in asset_object_json:
            invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, 0, user_id, user_info_dict["open_id"], user_info_dict["user_nick"], int(asset_object["asset_type"]), int(asset_object["asset_value"]), asset_object["asset_object_id"], 3, "", "手动配置", "手动配置")
            if invoke_result_data.success == False:
                return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message, asset_object_ids)
            else:
                if asset_object_ids:
                    asset_object_ids += ","
                asset_object_ids += asset_object["asset_object_id"]

        return self.response_json_success()


class UserAssetListHandler(ClientBaseHandler):
    """
    :description: 获取用户资产列表
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 获取用户资产列表
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param asset_type：资产类型(1-次数2-积分3-价格档位)
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        asset_type = int(self.get_param("asset_type", 0))

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})
        asset_base_model = AssetBaseModel(context=self)
        ref_params = {}
        return self.response_json_success(self.business_process_executed(asset_base_model.get_user_asset_list(app_id, act_id, user_id, asset_type), ref_params))


class AssetLogListHandler(ClientBaseHandler):
    """
    :description: 资产流水记录
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 资产流水记录
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
        :param operate_type：操作类型(0累计 1消耗)
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        user_id = self.get_user_id()
        user_open_id = self.get_param("user_open_id")
        user_nick = self.get_param("nick_name")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        source_type = int(self.get_param("source_type", 0))
        source_object_id = self.get_param("source_object_id")
        asset_type = int(self.get_param("asset_type", 0))
        asset_object_id = self.get_param("asset_object_id")
        operate_type = int(self.get_param("operate_type", -1))

        field = "*"
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})
        else:
            field = invoke_result_data.data["field"] if invoke_result_data.data.__contains__("field") else "*"
        asset_base_model = AssetBaseModel(context=self)
        page_info = asset_base_model.get_asset_log_list(app_id, act_id, asset_type, page_size, page_index, user_id, asset_object_id, start_date, end_date, user_nick, user_open_id, source_type, source_object_id, field, is_cache=False, operate_type=operate_type)
        ref_params = {}
        page_info.data = self.business_process_executed(page_info.data, ref_params)
        return self.response_json_success(page_info)


class UserInfoListHandler(ClientBaseHandler):
    """
    :description: 用户信息列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户信息列表
        :param act_id：活动标识
        :param user_id：用户标识
        :param user_open_id：_open_id
        :param nick_name：用户昵称
        :param user_state：_用户状态0正常1黑名单
        :param page_index：页索引
        :param page_size：页大小
        :param start_date：创建时间开始
        :param end_date：创建时间结束
        :return PageInfo
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        open_id = self.get_param("user_open_id")
        user_nick = self.get_param("nick_name")
        user_state = int(self.get_param("user_state", -1))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        user_base_model = UserBaseModel(context=self)
        page_info = user_base_model.get_user_list(app_id, act_id, page_size, page_index, user_state, user_id, start_date, end_date, user_nick, open_id)
        ref_params = {}
        return self.response_json_success(self.business_process_executed(page_info, ref_params))