# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 18:31:06
@LastEditTime: 2022-01-26 17:16:34
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.user_base_model import *
from seven_cloudapp_frame.models.order_base_model import *
from seven_cloudapp_frame.models.stat_base_model import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.asset_base_model import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_coupon_model import *
from seven_cloudapp_frame.libs.customize.wechat_helper import *
from seven_cloudapp_frame.libs.customize.tiktok_helper import *

class LoginHandler(ClientBaseHandler):
    """
    :description: 登录处理
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 登录处理
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param avatar：头像
        :return:
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        open_id = self.get_param("open_id")
        user_nick = self.get_param("user_nick")
        act_id = int(self.get_param("act_id", 0))
        module_id = int(self.get_param("module_id", 0))
        avatar = self.get_param("avatar")
        code = self.get_param("code", "")
        anonymous_code = self.get_param("anonymous_code", "")
        pt = self.get_param("pt", "tb")  #tb淘宝 tt抖音 wx微信 qq h5

        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error","小程序不存在")

        if self.check_request_user(app_id, app_info_dict["current_limit_count"]):
            return self.response_json_error("current_limit", "登录失败")

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)

        if pt == "wx" and code:
            invoke_result_data = WeChatHelper.code2_session(code, app_id=config.get_value("app_id"), app_secret=config.get_value("app_secret"))
            if invoke_result_data.success == False:
                return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            open_id =  invoke_result_data.data["openid"]
        elif pt == "tt" and code:
            invoke_result_data = TikTokHelper.code2_session(code, anonymous_code, app_id=config.get_value("app_id"), app_secret=config.get_value("app_secret"))
            if invoke_result_data.success == False:
                return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            open_id = invoke_result_data.data["openid"]

        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.save_user_by_openid(app_id, act_id, open_id, user_nick, avatar)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data.data["user_nick"] = self.emoji_base64_to_emoji(invoke_result_data.data["user_nick"])
        if invoke_result_data.data["user_nick_encrypt"]:
            invoke_result_data.data["user_nick"] = CryptographyHelper.base64_decrypt(invoke_result_data.data["user_nick_encrypt"])
        ref_params = {}
        ref_params["app_id"] = app_id
        ref_params["act_id"] = act_id
        ref_params["module_id"] = module_id
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data:result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        user_info_dict = result_data.data
        stat_base_model = StatBaseModel(context=self)
        key_list_dict = {}
        key_list_dict["VisitCountEveryDay"] = 1
        key_list_dict["VisitManCountEveryDay"] = 1
        key_list_dict["VisitManCountEveryDayIncrease"] = 1
        stat_base_model.add_stat_list(ref_params["app_id"], ref_params["act_id"], ref_params["module_id"], user_info_dict["user_id"], user_info_dict["open_id"], key_list_dict)
        return result_data


class UpdateUserInfoHandler(ClientBaseHandler):
    """
    :description: 更新用户信息
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 更新用户信息
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param avatar：头像
        :param is_member_before：初始会员状态
        :param is_favor_before：初始关注状态
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        open_id = self.get_param("open_id")
        user_nick = self.get_param("user_nick")
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        avatar = self.get_param("avatar")
        is_member_before = int(self.get_param("is_member_before", -1))
        is_favor_before = int(self.get_param("is_favor_before", -1))

        invoke_result_data = InvokeResultData()
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.update_user_info(app_id, act_id, user_id, open_id, user_nick, avatar, is_member_before, is_favor_before)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        else:
            return self.response_json_success("更新成功")


class CheckIsMemberHandler(ClientBaseHandler):
    """
    :description: 校验是否是店铺会员
    """
    def get_async(self):
        """
        :description: 校验是否是店铺会员
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        mix_nick = self.get_param("mix_nick")
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        access_token = app_info_dict["access_token"]
        if access_token == "":
            return self.response_json_error("error", "未授权请联系客服授权")
        top_base_model = TopBaseModel(context=self)
        app_key,app_secret = self.get_app_key_secret()
        return self.response_json_success(top_base_model.check_is_member(mix_nick,"", access_token, app_key, app_secret, is_log))


class ApplyBlackUnbindHandler(ClientBaseHandler):
    """
    :description: 提交黑名单解封申请
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 提交黑名单解封申请
        :param act_id:活动标识
        :param tb_user_id:用户标识
        :param reason:解封理由
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        open_id = self.get_param("open_id")
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        reason = self.get_param("reason", "误封号,申请解封")

        invoke_result_data = InvokeResultData()
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.apply_black_unbind(app_id, act_id, user_id, open_id, reason)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        else:
            return self.response_json_success()


class GetUnbindApplyHandler(ClientBaseHandler):
    """
    :description: 获取黑名单解封申请记录
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 获取黑名单解封申请记录
        :param act_id:活动标识
        :param tb_user_id:用户标识
        :param reason:解封理由
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        user_base_model = UserBaseModel(context=self)
        return self.response_json_success(user_base_model.get_black_info_dict(app_id, act_id, user_id))


class GetCouponPrizeHandler(ClientBaseHandler):
    """
    :description: 领取淘宝优惠券
    """
    @filter_check_params("act_id,tb_user_id,user_prize_id")
    def get_async(self):
        """
        :description: 领取淘宝优惠券（发奖接口）
        :param user_prize_id:用户奖品标识
        :param tb_user_id:用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        user_prize_id = int(self.get_param("user_prize_id", 0))
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        access_token = app_info_dict["access_token"]
        if access_token == "":
            return self.response_json_error("error", "未授权请联系客服授权")
        dependency_key = f"prize_roster_list:actid_{act_id}_userid_{user_id}"
        prize_roster_model = PrizeRosterModel(context=self)
        prize_roster_dict = prize_roster_model.get_cache_dict_by_id(user_prize_id, dependency_key=dependency_key)
        if not prize_roster_dict or prize_roster_dict['user_id'] != user_id or prize_roster_dict['act_id'] != act_id:
            return self.response_json_error("error", "奖品不存在")
        tao_coupon_model = TaoCouponModel(context=self)
        tao_coupon_dict = tao_coupon_model.get_dict(where="prize_id=%s", limit="1", params=[prize_roster_dict["prize_id"]])
        if not tao_coupon_dict or tao_coupon_dict['right_ename'] == "":
            return self.response_json_error("error", "奖品不是优惠券,无需领取")
        top_base_model = TopBaseModel(context=self)
        app_key,app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.alibaba_benefit_send(tao_coupon_dict['right_ename'], prize_roster_dict["open_id"], access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return self.response_json_error("error", "领取失败")
        resp = invoke_result_data.data
        if resp["alibaba_benefit_send_response"]:
            if resp["alibaba_benefit_send_response"]["result_success"] == True:
                prize_roster_model.update_table("prize_status=1", "id=%s", params=[user_prize_id])
                prize_roster_model.delete_dependency_key(dependency_key)
                result = {}
                result["prize_name"] = resp["alibaba_benefit_send_response"]["prize_name"]
                return self.response_json_success(result)
            if resp["alibaba_benefit_send_response"]["result_code"] == "COUPON_INVALID_OR_DELETED":
                prize_roster_model.update_table("prize_status=10", "id=%s", params=[user_prize_id])
                prize_roster_model.delete_dependency_key(dependency_key)
                return self.response_json_error("error", "领取失败：优惠券无效或已删除")
            if resp["alibaba_benefit_send_response"]["result_code"] == "APPLY_SINGLE_COUPON_COUNT_EXCEED_LIMIT":
                return self.response_json_error("error", "领取失败：优惠券超过限额")
            if resp["alibaba_benefit_send_response"]["result_code"] == "USER_PERMISSION_EXCEED_MAX_RIGHT_COUNT_IN_DAY":
                return self.response_json_error("error", "领取失败：同一张优惠券每天限领取一次")
            if resp["alibaba_benefit_send_response"]["result_code"] == "APPLY_ONE_SELLER_COUNT_EXCEED_LIMIT":
                return self.response_json_error("error", "领取失败：用户优惠券超出10张限制")
        else:
            result = resp["sub_msg"] if resp["sub_msg"] else ""
            if result == "" and resp["result_msg"]:
                result = resp["result_msg"]
            return self.response_json_error("error", f"领取失败:{result}")


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
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        asset_type = int(self.get_param("asset_type", 0))

        asset_base_model = AssetBaseModel(context=self)
        return self.response_json_success(asset_base_model.get_user_asset_list(app_id, act_id, user_id, asset_type))


class AssetLogListHandler(ClientBaseHandler):
    """
    :description: 资产流水记录
    """
    @filter_check_params("act_id,tb_user_id,asset_type")
    def get_async(self):
        """
        :description: 资产流水记录
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param asset_type：资产类型(1-次数2-积分3-价格档位))
        :param asset_object_id：资产对象标识
        :param operate_type：操作类型(0累计 1消耗
        :param page_size：条数
        :param page_index：页数
        :return list
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        open_id = self.get_param("open_id")
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        asset_type = int(self.get_param("asset_type", 0))
        asset_object_id = self.get_param("asset_object_id")
        operate_type = int(self.get_param("operate_type", -1))

        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})
        if not invoke_result_data.data:
            invoke_result_data.data = {}
        field = invoke_result_data.data["field"] if invoke_result_data.data.__contains__("field") else "*"
        asset_base_model = AssetBaseModel(context=self)
        page_info = asset_base_model.get_asset_log_list(app_id, act_id, asset_type, page_size, page_index, user_id, asset_object_id, field=field, is_cache=True, operate_type=operate_type)
        ref_params = {}
        page_info.data = self.business_process_executed(page_info.data, ref_params)
        return self.response_json_success(page_info)


class GetJoinMemberUrlHandler(ClientBaseHandler):
    """
    :description: 获取加入会员地址
    """
    def get_async(self):
        """
        :description: 获取加入会员地址
        :return
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("error", "小程序不存在")
        app_key, app_secret = self.get_app_key_secret()
        user_base_model = UserBaseModel(context=self)
        invoke_result_data = user_base_model.get_join_member_url(app_info_dict["access_token"], app_key, app_secret, is_log=is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class UserAddressListHandler(ClientBaseHandler):
    """
    :description: 收货地址列表
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :return: list
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        open_id = self.get_param("open_id")
        user_id = self.get_user_id()
        user_base_model = UserBaseModel(context=self)
        return self.response_json_success(user_base_model.get_user_address_list(app_id, act_id, user_id))


class SaveUserAddressHandler(ClientBaseHandler):
    """
    :description: 保存收货地址
    """
    @filter_check_params("act_id,tb_user_id,real_name,telephone")
    def get_async(self):
        """
        :param act_id：活动标识
        :param tb_user_id：用户标识
        :param is_default：是否默认地址（1是0否）
        :param real_name：真实姓名
        :param telephone：手机号码
        :param province：省
        :param city：市
        :param county：区
        :param street：街道
        :param adress：地址
        :return: dict
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        act_id = int(self.get_param("act_id", 0))
        user_id = self.get_user_id()
        open_id = self.get_param("open_id")
        user_address_id = int(self.get_param("user_address_id", 0))
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        province = self.get_param("province")
        city = self.get_param("city")
        county = self.get_param("county")
        street = self.get_param("street")
        address = self.get_param("address")
        is_default = int(self.get_param("is_default", 0))

        user_base_model = UserBaseModel(context=self)
        return self.response_json_success(user_base_model.save_user_address(app_id, act_id, user_id, open_id, user_address_id, real_name, telephone, province, city, county, street, address, is_default))
