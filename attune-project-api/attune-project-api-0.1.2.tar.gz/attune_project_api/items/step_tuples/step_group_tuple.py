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

from . import addStepDeclarative
from .step_tuple import StepTuple
from .step_tuple import StepTupleTypeEnum
from .. import NotZeroLenStr
from ... import ParameterTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField
from ...StorageTuple import StorageMemberTuple


ORDER_GAP = 100
MIN_ORDER_GAP = 10


@addTupleType
class StepGroupSubStepLinkTuple(StorageMemberTuple):
    __tupleType__ = "com.servertribe.attune.tuples.StepGroupSubStepLinkTuple"

    order: int = TupleField(defaultValue=0)
    stepKey: NotZeroLenStr = TupleField()

    step = RelationField(
        ForeignClass=StepTuple,
        referenceKeyFieldName="stepKey",
        cascadeOnUpdate=False,
    )

    uiData: Optional[dict] = TupleField(defaultValue={}, jsonExclude=True)


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Group Step")
@addTupleType
class StepGroupTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.GROUP.value

    concurrency: int = TupleField(defaultValue=1)
    isBlueprint: bool = TupleField(defaultValue=False)
    links: list[StepGroupSubStepLinkTuple] = TupleField(defaultValue=[])
    childSteps: list[StepTuple] = RelationField(
        ForeignClass=StepTuple,
        referenceKeyFieldName="links",
        isList=True,
        cascadeOnDelete=True,
        memberReferenceKeyFieldName="stepKey",
    )

    @classmethod
    def niceName(cls) -> str:
        return "Group StepTuple"

    def stepForLink(
        self, link: StepGroupSubStepLinkTuple
    ) -> Optional[StepTuple]:
        return self.storageContext.getItem(self.storageGroup, link.stepKey)

    def getLinkByOrder(self, order: int) -> StepGroupSubStepLinkTuple:
        for link in self.links:
            if link.order == order:
                return link

        raise Exception(
            "Can not find link with parent %s order %s", self.key, order
        )

    def parameters(self) -> list["ParameterTuple"]:
        return []

    def scriptReferences(self) -> list[str]:
        return []

    def removeStepLink(self, index):
        self.links.pop(index)

    def insertStepLink(self, index, stepKey):
        link = StepGroupSubStepLinkTuple(order=0, stepKey=stepKey)
        self.links.insert(index, link)

        lastLinkOrder = self.links[0].order
        for link in self.links[1:]:
            if link.order <= lastLinkOrder + MIN_ORDER_GAP:
                link.order = int(lastLinkOrder + (ORDER_GAP // 2))
            lastLinkOrder = link.order
