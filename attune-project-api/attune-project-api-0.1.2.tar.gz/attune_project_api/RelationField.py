from typing import Optional

from attune_project_api import StorageTuple
from attune_project_api.StorageTuple import StorageMemberTuple


class RelationField:
    def __init__(
        self,
        ForeignClass: type[StorageTuple],
        referenceKeyFieldName: str,
        cascadeOnDelete: bool = False,
        isList: bool = False,
        memberReferenceKeyFieldName: Optional[str] = None,
        cascadeOnUpdate=True,
    ):
        """Relation

        :param: memberReferenceKeyFieldName
         The dot reference field name creates a relation out of child objects
         for example

         class OtherTuple(StorageTuple):
             key = TupleField()

         class DotTuple(StorageMemberTuple):
             otherKey = TupleField()

             other = RelationField(
                tupleType=OtherTuple.tupleType(),
                referenceKeyFieldName="otherKey",
                cascadeOnDelete=True,
            )

         class Thing2Tuple(StorageTuple):
             key = TupleField()

             dotLinks:list[DotTuple] = TupleField()

             otherThings = Relation(
                tupleType=DotTuple.tupleType(),
                referenceKeyFieldName="dotLinks",
                isList=True,
                memberReferenceKeyFieldName="otherKey
            )



        """
        self.ForeignClass = ForeignClass
        self.referenceKeyFieldName = referenceKeyFieldName
        self.cascadeOnDelete = cascadeOnDelete
        self.isList = isList
        self.memberReferenceKeyFieldName = memberReferenceKeyFieldName
        self.cascadeOnUpdate = cascadeOnUpdate
        self.OriginClass = None

        if self.isList and not self.cascadeOnDelete:
            raise Exception("Relations expect cascade on delete for lists")

    def _setOriginClass(self, OriginClass: type[StorageTuple]) -> None:
        self.OriginClass = OriginClass

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return

        isMemberTuple = isinstance(instance, StorageMemberTuple)
        if isMemberTuple:
            context = instance.storageParent.storageContext
        else:
            context = instance.storageContext

        if not context:
            raise ValueError(f"ObjectStorageContext not bound")

        if getattr(instance, self.referenceKeyFieldName) is None:
            return None

        # It doesn't matter if we're a list or not, the member tuple level
        # must be a 1 to 1 relationship.
        if isMemberTuple:
            # From the member tuples perspective,
            # use referenceKeyFieldName, not memberReferenceKeyFieldName
            return context.getItem(
                self.ForeignClass.storageGroup,
                getattr(instance, self.referenceKeyFieldName),
            )

        # instance is the main StorageTuple, and this is not a list
        # handle this simple case and return
        if not self.isList:
            if self.memberReferenceKeyFieldName:
                raise NotImplementedError(
                    "Member Tuples that are not a list are not yet implemented"
                )
            return context.getItem(
                self.ForeignClass.storageGroup,
                getattr(instance, self.referenceKeyFieldName),
            )

        # We have a list, get it from the instance
        values = getattr(instance, self.referenceKeyFieldName)
        if not values:
            return None

        # If we have this set, then we have a list of tuples, each with a
        # variable that points to a key, convert that to a simple list
        if self.memberReferenceKeyFieldName:
            # Create a set of keys from our member tuples variable
            values = [
                getattr(memberTuple, self.memberReferenceKeyFieldName)
                for memberTuple in values
            ]

        # Using the set above, return a list that matches our list,
        # Doing it this way will maintain the list length, order and any
        # duplicates, and raise any exceptions for missing keys
        return [
            context.getItem(self.ForeignClass.storageGroup, key)
            for key in values
        ]
