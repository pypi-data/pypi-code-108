# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
from enum import Enum
from typing import Generic
from typing import TypeVar

from pydantic import ConstrainedInt
from pydantic import ConstrainedList
from pydantic import ConstrainedStr


class PositiveEqualInt(ConstrainedInt):
    ge = 0


class NotEmptyStr(ConstrainedStr):
    min_length = 1


T = TypeVar("T")


class NotEmptyList(ConstrainedList, Generic[T]):
    __args__ = [T]  # type: ignore

    min_items = 1
    item_type = T  # type: ignore


class RoleEnum(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"
    AD = "ad"
    FILE_SERVER = "file_server"
    INTERNET = "internet"
    SQUID = "squid"
    MAIL_SERVER = "mail_server"

    @staticmethod
    def from_str(label):
        if label == "client":
            return RoleEnum.CLIENT
        if label == "admin":
            return RoleEnum.ADMIN
        if label == "ad":
            return RoleEnum.AD
        if label == "file_server":
            return RoleEnum.FILE_SERVER
        if label == "internet":
            return RoleEnum.INTERNET
        if label == "squid":
            return RoleEnum.SQUID
        if label == "mail_server":
            return RoleEnum.MAIL_SERVER
        raise NotImplementedError
