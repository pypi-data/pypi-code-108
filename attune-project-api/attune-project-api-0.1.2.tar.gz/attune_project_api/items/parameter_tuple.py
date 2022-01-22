"""
*
 *  Copyright ServerTribe HQ Pty Ltd 2021
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  ServerTribe HQ Pty Ltd
 *
"""
import re
from typing import Any
from typing import Optional

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from . import NotZeroLenStr
from .. import ObjectStorageContext
from ..StorageTuple import ItemStorageGroupEnum
from ..StorageTuple import StorageTuple


def convertParameterNameToScriptRef(name):
    # NOTE, Duplicated client side, AttunePlaceholderMod.js,
    # $scope.textPhName = function () { ...
    return re.sub(r"[^A-Za-z0-9_]", "", name).lower()


@ObjectStorageContext.registerItemClass
@addTupleType
class ParameterTuple(StorageTuple):
    __tupleType__ = "c.s.s.b.Placeholder"
    __group__ = ItemStorageGroupEnum.Parameter

    # GENERIC_SERVER = ValueTypeEnum.GENERIC_SERVER.value
    # LIN_SERVER = ValueTypeEnum.LIN_SERVER.value
    # WIN_SERVER = ValueTypeEnum.WIN_SERVER.value
    # SERVER_LIST = ValueTypeEnum.SERVER_LIST.value
    # GENERIC_CRED = ValueTypeEnum.GENERIC_CRED.value
    # WIN_OS_CRED = ValueTypeEnum.WIN_OS_CRED.value
    # LIN_OS_CRED = ValueTypeEnum.LIN_OS_CRED.value
    # SQL_CRED = ValueTypeEnum.SQL_CRED.value
    # IP4_SUBNET = ValueTypeEnum.IP4_SUBNET.value
    # TEXT = ValueTypeEnum.TEXT.value

    # Temporary to get it working with Attune
    GENERIC_SERVER = "c.s.s.b.phv.Server"
    LIN_SERVER = "c.s.s.b.phv.LinuxServer"
    WIN_SERVER = "c.s.s.b.phv.WindowsServer"
    SERVER_LIST = "c.s.s.b.phv.ServerList"
    GENERIC_CRED = "c.s.s.b.phv.OsCred"
    WIN_OS_CRED = "c.s.s.b.phv.WinOsCred"
    LIN_OS_CRED = "c.s.s.b.phv.LinOsCred"
    SQL_CRED = "c.s.s.b.phv.SqlCred"
    IP4_SUBNET = "c.s.s.b.phv.Ip4Subnet"
    TEXT = "c.s.s.b.phv.Text"

    uiData: Optional[dict] = TupleField({}, jsonExclude=True)

    key: NotZeroLenStr = TupleField()
    type: NotZeroLenStr = TupleField(defaultValue=LIN_SERVER)
    name: NotZeroLenStr = TupleField()
    showInPlan: bool = TupleField(defaultValue=True)
    comment: Optional[str] = TupleField()

    def __str__(self):
        return self.name

    __repr__ = __str__

    @property
    def textName(self):
        return convertParameterNameToScriptRef(self.name)

    @property
    def variableValueMapKey(self):
        return self.name, self.type


# This must match attune-ui/src/app/parameter/input-constants.ts
ParameterTypeNames = {
    ParameterTuple.SERVER_LIST: "Node List",
    ParameterTuple.TEXT: "Text",
    ParameterTuple.GENERIC_SERVER: "Basic Node",
    ParameterTuple.GENERIC_CRED: "Basic Credential",
    ParameterTuple.WIN_SERVER: "Windows Node",
    ParameterTuple.WIN_OS_CRED: "Windows Credential",
    ParameterTuple.LIN_SERVER: "Linux/Unix Node",
    ParameterTuple.LIN_OS_CRED: "Linux/Unix Credential",
    ParameterTuple.IP4_SUBNET: "Network IPv4 Subnet",
    ParameterTuple.SQL_CRED: "Oracle SQL Credential",
}
niceParameterNames = ParameterTypeNames
niceValueNames = ParameterTypeNames
