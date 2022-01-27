# python3
# -*- encoding: utf-8 -*-
"""
@Author:
    JoMar Wu (sos901012@gmail.com)
@Create Time:
    2019-08-28 18:07:25
@License:
    Copyright © 2019 Shenzhen Yuejiang Co., Ltd.
@Desc:
    None
"""
from typing import List, Any


class MessageCenterError(Exception):
    pass


class IsNotMessageHandler(MessageCenterError):
    def __init__(self, obj: object):
        super().__init__("%s is not MessageHandler." % str(obj))


class MustRegisterOrphan(MessageCenterError):
    def __init__(self):
        super().__init__("Must register orphan.")


class CannotFoundModule(MessageCenterError):
    def __init__(self, name: object):
        super().__init__("%s can not found." % str(name))


class CannotFoundFunc(MessageCenterError):
    def __init__(self, name: object):
        super().__init__("%s can not found." % str(name))


class InvalidMethodFormat(MessageCenterError):
    def __init__(self, method: object):
        super().__init__("%s" % str(method))


class CanNotFoundCallback(MessageCenterError):
    def __init__(self, callback_id: object):
        super().__init__("callback(%s) can not found." % str(callback_id))


class InvaildCallback(MessageCenterError):
    def __init__(self, obj: object):
        super().__init__("objest(%s) is not callable." % str(obj))


class InvaildParams(MessageCenterError):
    def __init__(self, args: List[Any]):
        super().__init__("%s is invaild params." % str(args))


class CannotFoundMethod(MessageCenterError):
    pass