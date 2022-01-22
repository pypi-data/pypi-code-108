from attune_project_api import ParameterTuple
from attune_project_api.RelationField import RelationField
from attune_project_api._contexts import GitObjectStorageContext
from attune_project_api.items import NotZeroLenStr
from attune_project_api.items.file_archive_tuples.file_archive_tuple import (
    FileArchiveTuple,
)
from attune_project_api.items.step_tuples import addStepDeclarative
from attune_project_api.items.step_tuples import extractTextPlaceholders
from attune_project_api.items.step_tuples.step_tuple import StepTuple
from attune_project_api.items.step_tuples.step_tuple import StepTupleTypeEnum
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@GitObjectStorageContext.registerItemClass
@addStepDeclarative("Push Files")
@addTupleType
class StepPushDesignFileTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.PUSH_DESIGN_FILE.value

    serverKey: NotZeroLenStr = TupleField()
    osCredKey: NotZeroLenStr = TupleField()
    deployPath: NotZeroLenStr = TupleField()
    archiveKey: NotZeroLenStr = TupleField()
    unpack: bool = TupleField(False)

    server: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="serverKey",
    )
    osCred: ParameterTuple = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="osCredKey",
    )
    archive: FileArchiveTuple = RelationField(
        ForeignClass=FileArchiveTuple,
        referenceKeyFieldName="archiveKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [self.server, self.osCred]

    def scriptReferences(self) -> list[str]:
        return extractTextPlaceholders(self.deployPath)
