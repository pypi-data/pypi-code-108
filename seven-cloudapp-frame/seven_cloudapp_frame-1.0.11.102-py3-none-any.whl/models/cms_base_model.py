# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-11-26 10:22:44
@LastEditTime: 2022-01-13 14:50:51
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.seven_model import PageInfo
from seven_cloudapp_frame.models.db_models.cms.cms_info_model import *

class CmsBaseModel():
    """
    :description: 位置信息（资讯）相关业务模型 用于后台或者中台案例和教程等配置信息
    """
    def __init__(self,context=None,logging_error=None,logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info
    
    def _delete_cms_info_dependency_key(self, place_id):
        """
        :description: 删除位置信息依赖建
        :param place_id: 位置标识
        :param act_id: 活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            redis_init = SevenHelper.redis_init()
            if place_id:
                redis_init.delete(f"cms_info_list:placeid_{place_id}")
        except Exception as ex:
            pass

    def save_cms_info(self, place_id, cms_id, app_id, act_id, info_title, simple_title, simple_title_url, info_type, info_summary, info_tag, info_mark, target_url, min_pic, mid_pic, max_pic, info_data, pic_collect_json, sort_index, is_release, i1, i2, i3, i4, s1, s2, s3, s4):
        """
        :description: 保存位置信息
        :param place_id：位置标识
        :param cms_id：信息标识
        :param app_id：应用标识
        :param act_id：活动标识
        :param info_title：信息标题
        :param simple_title：信息短标题
        :param simple_title_url：短标题链接
        :param info_type：短标题链接
        :param info_summary：短标题链接
        :param info_tag：信息标签[文章内容特性][砍人事件]
        :param info_mark：信息标记[首发,推荐,独家，热门]
        :param target_url：跳转地址
        :param min_pic：信息小图
        :param mid_pic：信息中图
        :param max_pic：信息大图
        :param info_data：信息内容
        :param pic_collect_json：图集json
        :param sort_index：排序
        :param is_release：是否发布（1是0否）
        :param i1：i1
        :param i2：i2
        :param i3：i3
        :param i4：i4
        :param s1：s1
        :param s2：s2
        :param s3：s3
        :param s4：s4
        :return
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not place_id or not info_title:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data

        cms_info = None
        is_add = False
        cms_info_model = CmsInfoModel(context=self.context)
        if cms_id > 0:
            cms_info = cms_info_model.get_entity_by_id(cms_id)
            if not cms_info or (app_id and cms_info.app_id != app_id):
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "信息不存在"
                return invoke_result_data
            old_cms_info = deepcopy(cms_info)
        if not cms_info:
            is_add = True
            cms_info = CmsInfo()
        cms_info.place_id = place_id
        cms_info.app_id = app_id
        cms_info.act_id = act_id
        cms_info.info_title = info_title
        cms_info.simple_title = simple_title
        cms_info.simple_title_url = simple_title_url
        cms_info.info_type = info_type
        cms_info.info_summary = info_summary
        cms_info.info_tag = info_tag
        cms_info.info_mark = info_mark
        cms_info.target_url = target_url
        cms_info.min_pic = min_pic
        cms_info.mid_pic = mid_pic
        cms_info.max_pic = max_pic
        cms_info.info_data = info_data
        cms_info.pic_collect_json = pic_collect_json if pic_collect_json else []
        cms_info.sort_index = sort_index
        cms_info.i1 = i1
        cms_info.i2 = i2
        cms_info.i3 = i3
        cms_info.i4 = i4
        cms_info.s1 = s1
        cms_info.s2 = s2
        cms_info.s3 = s3
        cms_info.s4 = s4
        cms_info.modify_date = SevenHelper.get_now_datetime()
        cms_info.is_release = is_release
        if is_release == 1:
            cms_info.release_date = cms_info.modify_date
        if is_add:
            cms_info.create_date = cms_info.modify_date
            cms_info.id = cms_info_model.add_entity(cms_info)
        else:
            cms_info_model.update_entity(cms_info,exclude_field_list="place_id,app_id,act_id,create_date")
        result = {}
        result["is_add"] = is_add
        result["new"] = cms_info
        result["old"] = old_cms_info
        invoke_result_data.data = result
        self._delete_cms_info_dependency_key(place_id)
        return invoke_result_data
    
    def get_cms_info_list(self, place_id, page_size, page_index, order_by="id desc",field="*", app_id="", act_id=0, is_cache=True):
        """
        :description: 位置信息列表
        :param place_id：位置标识
        :param page_size：页大小
        :param page_index：页索引
        :param order_by：排序
        :param field：查询字段
        :param app_id：应用标识
        :param act_id：活动标识
        :param is_cache：是否缓存
        :return:
        :last_editors: HuangJianYi
        """
        page_info = PageInfo(page_index, page_size, 0, [])
        if not place_id:
            return page_info
        condition = "place_id=%s and is_release=1"
        params = [place_id]
        if act_id:
            condition+=" and act_id=%s"
            params.append(act_id)
        if app_id:
            condition+=" and app_id=%s"
            params.append(app_id)
        cms_info_model = CmsInfoModel(context=self.context)
        if is_cache == True:
            page_list, total = cms_info_model.get_cache_dict_page_list(field=field, page_index=page_index, page_size=page_size, where=condition, group_by="", order_by=order_by,params=params,dependency_key=f"cms_info_list:placeid_{place_id}",cache_expire=600)
        else:
            page_list, total = cms_info_model.get_dict_page_list(field=field, page_index=page_index, page_size=page_size, where=condition, group_by="", order_by=order_by,params=params)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info
        