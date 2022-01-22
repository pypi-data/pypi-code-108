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
from . import extractTextPlaceholders
from .step_tuple import StepTupleTypeEnum
from .. import NotZeroLenStr
from ... import ParameterTuple
from ... import StepTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField


SSH_STEP_INTERPRETERS = {}


class StepSshInterpreter:
    def __init__(self, _id, name, command, head, tail, uiAceMode):
        self.id, self.name, self.command = _id, name, command
        self.head, self.tail = head, tail
        self.uiAceMode = uiAceMode
        SSH_STEP_INTERPRETERS[self.id] = self


stepSshIntBash = StepSshInterpreter(
    1, "bash", "bash -l", "set -o nounset; set -o errexit;", "", "sh"
)

stepSshIntPython = StepSshInterpreter(
    2, "python", "python -u", "", "", "python"
)

stepSshIntPerl = StepSshInterpreter(3, "perl", "perl", "", "exit 0;", "perl")


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Execute Linux Script")
@addTupleType
class StepSshTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.SSH.value

    script: NotZeroLenStr = TupleField()
    interpreter: int = TupleField(defaultValue=stepSshIntBash.id)
    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()
    successExitCode: int = TupleField(defaultValue=0)

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred]

    def scriptReferences(self) -> list[str]:
        return extractTextPlaceholders(self.script)
