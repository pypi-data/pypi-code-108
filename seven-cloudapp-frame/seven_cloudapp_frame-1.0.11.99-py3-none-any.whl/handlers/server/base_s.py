# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 17:00:55
@LastEditTime: 2021-12-29 15:32:27
@LastEditors: HuangJianYi
@Description: 基础模块
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.cms_base_model import *
from seven_cloudapp_frame.models.db_models.cms.cms_info_model import *
from seven_cloudapp_frame.models.db_models.saas.saas_custom_model import *
from seven_cloudapp_frame.models.db_models.marketing.marketing_program_model import *
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class LeftNavigationHandler(ClientBaseHandler):
    """
    :description: 左侧导航栏
    """
    def get_async(self):
        """
        :description: 左侧导航栏
        :return:
        :last_editors: HuangJianYi
        """
        app_base_model = AppBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = app_base_model.get_left_navigation(self.get_user_nick(), self.get_param("access_token"), app_key, app_secret, self.get_param("app_id"))
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class FriendLinkListHandler(ClientBaseHandler):
    """
    :description: 获取友情链接产品互推列表
    """
    def get_async(self):
        """
        :description: 获取友情链接产品互推列表
        :param {*}
        :return list
        :last_editors: HuangJianYi
        """
        friend_link_model = FriendLinkModel(context=self.context)
        friend_link_list = friend_link_model.get_cache_list(where="is_release=1")
        return self.response_json_success(friend_link_list)


class SaasCustomHandler(ClientBaseHandler):
    """
    :description: saas定制化信息获取
    """
    def get_async(self):
        """
        :description: saas定制化信息获取
        :param {*}
        :return int
        :last_editors: HuangJianYi
        """
        user_nick = self.get_user_nick()
        if not user_nick:
            return self.response_json_success(0)
        store_user_nick = user_nick.split(':')[0]
        if not store_user_nick:
            return self.response_json_success(0)
        cloud_app_id = 0
        saas_custom = SaasCustomModel(context=self).get_entity("store_user_nick=%s AND is_release=1", params=store_user_nick)
        if saas_custom:
            cloud_app_id = saas_custom.cloud_app_id

        return self.response_json_success(cloud_app_id)


class SendSmsHandler(ClientBaseHandler):
    """
    :description: 发送短信
    """
    def get_async(self):
        """
        :description: 发送短信
        :param thelephone：电话号码
        :return 
        :last_editors: HuangJianYi
        """
        open_id = self.get_open_id()
        thelephone = self.get_param("thelephone")
        client = AcsClient('LTAI4FwMYR1FBBui21t7cyh7', 'zyTM5zpYcL8lMXwtDgVoCfHgndoSKi', 'cn-hangzhou')

        result_code = str(random.randint(100000, 999999))
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', thelephone)
        request.add_query_param('SignName', "天志互联")
        request.add_query_param('TemplateCode', "SMS_193145309")
        request.add_query_param('TemplateParam', "{\"code\":" + result_code + "}")

        response = client.do_action(request)

        result = dict(json.loads(response))
        result["result_code"] = result_code
        #记录验证码
        SevenHelper.redis_init().set("user_" + open_id + "_bind_phone_code", result_code, ex=300)

        return self.response_json_success()


class MarketingProgramListHandler(ClientBaseHandler):
    """
    :description: 获取营销方案列表获取营销方案列表
    """
    def get_async(self):
        """
        :description: 获取营销方案列表
        :return: 列表
        :last_editors: HuangJianYi
        """
        marketing_program_list = MarketingProgramModel(context=self).get_cache_dict_list()
        return self.response_json_success(marketing_program_list)


class SaveCmsInfoHandler(ClientBaseHandler):
    """
    :description: 保存位置信息
    """
    @filter_check_params("place_id,info_title")
    def get_async(self):
        """
        :description: 保存位置信息
        :params place_id:位置标识
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        place_id = int(self.get_param("place_id", 0))
        cms_id = int(self.get_param("cms_id", 0))
        info_title = self.get_param("info_title")
        simple_title = self.get_param("simple_title")
        simple_title_url = self.get_param("simple_title_url")
        info_type = int(self.get_param("info_type", 0))
        info_summary = self.get_param("info_summary")
        info_tag = self.get_param("info_tag")
        info_mark = self.get_param("info_mark")
        target_url = self.get_param("target_url")
        min_pic = self.get_param("min_pic")
        mid_pic = self.get_param("mid_pic")
        max_pic = self.get_param("max_pic")
        info_data = self.get_param("info_data")
        pic_collect_json = self.get_param("pic_collect_json")
        sort_index = int(self.get_param("sort_index", 0))
        is_release = int(self.get_param("is_release", 0))
        i1 = int(self.get_param("i1", 0))
        i2 = int(self.get_param("i2", 0))
        i3 = int(self.get_param("i3", 0))
        i4 = int(self.get_param("i4", 0))
        s1 = self.get_param("s1")
        s2 = self.get_param("s2")
        s3 = self.get_param("s3")
        s4 = self.get_param("s4")

        cms_base_model = CmsBaseModel(context=self)
        invoke_result_data = cms_base_model.save_cms_info(place_id, cms_id, app_id, act_id, info_title, simple_title, simple_title_url, info_type, info_summary, info_tag, info_mark, target_url, min_pic, mid_pic, max_pic, info_data, pic_collect_json, sort_index, is_release, i1, i2, i3, i4, s1, s2, s3, s4)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if invoke_result_data.data["is_add"] == True:
            # 记录日志
            self.create_operation_log(OperationType.add.value, invoke_result_data.data["new"].__str__(), "SaveCmsInfoHandler", None, self.json_dumps(invoke_result_data.data["new"]), self.get_open_id(), self.get_user_nick())
        else:
            self.create_operation_log(OperationType.update.value, invoke_result_data.data["new"].__str__(), "SaveCmsInfoHandler", self.json_dumps(invoke_result_data.data["old"]), self.json_dumps(invoke_result_data.data["new"]), self.get_open_id(), self.get_user_nick())

        return self.response_json_success(invoke_result_data.data["new"].id)


class CmsInfoListHandler(ClientBaseHandler):
    """
    :description: 获取位置信息列表
    """
    @filter_check_params("place_id")
    def get_async(self):
        """
        :description: 获取位置信息列表
        :params place_id:位置标识
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        place_id = int(self.get_param("place_id", 0))
        page_size = int(self.get_param("page_size", 20))
        page_index = int(self.get_param("page_index", 0))

        order_by = "id desc"
        field = "*"
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_success({"data": []})
        else:
            order_by = invoke_result_data.data["order_by"] if invoke_result_data.data.__contains__("order_by") else "id desc"
            field = invoke_result_data.data["field"] if invoke_result_data.data.__contains__("field") else "*"
        cms_base_model = CmsBaseModel(context=self)
        page_list, total = self.business_process_executed(cms_base_model.get_cms_info_list(place_id=place_id, page_size=page_size, page_index=page_index, order_by=order_by, field=field, app_id=app_id, act_id=act_id, is_cache=False), ref_params={})
        page_info = PageInfo(page_index, page_size, total, self.business_process_executed(page_list, ref_params={}))
        return self.response_json_success(page_info)


class GetProductPriceHandler(ClientBaseHandler):
    """
    :description: 获取产品价格信息
    """
    def get_async(self):
        """
        :description: 获取产品价格信息
        :return 
        :last_editors: HuangJianYi
        """
        product_price_model = ProductPriceModel(context=self)
        now_date = SevenHelper.get_now_datetime()
        product_price = product_price_model.get_dict(where="%s>=begin_time and %s<=end_time and is_release=1", order_by="create_time desc", params=[now_date, now_date])
        if not product_price:
            return self.response_json_error("error", "找不到产品价格信息")
        try:
            product_price["content"] = SevenHelper.json_loads(product_price["content"])
        except:
            return self.response_json_error("error", "产品价格信息格式有误")

        return self.reponse_json_success(product_price)