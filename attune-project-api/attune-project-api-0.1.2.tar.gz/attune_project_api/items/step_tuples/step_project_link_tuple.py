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
from ... import ParameterTuple
from ... import StepTuple
from ...ObjectStorageContext import ObjectStorageContext


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Project Link")
@addTupleType
class StepProjectLinkTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.PROJECT_LINK.value

    projectKey: str = TupleField()
    blueprintKey: str = TupleField()
    pullUrl: str = TupleField()

    def parameters(self) -> list["ParameterTuple"]:
        return []

    def scriptReferences(self) -> list[str]:
        return []
