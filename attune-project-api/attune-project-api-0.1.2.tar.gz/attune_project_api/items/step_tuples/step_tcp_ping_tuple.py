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

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from . import addStepDeclarative
from .step_tuple import StepTupleTypeEnum
from .. import NotZeroLenStr
from ... import ParameterTuple
from ... import StepTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Tcp Ping")
@addTupleType
class StepTcpPingTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.TCP_PING.value

    serverKey: NotZeroLenStr = TupleField()
    tcpPort: int = TupleField()
    preWait: int = TupleField(defaultValue=0)
    minDowntime: int = TupleField(defaultValue=0)
    postWait: int = TupleField(defaultValue=0)

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server]

    def scriptReferences(self) -> list[str]:
        return []
