from collections import namedtuple

from attune_project_api.RelationField import RelationField

BackReference = namedtuple(
    "BackReference",
    [
        "origin",
        "referenceKeyFieldName",
        "cascade",
        "isList",
        "memberReferenceKeyFieldName",
    ],
)

Cascade = namedtuple(
    "Cascade", ["attribName", "cascadedOn", "memberReferenceKeyFieldName"]
)


class RelationReferences:
    def __init__(self):
        self.back_references: list[BackReference] = []
        self.cascades: list[Cascade] = []


class RelationGraph:
    def __init__(self):
        self.__stagedRelations: list[RelationField] = []

    def getRelationsToStorageTupleKey(self, Class_) -> list[RelationField]:
        return list(
            set(
                filter(
                    lambda r: issubclass(Class_, r.ForeignClass),
                    self.__stagedRelations,
                )
            )
        )

    def add(self, relation: RelationField):
        if self.__stagedRelations is None:
            raise Exception("The RelationGraph has already been compiled")
        self.__stagedRelations.append(relation)
