#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : wechat
# @Time         : 2021/6/7 11:17 上午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 日报

from meutils.pipe import *
from meutils.notice.wechat import Bot

bot = Bot("a242fcec-8156-4963-96be-a462b0bb8e76") # 算法群
json = {
    "msgtype": "text",
    "text": {
        "content": "每日站会：可文字同步状态。",
        "mentioned_mobile_list": ["@all"]
    }
}
logger.info("站会通知")

bot.send(json)
