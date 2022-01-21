# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-04-16 14:38:22
@LastEditTime: 2022-01-06 10:35:33
@LastEditors: HuangJianYi
:Description: 基础路由   业务方可以直接使用语句 handlers.extend(seven_cloudapp_frame.route.seven_cloudapp_frame_route()) 引入
"""
# 框架引用
from seven_framework.web_tornado.monitor import MonitorHandler
from seven_cloudapp_frame.handlers.core import *
from seven_cloudapp_frame.handlers.server import *
from seven_cloudapp_frame.handlers.client import *


def seven_cloudapp_frame_route():
    return [
        (r"/monitor", MonitorHandler),
        (r"/", IndexHandler),
        #客户端
        (r"/client/address_list", address.AddressInfoListHandler),  #收货地址列表
        (r"/client/login", user.LoginHandler),  #小程序登录
        (r"/client/update_user_info", user.UpdateUserInfoHandler),  #更新用户信息如昵称、头像等
        (r"/client/check_is_member", user.CheckIsMemberHandler),  #校验是否是店铺会员
        (r"/client/apply_black_unbind", user.ApplyBlackUnbindHandler),  #申请黑名单解封
        (r"/client/get_unbind_apply", user.GetUnbindApplyHandler),  #获取黑名单解封申请记录
        (r"/client/user_asset_list", user.UserAssetListHandler),  #用户资产列表
        (r"/client/asset_log_list", user.AssetLogListHandler),  #用户资产流水列表
        (r"/client/get_join_member_url", user.GetJoinMemberUrlHandler),  #加入会员地址
        (r"/client/get_coupon_prize", user.GetCouponPrizeHandler),  #领取淘宝优惠券
        (r"/client/user_address_list", user.UserAddressListHandler),  #收货地址列表
        (r"/client/save_user_address", user.SaveUserAddressHandler),  #保存收货地址
        (r"/client/theme_info", theme.ThemeInfoHandler),  #主题信息
        (r"/client/save_theme", theme.SaveThemeHandler),  #保存主题信息，由前端通过工具进行保存
        (r"/client/save_skin", theme.SaveSkinHandler),  #保存皮肤信息，由前端通过工具进行保存
        (r"/client/theme_info_list", theme.ThemeInfoListHandler),  #主题列表
        (r"/client/skin_info_list", theme.SkinInfoListHandler),  #皮肤列表
        (r"/client/ip_info_list", ip.IpInfoListHandler),  #ip信息列表
        (r"/client/act_info", act.ActInfoHandler),  #活动信息
        (r"/client/act_prize_list", act.ActPrizeListHandler),  #活动奖品列表
        (r"/client/cms_info_list", act.CmsInfoListHandler),  #位置信息列表
        (r"/client/app_expire", app.AppExpireHandler),  #小程序过期时间
        (r"/client/add_wechat_subscribe", app.AddWechatSubscribeHandler),  #添加微信订阅次数
        (r"/client/sku_info", goods.SkuInfoHandler),  #sku信息
        (r"/client/goods_list", goods.GoodsListHandler),  #商品列表
        (r"/client/horseracelamp_list", order.HorseracelampListHandler),  #中奖记录跑马灯列表
        (r"/client/prize_order_list", order.PrizeOrderListHandler),  #用户订单列表
        (r"/client/create_prize_order", order.SelectPrizeOrderHandler),  #选择中奖记录进行下单
        (r"/client/submit_sku", order.SubmitSkuHandler),  #中奖记录选择sku
        (r"/client/prize_roster_list", order.PrizeRosterListHandler),  #中奖记录列表
        (r"/client/sync_pay_order", order.SyncPayOrderHandler),  #同步淘宝支付订单给用户加资产
        (r"/client/task_info_list", task.TaskInfoListHandler),  #任务列表
        (r"/client/receive_reward", task.ReceiveRewardHandler),  #统一领取任务奖励
        (r"/client/free_gift", task.FreeGiftHandler),  #免费领取、新人有礼等任务
        (r"/client/one_sign", task.OneSignHandler),  #单次签到任务
        (r"/client/weekly_sign", task.WeeklySignHandler),  #每周签到任务
        (r"/client/cumulative_sign", task.CumulativeSignHandler),  #累计签到任务
        (r"/client/invite_new_user", task.InviteNewUserHandler),  #邀请新用户任务
        (r"/client/invite_join_member", task.InviteJoinMemberHandler),  #邀请加入会员任务
        (r"/client/browse_site", task.BrowseSiteHandler),  #处理浏览网址相关任务 如：浏览店铺、浏览直播间、浏览会场/专题
        (r"/client/collect_goods", task.CollectGoodsHandler),  #收藏商品任务
        (r"/client/browse_goods", task.BrowseGoodsHandler),  #浏览商品任务
        (r"/client/favor_store", task.FavorStoreHandler),  #关注店铺任务
        (r"/client/join_member", task.JoinMemberHandler),  #加入会员任务
        (r"/client/task_share", task.ShareHandler),  #分享奖励任务
        (r"/client/share_report", stat.ShareReportHandler),  #分享统计上报
        (r"/client/invite_report", stat.InviteReportHandler),  #邀请进入统计上报
        (r"/client/wvoucher_order", pay.WechatVoucherOrderHandler),  #创建微信预订单
        (r"/client/wpay_notify", pay.WechatPayNotifyHandler),  #微信支付异步通知
        (r"/client/wrefund_notify", pay.WechatRefundNotifyHandler),  #微信退款异步通知
        (r"/client/tvoucher_order", pay.TiktokVoucherOrderHandler),  #创建抖音预订单
        (r"/client/tpay_notify", pay.TiktokPayNotifyHandler),  #抖音支付异步通知
        (r"/client/trefund_notify", pay.TiktokRefundNotifyHandler),  #抖音退款异步通知

        #后台和千牛端
        (r"/server/saas_custom", base_s.SaasCustomHandler),  #saas定制化信息获取
        (r"/server/login", user_s.LoginHandler),  #千牛端登录
        (r"/server/left_navigation", base_s.LeftNavigationHandler),  #左侧导航
        (r"/server/friend_link_list", base_s.FriendLinkListHandler),  #获取友情链接产品互推列表
        (r"/server/send_sms", base_s.SendSmsHandler),  #发短信
        (r"/server/cms_info_list", base_s.CmsInfoListHandler),  #位置信息列表
        (r"/server/save_cms_info", base_s.SaveCmsInfoHandler),  #保存位置信息
        (r"/server/get_product_price", base_s.GetProductPriceHandler),  #获取产品价格信息
        (r"/server/app_info", app_s.AppInfoHandler),  #应用信息
        (r"/server/get_app_id", app_s.GetAppIDHandler),  #根据店铺名称返回应用标识 用于GM工具
        (r"/server/instantiate", app_s.InstantiateAppHandler),  #实例化小程序
        (r"/server/version_upgrade", app_s.VersionUpgradeHandler),  #小程序端版本升级
        (r"/server/update_telephone", app_s.UpdateTelephoneHandler),  #更新手机号
        (r"/server/get_short_url", app_s.GetShortUrlHandler),  #淘宝短链接
        (r"/server/act_type_list", act_s.ActTypeListHandler),  #活动类型列表
        (r"/server/next_progress", act_s.NextProgressHandler),  #活动下一步操作
        (r"/server/add_act_info", act_s.AddActInfoHandler),  #添加活动
        (r"/server/update_act_info", act_s.UpdateActInfoHandler),  #修改活动
        (r"/server/act_info_list", act_s.ActInfoListHandler),  #活动列表
        (r"/server/act_info", act_s.ActInfoHandler),  #单条活动信息
        (r"/server/delete_act_info", act_s.DeleteActInfoHandler),  #删除活动（假删除）
        (r"/server/review_act_info", act_s.ReviewActInfoHandler),  #还原活动
        (r"/server/release_act_info", act_s.ReleaseActInfoHandler),  #上下架活动
        (r"/server/create_act_qrcode", act_s.CreateActQrCodeHandler),  #生成小程序二维码
        (r"/server/save_act_module", module_s.SaveActModuleHandler),  #保存活动模块信息（保存新增和修改）
        (r"/server/act_module", module_s.ActModuleHandler),  #单条活动模块信息
        (r"/server/act_module_list", module_s.ActModuleListHandler),  #活动模块列表
        (r"/server/delete_act_module", module_s.DeleteActModuleHandler),  #删除活动模块（假删除）
        (r"/server/review_act_module", module_s.ReviewActModuleHandler),  #还原活动模块
        (r"/server/release_act_module", module_s.ReleaseActModuleHandler),  #上下架活动模块
        (r"/server/save_act_prize", prize_s.SaveActPrizeHandler),  #保存活动奖品
        (r"/server/act_prize_list", prize_s.ActPrizeListHandler),  #活动奖品列表
        (r"/server/delete_act_prize", prize_s.DeleteActPrizeHandler),  #删除活动奖品（假删除）
        (r"/server/review_act_prize", prize_s.ReviewActPrizeHandler),  #还原活动奖品
        (r"/server/release_act_prize", prize_s.ReleaseActPrizeHandler),  #上下架活动奖品
        (r"/server/act_prize_export", prize_s.ActPrizeExportHandler),  #导出活动奖品列表
        (r"/server/pay_order_list", order_s.PayOrderListHandler),  #淘宝支付订单列表
        (r"/server/prize_order_list", order_s.PrizeOrderListHandler),  #奖品订单列表
        (r"/server/prize_roster_list", order_s.PrizeRosterListHandler),  #用户中奖记录列表
        (r"/server/prize_order_export", order_s.PrizeOrderExportHandler),  #导出奖品订单列表
        (r"/server/prize_roster_export", order_s.PrizeRosterExportHandler),  #导出用户中奖记录列表
        (r"/server/tao_pay_order_export", order_s.TaoPayOrderExportHandler),  #导出淘宝订单列表
        (r"/server/update_prize_order_status", order_s.UpdatePrizeOrderStatusHandler),  #更新奖品订单状态
        (r"/server/update_prize_order_seller_remark", order_s.UpdatePrizeOrderSellerRemarkHandler),  #更新奖品订单卖家备注
        (r"/server/import_prize_order", order_s.ImportPrizeOrderHandler),  #导入发货订单
        (r"/server/stat_report_list", report_s.StatReportListHandler),  #报表数据列表(表格)
        (r"/server/trend_report_list", report_s.TrendReportListHandler),  #报表数据列表(趋势图)
        (r"/server/user_info_list", user_s.UserInfoListHandler),  #用户信息列表
        (r"/server/update_user_status", user_s.UpdateUserStatusHandler),  #更新用户状态（0正常1黑名单）
        (r"/server/update_user_status_by_black", user_s.UpdateUserStatusByBlackHandler),  #更新用户状态(黑名单管理模式)
        (r"/server/audit_user_black", user_s.AuditUserBlackHandler),  #审核黑名单状态
        (r"/server/update_audit_remark", user_s.UpdateAuditRemarkHandler),  #修改审核备注
        (r"/server/user_black_list", user_s.UserBlackListHandler),  #黑名单列表
        (r"/server/update_user_asset", user_s.UpdateUserAssetHandler),  #更新用户资产值
        (r"/server/batch_update_user_asset", user_s.BatchUpdateUserAssetHandler),  #批量更新用户资产值
        (r"/server/user_asset_list", user_s.UserAssetListHandler),  #用户资产列表
        (r"/server/asset_log_list", user_s.AssetLogListHandler),  #资产流水列表
        (r"/server/init_launch_goods", launch_s.ResetLaunchGoodsHandler),  #重置商品投放 删除已投放的记录并将活动投放状态改为未投放
        (r"/server/init_launch_goods", launch_s.InitLaunchGoodsHandler),  #初始化投放商品
        (r"/server/async_launch_goods", launch_s.AsyncLaunchGoodsHandler),  #同步投放商品（小程序投放-商品绑定/解绑）
        (r"/server/launch_goods_list", launch_s.LaunchGoodsListHandler),  #投放商品列表
        (r"/server/update_launch_goods_status", launch_s.UpdateLaunchGoodsStatusHandler),  #更新投放商品的状态
        (r"/server/init_launch_goods_callback", launch_s.InitLaunchGoodsCallBackHandler),  #初始化投放商品回调接口
        (r"/server/update_theme", theme_s.UpdateThemeHandler),  #更新主题
        (r"/server/theme_info_list", theme_s.ThemeInfoListHandler),  #主题信息列表
        (r"/server/skin_info_list", theme_s.SkinInfoListHandler),  #皮肤信息列表
        (r"/server/save_ip_info", ip_s.SaveIpInfoHandler),  #保存ip信息
        (r"/server/delete_ip_info", ip_s.DeleteIpInfoHandler),  #删除ip信息
        (r"/server/ip_info_list", ip_s.IpInfoListHandler),  #ip信息列表
        (r"/server/release_ip_info", ip_s.ReleaseIpInfoHandler),  #上下架ip信息
        (r"/server/save_price_gear", price_s.SavePriceGearHandler),  #保存价格档位信息
        (r"/server/price_gear_list", price_s.PriceGearListHandler),  #价格档位列表
        (r"/server/delete_price_gear", price_s.DeletePriceGearHandler),  #删除价格档位（假删除）
        (r"/server/review_price_gear", price_s.ReviewPriceGearHandler),  #还原价格档位
        (r"/server/check_price_gear", price_s.CheckPriceGearHandler),  #校验价格档位
        (r"/server/inventory_goods_list", goods_s.InventoryGoodsListHandler),  #仓库中的商品列表
        (r"/server/goods_list", goods_s.GoodsListHandler),  #在售中的商品列表
        (r"/server/goods_list_by_goodsids", goods_s.GoodsListByGoodsIDHandler),  #根据商品ID返回在售中商品列表
        (r"/server/goods_info", goods_s.GoodsInfoHandler),  #商品信息
        (r"/server/benefit_detail", goods_s.BenefitDetailHandler),  #获取优惠券详情信息
        (r"/server/task_info_list", task_s.TaskInfoListHandler),  #任务信息列表
        (r"/server/save_task_info", task_s.SaveTaskInfoHandler),  #保存任务信息
        (r"/server/special_goods_list", goods_s.SpecialGoodsListHandler),  #专属下单商品列表
        (r"/server/bind_special_goods", goods_s.BindSpecialGoodsHandler),  #专属下单商品绑定
    ]