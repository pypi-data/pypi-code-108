# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-06-02 14:32:40
@LastEditTime: 2021-12-15 11:46:42
@LastEditors: HuangJianYi
:description: 枚举类
"""

from enum import Enum

class OperationType(Enum):
    """
    :description: 用户操作日志类型
    """
    add = 1 #添加
    update = 2 #更新
    delete = 3 #删除
    review = 4 #还原

class TaskType(Enum):
    """
    docstring：任务类型 业务的自定义任务类型从201起
    """
    # 掌柜有礼、免费领取、新人有礼，格式：{"reward_value":0,"asset_object_id":""}  字段说明：reward_value:奖励值 asset_object_id:资产对象标识
    free_gift = 1
    # 单次签到，格式：{"reward_value":0,"asset_object_id":""}  字段说明：reward_value:奖励值 asset_object_id:资产对象标识
    one_sign = 2
    # 每周签到，格式：{"day_list":{"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0},"asset_object_id":""}  字段说明：day_list:每天奖励配置列表 asset_object_id:资产对象标识
    weekly_sign = 3
    # 邀请新用户，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    invite_new_user = 4
    # 邀请入会，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""}  字段说明：reward_value:奖励值 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    invite_join_member = 5
    # 关注店铺，格式：{"reward_value":0,"once_favor_reward":0,"asset_object_id":""} 字段说明：reward_value:奖励值 once_favor_reward:已关注是否奖励1是0否 asset_object_id:资产对象标识
    favor_store = 6
    # 加入店铺会员，格式：{"reward_value":0,"once_member_reward":0,"asset_object_id":""} 字段说明：reward_value:奖励值 once_member_reward:已入会是否奖励1是0否 asset_object_id:资产对象标识
    join_member = 7
    # 收藏商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 asset_object_id:资产对象标识 limit_num:完成限制数 goods_ids:商品ID串 goods_list:商品列表
    collect_goods = 8
    # 浏览商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 asset_object_id:资产对象标识 limit_num:完成限制数 goods_ids:商品ID串 goods_list:商品列表
    browse_goods = 9
    # 浏览店铺，格式：[{"id":"","reward_value":0,"link_url":"","satisfy_num":1,"limit_num":1,"asset_object_id":""}] 字段说明：id:子任务类型,必填 reward_value:奖励值 satisfy_num:满足数  link_url:链接地址 asset_object_id:资产对象标识 limit_num:完成限制数
    browse_store = 10
    # 浏览直播间，格式：[{"id":"","reward_value":0,"link_url":"","satisfy_num":1,"limit_num":1,"asset_object_id":""}]  字段说明：id:子任务类型,必填 reward_value:奖励值 satisfy_num:满足数  link_url:链接地址 asset_object_id:资产对象标识 limit_num:完成限制数
    browse_live_room = 11
    # 浏览会场/专题，格式：[{"id":"","reward_value":0,"link_url":"","satisfy_num":1,"limit_num":1,"asset_object_id":""}] 字段说明：id:子任务类型,必填 reward_value:奖励值 satisfy_num:满足数  link_url:链接地址 asset_object_id:资产对象标识 limit_num:完成限制数
    browse_special_topic = 12
    # 累计签到，格式：{"day_list":{"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0},"asset_object_id":"","is_loop":1} 字段说明： day_list:每天奖励配置列表 asset_object_id:资产对象标识 is_loop:是否循环1是0否
    cumulative_sign = 13
    # 分享，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    share = 14
