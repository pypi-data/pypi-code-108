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

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from attune_project_api.items import NotZeroLenStr
from . import addStepDeclarative
from . import extractTextPlaceholders
from .step_tuple import StepTupleTypeEnum
from ... import ParameterTuple
from ... import StepTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField

STEP_WIN_CMD_INTERPRETERS = {}


class StepWinCmdInterpreter:
    def __init__(self, _id, name):
        self.id, self.name = _id, name
        STEP_WIN_CMD_INTERPRETERS[self.id] = self


# ID=1, hard coded in 8ba86d3c39b_added_support_to_for_shell_interpreters.py
# due to upgrade import issues
winCmdIntBatchScript = StepWinCmdInterpreter(1, "Batch Script")
winCmdIntPowershellScript = StepWinCmdInterpreter(2, "Powershell Script")
winCmdIntCustom = StepWinCmdInterpreter(3, "Custom")


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Execute Windows Script")
@addTupleType
class StepWinRmTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.WINRM.value

    script: NotZeroLenStr = TupleField()
    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()
    interpreter: int = TupleField(defaultValue=winCmdIntPowershellScript.id)
    interpreterCommand: Optional[str] = TupleField()
    interpreterScriptExt: Optional[str] = TupleField()
    interpreterScriptSyntax: Optional[str] = TupleField()
    successExitCode: int = TupleField(defaultValue=0)
    timeout: Optional[int] = TupleField()

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )

    @property
    def interpreterWinCmd(self):
        return STEP_WIN_CMD_INTERPRETERS[self.interpreter]

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred]

    def scriptReferences(self) -> list[str]:
        textPh = extractTextPlaceholders(self.script)
        if self.interpreterCommand:
            textPh += extractTextPlaceholders(self.interpreterCommand)
        return textPh
