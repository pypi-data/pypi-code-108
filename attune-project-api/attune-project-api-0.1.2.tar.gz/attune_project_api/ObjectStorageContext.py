import inspect
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple
from pathlib import Path
from typing import Generator
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import get_args
from typing import get_type_hints

from vortex.Tuple import TUPLE_TYPES
from vortex.Tuple import Tuple

from .Exceptions import ItemNotFoundError
from .Exceptions import NonUniqueNameError
from .RelationField import RelationField
from .StorageTuple import ItemStorageGroupEnum
from .StorageTuple import StorageMemberTuple
from .StorageTuple import StorageTuple
from ._private.RelationGraph import RelationGraph
from .tuples.git_commit_tuple import GitCommitTuple


class TupleValidatorABC(ABC):
    @abstractmethod
    def validate(
        self,
        contexts: "ObjectStorageContext",
        item: Tuple,
    ) -> None:
        """Validate

        :param contexts: TODO
        :param item: TODO

        """


ContextProjectInfo = namedtuple("ContextProjectInfo", ["key", "name"])


ArchiveFileInfo = namedtuple("ArchiveFileInfo", ["path", "size"])
ArchiveFileContent = namedtuple(
    "ArchiveFileInfoContent", ["path", "data", "executable"]
)

VersionedFileInfo = namedtuple(
    "VersionedFileInfo", ["path", "size", "executable", "sha1"]
)

VersionedFileContent = namedtuple(
    "VersionedFileContent", ["path", "data", "executable", "sha1"]
)


class ObjectStorageContextFileMixin(metaclass=ABCMeta):
    @abstractmethod
    def readItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> bytes:
        """Read Item Versioned File

        Reads the file contents of a file that belongs with a version
        controlled item.

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :param path: The relative path to the file within its storage directory
        :return: The bytes contents of the file
        """
        raise NotImplementedError()

    @abstractmethod
    def writeItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path, data: bytes
    ) -> None:
        """Write Item Versioned File

        Writes the file contents of a file that belongs with a version
        controlled item.

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :param path: The relative path to the file within its storage directory
        :param data: The bytes of the file to write.
        """
        raise NotImplementedError()

    @abstractmethod
    def listItemVersionedFiles(
        self, group: ItemStorageGroupEnum, key: str
    ) -> list[VersionedFileInfo]:
        """List Item Versioned File

        Return a list of files that are versioned for this item

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :return: A list of VersionedFileInfo with paths relative to the content
            root
        """
        raise NotImplementedError()

    @abstractmethod
    def getItemVersionedFileContent(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> Optional[VersionedFileContent]:
        """Get Item Versioned File Content

        Return a the content of a file that is versioned for this item

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :param path: The relative content root path
        :return: A tuple containing some file information and the content
        """
        raise NotImplementedError()

    @abstractmethod
    def setItemVersionedFileContent(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        path: Path,
        data: bytes,
        executable: bool,
    ) -> None:
        """Set Item Versioned File Content

        Write new content for a versioned file to the storage

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :param path: The relative content root path
        :param data: The data to write to the storage
        :param executable: Should file have the executable flag set?
        """
        raise NotImplementedError()

    @abstractmethod
    def moveItemVersionedFile(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        fromPath: Path,
        toPath: Path,
    ) -> None:
        """Move Item Verseioned File

        Move an item relative to the items file content directory

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :param fromPath: The current path
        :param toPath: The new path
        """
        raise NotImplementedError()

    @abstractmethod
    def moveItemVersionedDirectory(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        fromPath: Path,
        toPath: Path,
    ) -> None:
        """Move a directory of Verseioned Files

        Move a directory files relative to the items file
        content directory.

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :param fromPath: The current path
        :param toPath: The new path
        """
        raise NotImplementedError()

    @abstractmethod
    def deleteItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> None:
        """Delete Item Verseioned File

        Delete an item relative to the items file content directory

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :param path: The path to delete
        """
        raise NotImplementedError()

    @abstractmethod
    def deleteItemVersionedDirectory(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> None:
        """Delete a directory of Verseioned Files

        Delete a directory files relative to the items file
        content directory.

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :param path: The path to delete
        """
        raise NotImplementedError()

    @abstractmethod
    def getItemLargeFilesPath(
        self, group: ItemStorageGroupEnum, key: str
    ) -> Path:
        """Get Items Large File Path

        Get a file path of where an items unversioned files can be written
        to.

        Large files are not version controlled, but they are managed

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :return: An absoloute path object to where unversioned files
            can be written
        """
        raise NotImplementedError()


class ObjectStorageContext(ObjectStorageContextFileMixin):
    _ItemParentClassByTupleType: dict[str, type[StorageTuple]] = {}

    _RelationGraph = RelationGraph()

    # TupleValidatorABC's registered with the StorageContext using
    # registerValidator
    _Validators: list[TupleValidatorABC] = []

    _BaseClassByGroup = {}

    @classmethod
    def registerItemClass(
        cls,
        ItemClass: type[StorageTuple],
    ) -> type[StorageTuple]:
        """Register Item Class

        Registers a `StorageTuple` with the `ObjectStorageContext`. `ItemClass`
        needs to have a `__group__` from `ItemStorageGroupEnum` set. Meant to be
        used as a decorator. Returns `ItemClass`

        :param ItemClass: A StorageTuple with a group from ItemStorageGroupEnum
        :return: ItemClass
        """
        # Python must import and register the baseclass before registering
        # any classes that import from it, so the first one registered is the
        # base class
        if ItemClass.storageGroup not in ObjectStorageContext._BaseClassByGroup:
            ObjectStorageContext._BaseClassByGroup[
                ItemClass.storageGroup
            ] = ItemClass

        cls.__registerRelationsFromClass(ItemClass, isMemberTuple=False)

        # BaseClasses are not always registered as tuples
        if ItemClass.tupleType() and ItemClass.tupleType() in TUPLE_TYPES:
            cls.__registerMemberTuples(ItemClass)

        return ItemClass

    @classmethod
    def __registerMemberTuples(cls, ItemClass):
        typeHints = get_type_hints(ItemClass, include_extras=True)
        for fieldName in ItemClass.tupleFieldNames():
            hint = typeHints.get(fieldName)
            if hint:
                for TypingClassArg in get_args(hint):
                    if inspect.isclass(TypingClassArg) and issubclass(
                        TypingClassArg, StorageMemberTuple
                    ):
                        cls._ItemParentClassByTupleType[
                            TypingClassArg.tupleType()
                        ] = ItemClass
                        cls.__registerRelationsFromClass(
                            TypingClassArg, isMemberTuple=True
                        )

    @classmethod
    def __registerRelationsFromClass(cls, TupleWithRelations, isMemberTuple):
        relations = list(
            filter(
                lambda r: isinstance(r, RelationField),
                TupleWithRelations.__dict__.values(),
            )
        )
        for relation in relations:
            # JJC Member Tuples should not participate in storage or relations
            # Add a helpful exception for this use case that isn't implemented
            if isMemberTuple:
                if relation.cascadeOnDelete or relation.cascadeOnUpdate:
                    raise Exception(
                        "StorageMemberTuple classes can not cascade "
                        "anything, pass cascadeOnDelete=False, "
                        "cascadeOnUpdate=False to RelationField"
                    )
                continue

            # noinspection PyProtectedMember
            relation._setOriginClass(TupleWithRelations)
            cls._RelationGraph.add(relation)

    @classmethod
    @property
    def _relationGraph(cls) -> RelationGraph:
        return cls._RelationGraph

    @classmethod
    def registerValidator(
        cls,
        ValidatorClass: Type[TupleValidatorABC],
    ) -> Type[TupleValidatorABC]:
        """Register Validator

        Registers a Validator with the `ObjectStorageContext` and calls the
        `validate` method on stores and loads. Meant to be used as a decorator

        :param ValidatorClass: TupleValidatorABC class to register
        :return: ValidatorClass
        """

        # We store an instance of the validator
        cls._Validators.append(ValidatorClass())

        return ValidatorClass

    @classmethod
    def Validators(cls) -> list[TupleValidatorABC]:
        """Validators

        Returns a list of all the validators registered with the StorageContext

        :return:
        """
        return cls._Validators

    def validateKeyDoesNotExist(
        self, group: ItemStorageGroupEnum, itemKey: str
    ) -> None:
        """Validate Key

        Validate the key for a particular group. Raises `NonUniqueNameError` if
        an item with the same key already exists. Should be called before
        binding, storing, and updating keys.

        :param group: Group to check key in
        :param itemKey: Key to check for uniqueness in
        :return: None. Raises NonUniqueNameError if item with same key exists
        """
        try:
            existingItem = self.getItem(group, itemKey)
        except ItemNotFoundError:
            return

        if existingItem is not None:
            raise NonUniqueNameError(f"Key {itemKey} already exists")

    @abstractmethod
    def load(self) -> None:
        """Load

        Call this method after constructing the class, this will load the
        project ready for use.
        """

    @property
    @abstractmethod
    def project(self) -> ContextProjectInfo:
        """Project

        Returns a tuple with information about this project

        :return: A ContextProjectInfo
        """
        raise NotImplementedError()

    @abstractmethod
    def validateItem(self, item):
        """Validate Item

        Validate the tuples as a whole and the individual `TupleFields`

        :param item: Item to be validated
        :return: None. Raises exceptions if validaton errors
        """
        raise NotImplementedError()

    @abstractmethod
    def expungeItem(self, item: StorageTuple) -> None:
        """Unbind Item

        Unbinds an item from the `ObjectStorageContext`, separating it from the
        storage context. The item cannot be used with with the
        ObjectStorageContext unless rebound

        :param item: Item to unbind
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def expireItem(self, item: StorageTuple) -> None:
        """Expire Item

        Marks an item as expired. This item cannot be bound with the
        StorageContext again and therefore cannot be reused

        :param item: Item to be expired
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def getItem(self, group: ItemStorageGroupEnum, key: str) -> StorageTuple:
        """Get Item

        Get item from `group` with a particular `key`. Raises an
        `ItemNotFoundError` if the item does not exist in the `group`.

        :param group: Group to fetch item from
        :param key: Key of the item to group
        :return: Item with `key` from `group`
        """
        raise NotImplementedError()

    @abstractmethod
    def getItems(
        self,
        group: ItemStorageGroupEnum,
    ) -> Iterator[StorageTuple]:
        """Get Items

        Get all items of `group`.

        :param group: Group to fetch items from
        :return: Iterator over items for this group
        """
        raise NotImplementedError()

    def getItemMap(
        self, group: ItemStorageGroupEnum
    ) -> dict[str, StorageTuple]:
        """Get Item Map

        Get a dictionary with key=key and value=item

        :param group: Group to fetch items from
        :return: A dictionary with all the objects
        True
        """
        raise NotImplementedError()

    @abstractmethod
    def addItem(self, item: StorageTuple):
        """Store Item

        Store an item to the underlying storage. Item needs to be bound to
        the ObjectStorageContext first.

        :param item: Item to store
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def mergeItem(self, item: StorageTuple) -> StorageTuple:
        """Merge Item

        Merges updated item which has the same key as item. Meant to
        be used when an item data is updated (except the key). Invalidates
        instances of the old item with the same key. Returns the updated
        item. Raises `ItemNotFoundError` if item is not stored.


        :param item: Item to be merged
        :return: Bound and stored item
        """
        raise NotImplementedError()

    @abstractmethod
    def updateItemKey(
        self,
        item: StorageTuple,
        newName: str,
    ) -> None:
        """Update Key

        Update the key of a renamed item.

        :param item: Item whose key is to be updated
        :param newName: New name
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def allBranches(self) -> List[str]:
        """All Branches

        Get a list of all user-accessible (Attune) branches

        :return: List of strings
        """
        raise NotImplementedError()

    @abstractmethod
    def allRemotes(self) -> List[tuple[str, str]]:
        """All Remotes

        Get a list of all remotes (name, url pair) defined for the project.

        :return: List of tuples of strings
        """
        raise NotImplementedError()

    @abstractmethod
    def addRemote(self, remote: str, url: str) -> None:
        """Add Remote

        Add a new remote to the project

        :param remote: Name of the remote. Will override existing remote if
        one exists with the same name
        :param url: URL of the remote
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def deleteItem(self, item: StorageTuple):
        """Delete Item

        Delete item from the underlying storage and unbind it

        :param item: Item to be deleted
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def commit(self, msg: str):
        """Create Commit

        Create a raw commit on the working branch

        :param msg: Commit message for the commit
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def checkoutBranch(self, branchName: str) -> None:
        """Checkout Branch

        Checkout (create or switch) to a new (or existing) branch in Git

        :param branchName: Name of the branch to create (or switch if already
        exists)
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def setCommitterSignature(self, name: str, email: str) -> None:
        """Set Committer Signature

        Set the name and email address of the user to use for Squash and Merge
        commits

        :param name: Name of the committer
        :param email: Email of the committer
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def mergeBranches(self, sourceBranch: str) -> None:
        """Merge Branches

        Merge sourceBranch with the currently checked out branch. Reverts and
        does not proceed if led to a merge conflict

        :param sourceBranch: Name of the branch to merge
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def squashAndMergeWorking(self, mergeCommitMessage: str) -> None:
        """Squash and Merge Working

        Creates a commit on the checked branch with all the work since the
        previous commit

        :param mergeCommitMessage: Message to use for the commit
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def pushToRemote(
        self, remote: str, username: str, password: str = None
    ) -> None:
        """Push to Remote

        Push all commits to the URL of the selected remote

        :param remote: Name of the remote to push to
        :param username: Username for remote which has access to the project
        repository
        :param password: Password for the username account
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def getCommits(self) -> Generator[GitCommitTuple, None, None]:
        """Get Commits

        Get all commits for the current checked out branch in reverse
        chronological order

        :return: Generator iterator over commits
        """
        raise NotImplementedError()

    def _cascadeUpdateKey(
        self, itemForKeyUpdate: StorageTuple, newKey: str
    ) -> None:
        """Cascade Update

        This method updates all stored items that point to the key of item
        being updated.

        :param ClassForKeyUpdate: The class of the item being updated
        :param newKey: the new key to use
        :param oldKey: the old key we replacing

        """
        oldKey = itemForKeyUpdate.key

        # Delete references that point to item
        # Handle the simple cases first, that's 1-1
        def handleOneToOne(originRelation, otherItem):
            refFieldName = originRelation.referenceKeyFieldName
            if getattr(otherItem, refFieldName) != oldKey:
                return

            setattr(otherItem, refFieldName, newKey)
            self.mergeItem(otherItem)

        # Handle the one to many with a list of strings case
        def handleOneToManyWithStringList(originRelation, otherItem):
            # This will be a computationally costly exercise.
            refFieldName = originRelation.referenceKeyFieldName
            listVal = getattr(otherItem, refFieldName)
            if not listVal or not oldKey in listVal:
                return

            listVal = [newKey if key == oldKey else key for key in listVal]
            setattr(otherItem, refFieldName, listVal)
            self.mergeItem(otherItem)

        # Handle the one to many with a list of tuples that point to the key
        def handleOneToManyWithTupleList(originRelation, otherItem):
            # This will be a computationally costly exercise.
            refFieldName = originRelation.referenceKeyFieldName
            memberRefFieldName = originRelation.memberReferenceKeyFieldName
            listVal = getattr(otherItem, refFieldName)
            if not listVal:
                return

            updated = False
            for memberTuple in listVal:
                if getattr(memberTuple, memberRefFieldName) == oldKey:
                    setattr(memberTuple, memberRefFieldName, newKey)
                    updated = True

            if updated:
                self.mergeItem(otherItem)

        # Load the relations for this method
        relationsPointingToOurKey: list[
            RelationField
        ] = ObjectStorageContext._relationGraph.getRelationsToStorageTupleKey(
            itemForKeyUpdate.__class__
        )

        # Iterate through each relation
        for originRelation in relationsPointingToOurKey:
            if not originRelation.cascadeOnUpdate:
                continue

            otherItemsIter = filter(
                lambda r: isinstance(r, originRelation.OriginClass),
                self.getItems(originRelation.OriginClass.storageGroup),
            )
            for otherItem in otherItemsIter:
                # If we've deleted it, then move on.
                if otherItem.storageIsExpired:
                    continue

                # handle the four relation cases
                if originRelation.isList:
                    if originRelation.memberReferenceKeyFieldName:
                        handleOneToManyWithTupleList(originRelation, otherItem)
                    else:
                        handleOneToManyWithStringList(originRelation, otherItem)

                else:
                    if originRelation.memberReferenceKeyFieldName:
                        raise NotImplementedError()
                    else:
                        handleOneToOne(originRelation, otherItem)

    def _cascadeDelete(self, itemToDelete: StorageTuple) -> None:
        """Cascade Delete

        This method deletes all stored items that point to the key of item
        being deleted.

        :param: itemToDelete The item being deleted

        """

        # Delete references that point to item
        # Handle the simple cases first, that's 1-1
        def handleOneToOne(originRelation, otherItem):
            refFieldName = originRelation.referenceKeyFieldName
            if getattr(otherItem, refFieldName) != itemToDelete.key:
                return

            if originRelation.cascadeOnDelete:
                self.deleteItem(otherItem)
            else:
                setattr(otherItem, refFieldName, None)
                self.mergeItem(otherItem)

        # Handle the one to many with a list of strings case
        def handleOneToManyWithStringList(originRelation, otherItem):
            # We could just set the entry to None, but I doubt that's useful
            assert originRelation.cascadeOnDelete, "We're only cascade deleting"
            refFieldName = originRelation.referenceKeyFieldName
            listVal = getattr(otherItem, refFieldName)
            if not listVal:
                return

            listVal = [key for key in listVal if key != itemToDelete.key]
            setattr(otherItem, refFieldName, listVal)

        # Handle the one to many with a list of tuples that point to the key
        def handleOneToManyWithTupleList(originRelation, otherItem):
            assert originRelation.cascadeOnDelete, "We're only cascade deleting"
            refFieldName = originRelation.referenceKeyFieldName
            memberRefFieldName = originRelation.memberReferenceKeyFieldName
            listVal = getattr(otherItem, refFieldName)
            if not listVal:
                return

            listVal = [
                memberTuple
                for memberTuple in listVal
                if getattr(memberTuple, memberRefFieldName) != itemToDelete.key
            ]
            setattr(otherItem, refFieldName, listVal)

        # Load the relations for this method
        ClassForDelete = itemToDelete.__class__
        relationsPointingToOurKey: list[
            RelationField
        ] = ObjectStorageContext._relationGraph.getRelationsToStorageTupleKey(
            ClassForDelete
        )

        # Iterate through each relation
        for originRelation in relationsPointingToOurKey:
            otherItemsIter = filter(
                lambda r: isinstance(r, originRelation.OriginClass),
                self.getItems(originRelation.OriginClass.storageGroup),
            )
            for otherItem in otherItemsIter:
                # If we've deleted it, then move on.
                if otherItem.storageIsExpired:
                    continue

                # handle the four relation cases
                if originRelation.isList:
                    if originRelation.memberReferenceKeyFieldName:
                        handleOneToManyWithTupleList(originRelation, otherItem)
                    else:
                        handleOneToManyWithStringList(originRelation, otherItem)

                else:
                    if originRelation.memberReferenceKeyFieldName:
                        raise NotImplementedError()
                    else:
                        handleOneToOne(originRelation, otherItem)
