from abc import ABCMeta
from enum import Enum
from typing import Optional

from attune_project_api import ObjectStorageContext
from attune_project_api import StorageTuple
from attune_project_api.StorageTuple import ItemStorageGroupEnum
from attune_project_api.items import NotZeroLenStr
from vortex.Tuple import PolymorphicTupleTypeFieldArg
from vortex.Tuple import TupleField


class StepTupleTypeEnum(Enum):
    GROUP = "com.servertribe.attune.tuples.StepGroupTuple"
    SQL_ORACLE = "com.servertribe.attune.tuples.StepSqlOracleTuple"
    SSH = "com.servertribe.attune.tuples.StepSshTuple"
    SSH_PROMPTED = "com.servertribe.attune.tuples.StepSshPromptedTuple"
    WINRM = "com.servertribe.attune.tuples.StepWinRmTuple"

    PUSH_DESIGN_FILE = "com.servertribe.attune.tuples.StepPushDesignFileTuple"
    PUSH_DESIGN_FILE_COMPILED = (
        "com.servertribe.attune.tuples.StepPushDesignFileCompiledTuple"
    )

    BOOTSTRAP_LINUX = "com.servertribe.attune.tuples.StepBootstrapLinuxTuple"

    TCP_PING = "com.servertribe.attune.tuples.StepTcpPingTuple"

    PROJECT_LINK = "com.servertribe.attune.tuples.StepProjectLinkTuple"


@ObjectStorageContext.registerItemClass
class StepTuple(StorageTuple, metaclass=ABCMeta):
    __tupleArgs__ = (PolymorphicTupleTypeFieldArg("type"),)
    __group__ = ItemStorageGroupEnum.Step

    uiData: Optional[dict] = TupleField(defaultValue={}, jsonExclude=True)

    name: NotZeroLenStr = TupleField()
    comment: Optional[str] = TupleField(defaultValue="")
    enabled: bool = TupleField(defaultValue=True)
    type: NotZeroLenStr = TupleField()

    def parameters(self) -> list["ParameterTuple"]:
        """Parameters

        return a list of parameters linked to from this step

        """
        # This is an abstract kind of method, but we can't have an abstract
        # class because StepTuple() is constructed to send to the UI
        raise NotImplementedError()

    def scriptReferences(self) -> list[str]:
        """Script References

        return a list of script references within this step.

        """
        # This is an abstract kind of method, but we can't have an abstract
        # class because StepTuple() is constructed to send to the UI
        raise NotImplementedError()
