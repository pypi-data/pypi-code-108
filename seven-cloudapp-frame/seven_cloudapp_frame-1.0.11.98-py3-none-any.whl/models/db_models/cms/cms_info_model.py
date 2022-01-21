# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-11-25 18:38:13
@LastEditTime: 2021-11-26 10:59:17
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class CmsInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(CmsInfoModel, self).__init__(CmsInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class CmsInfo:

    def __init__(self):
        super(CmsInfo, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.place_id = 0  # 信息位标识
        self.info_title = ""  # 信息标题
        self.simple_title = ""  # 信息短标题
        self.simple_title_url = ""  # 短标题链接
        self.info_type = 0  # 信息类型
        self.info_summary = ""  # 信息摘要
        self.info_tag = ""  # 信息标签[文章内容特性][砍人事件]
        self.info_mark = ""  # 信息标记[首发,推荐,独家，热门]
        self.target_url = ""  # 跳转地址
        self.min_pic = ""  # 信息小图
        self.mid_pic = ""  # 信息中图
        self.max_pic = ""  # 信息大图
        self.info_data = ""  # 信息内容
        self.pic_collect_json = ""  # 图集json
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.i1 = 0  # i1
        self.i2 = 0  # i2
        self.i3 = 0  # i3
        self.i4 = 0  # i4
        self.s1 = ""  # s1
        self.s2 = ""  # s2
        self.s3 = ""  # s3
        self.s4 = ""  # s4

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'place_id', 'info_title', 'simple_title', 'simple_title_url', 'info_type', 'info_summary', 'info_tag', 'info_mark', 'target_url', 'min_pic', 'mid_pic', 'max_pic', 'info_data', 'pic_collect_json', 'sort_index', 'is_release', 'release_date', 'create_date', 'modify_date', 'i1', 'i2', 'i3', 'i4', 's1', 's2', 's3','s4']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "cms_info_tb"
