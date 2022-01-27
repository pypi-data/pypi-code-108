# python3
# -*- encoding: utf-8 -*-
"""
@Author:
    JoMar Wu (sos901012@gmail.com)
@Create Time:
    2019-08-28 18:06:55
@License:
    Copyright © 2019 Shenzhen Yuejiang Co., Ltd.
@Desc:
    None
"""

from .MessageCenter import MessageCenter
from . import MessageCenterError

message_center = MessageCenter()

__all__ = ("message_center", "MessageCenterError")
