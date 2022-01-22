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
from typing import Optional

from attune_project_api.items import NotZeroLenStr
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from . import addStepDeclarative
from . import extractTextPlaceholders
from .step_tuple import StepTuple
from .step_tuple import StepTupleTypeEnum
from ... import ParameterTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Execute Linux Oracle SQL")
@addTupleType
class StepSqlOracleTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.SQL_ORACLE.value

    sql: NotZeroLenStr = TupleField()
    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()
    sqlCredKey: NotZeroLenStr = TupleField()
    plsql: bool = TupleField(defaultValue=False)
    commit: bool = TupleField(defaultValue=True)
    acceptOraErrors: Optional[str] = TupleField()

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )
    sqlCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="sqlCredKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred, self.sqlCred]

    def scriptReferences(self) -> list[str]:
        return extractTextPlaceholders(self.sql)
