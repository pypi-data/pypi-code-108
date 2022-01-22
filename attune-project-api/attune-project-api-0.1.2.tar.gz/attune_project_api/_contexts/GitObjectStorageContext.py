import json
import logging
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterator
from typing import Optional

import pygit2
import pytz
from vortex.Tuple import Tuple

from .git_lib_mixin import GitLibMixin
from ..Exceptions import ItemNotFoundError
from ..ObjectStorageContext import ContextProjectInfo
from ..ObjectStorageContext import ObjectStorageContext
from ..ObjectStorageContext import ObjectStorageContextFileMixin
from ..ObjectStorageContext import VersionedFileContent
from ..ObjectStorageContext import VersionedFileInfo
from ..StorageTuple import ItemStorageGroupEnum
from ..StorageTuple import StorageTuple
from .._private.utils import makeStorageKey


logger = logging.getLogger(__name__)

DIR_CREATE_MODE = 0o700


class ProjectValidationError(Exception):
    def __init__(self, errors: list[str]):
        Exception.__init__(
            self, "%s errors occurred during load of project" % len(errors)
        )
        self.errors: list[str] = errors


class GitObjectStorageContextFileMixin(ObjectStorageContextFileMixin):
    CONTENTS_PATH = "contents"

    # ---------------
    # List the abstract methods we depend on

    # @abstractmethod
    # @property
    # def projectPath(self) -> Path:
    #     pass
    #
    # @abstractmethod
    # def _readFile(self, path: Path) -> bytes:
    #     pass
    #
    # @abstractmethod
    # def _writeFile(self, path: Path, data: bytes) -> None:
    #     pass
    #
    # @abstractmethod
    # def _getTree(self, path: Path) -> pygit2.Tree:
    #     pass

    # ---------------
    # Start our implementation

    @property
    def _unversionedFilesPath(self) -> Path:
        return self.projectPath / "file_storage"

    def __makeVersionedPath(self, group: ItemStorageGroupEnum, key: str):
        return Path(f"{group.value}/{makeStorageKey(key)}") / self.CONTENTS_PATH

    def readItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> bytes:
        return self._readFile(self.__makeVersionedPath(group, key) / path)

    def writeItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path, data: bytes
    ) -> None:
        self._writeFile(self.__makeVersionedPath(group, key) / path, data)

    def listItemVersionedFiles(
        self, group: ItemStorageGroupEnum, key: str
    ) -> list[VersionedFileInfo]:
        infos = []
        try:
            tree = self._getTree(self.__makeVersionedPath(group, key))
        except FileNotFoundError:
            logger.debug(
                "No content files found for Group %s, Key %s", group, key
            )
            return []

        def recurse(tree, parentPath: Path):
            for item in tree:
                if isinstance(item, pygit2.Tree):
                    recurse(item, parentPath / item.name)
                else:
                    assert isinstance(item, pygit2.Object)
                    infos.append(
                        VersionedFileInfo(
                            path=parentPath / item.name,
                            size=item.size,
                            executable=item.filemode
                            & pygit2.GIT_FILEMODE_BLOB_EXECUTABLE,
                            sha1=item.hex,
                        )
                    )

        recurse(tree, Path())
        return infos

    def getItemVersionedFileContent(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> Optional[VersionedFileContent]:
        try:
            tree = self._getTree(
                self.__makeVersionedPath(group, key) / path.parent
            )
        except FileNotFoundError:
            logger.error(
                "No file found for Group %s, Key %s, Path %s", group, key, path
            )
            raise

        if path.name not in tree:
            logger.error(
                "No file found for Group %s, Key %s, Path %s", group, key, path
            )
            raise FileNotFoundError()

        fileObject = tree / path.name
        if not isinstance(fileObject, pygit2.Object):
            logger.error(
                "Found a directory, not a file for Group %s, Key %s, Path %s",
                group,
                key,
                path,
            )
            raise FileNotFoundError()

        return VersionedFileContent(
            path=path,
            data=fileObject.data,
            executable=fileObject.filemode
            & pygit2.GIT_FILEMODE_BLOB_EXECUTABLE,
            sha1=fileObject.hex,
        )

    def setItemVersionedFileContent(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        path: Path,
        data: bytes,
        executable: bool,
    ) -> None:
        treePath = self.__makeVersionedPath(group, key) / path
        mode = (
            pygit2.GIT_FILEMODE_BLOB_EXECUTABLE
            if executable
            else pygit2.GIT_FILEMODE_BLOB
        )

        self._writeFile(
            str(treePath),
            data,
            mode=mode,
        )

    def moveItemVersionedFile(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        fromPath: Path,
        toPath: Path,
    ) -> None:
        fromContentPath = self.__makeVersionedPath(group, key) / fromPath
        toContentPath = self.__makeVersionedPath(group, key) / toPath
        self._moveFile(fromContentPath, toContentPath)

    def moveItemVersionedDirectory(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        fromPath: Path,
        toPath: Path,
    ) -> None:
        fromContentPath = self.__makeVersionedPath(group, key) / fromPath
        toContentPath = self.__makeVersionedPath(group, key) / toPath
        self._moveDirectory(fromContentPath, toContentPath)

    def deleteItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> None:
        contentPath = self.__makeVersionedPath(group, key) / path
        self._deleteFile(contentPath)

    def deleteItemVersionedDirectory(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> None:
        contentPath = self.__makeVersionedPath(group, key) / path
        self._deleteDirectory(contentPath)

    def getItemLargeFilesPath(
        self, group: ItemStorageGroupEnum, key: str
    ) -> Path:
        path = (
            self._unversionedFilesPath
            / group.value
            / makeStorageKey(key)
            / self.CONTENTS_PATH
        )
        path.mkdir(mode=DIR_CREATE_MODE, parents=True, exist_ok=True)
        return path


class GitObjectStorageContext(
    GitLibMixin, ObjectStorageContext, GitObjectStorageContextFileMixin
):
    def __init__(self, projectPath: Path, info: ContextProjectInfo):
        assert isinstance(projectPath, Path), "projectPath is not of type Path"
        GitLibMixin.__init__(self, projectPath)
        self.__projectInfo = info

        """ This is equivalent to an Identity Map in SqlAlchemy Session
        Holds references to all instances fetched from the storage
        ensuring that "one and only one" reference exists for an item
        For example, s1 = getItem("Step1"), s2 = getItem("Step1")
        id(s1) == id(s2) """
        self.__instanceByKeyByGroup = defaultdict(dict)

        self.__instanceByKeyByGroup[ItemStorageGroupEnum.Step] = {}
        self.__instanceByKeyByGroup[ItemStorageGroupEnum.Parameter] = {}
        self.__instanceByKeyByGroup[ItemStorageGroupEnum.FileArchive] = {}

    def load(self):
        # Cache all items in memory upon load.
        # This will speed up the access of the data
        self.__loadItems(ItemStorageGroupEnum.Parameter)
        self.__loadItems(ItemStorageGroupEnum.FileArchive)
        self.__loadItems(ItemStorageGroupEnum.Step)

    @property
    def project(self) -> ContextProjectInfo:
        return self.__projectInfo

    def getItem(
        self, group: ItemStorageGroupEnum, key: str
    ) -> Optional[StorageTuple]:
        assert group in self.__instanceByKeyByGroup, (
            "Group %s is not a valid" % group
        )
        itemsByKey = self.__instanceByKeyByGroup[group]

        if key not in itemsByKey:
            raise ItemNotFoundError(
                "Item not found, Group [%s], Key [%s]" % (group, key)
            )

        return itemsByKey[key]

    def getItems(
        self,
        group: ItemStorageGroupEnum,
    ) -> Iterator[StorageTuple]:
        assert group in self.__instanceByKeyByGroup, (
            "Group %s is not " "valid" % group
        )
        return iter(self.__instanceByKeyByGroup[group].values())

    def getItemMap(
        self, group: ItemStorageGroupEnum
    ) -> dict[str, StorageTuple]:
        assert group in self.__instanceByKeyByGroup, (
            "Group %s is not " "valid" % group
        )
        return self.__instanceByKeyByGroup[group].copy()

    def addItem(self, item: StorageTuple):
        item._bind(self)

        # Validate the item before storing
        self.validateItem(item)
        self.validateKeyDoesNotExist(group=item.storageGroup, itemKey=item.key)

        self.__writeItem(item)
        self.__storeReferenceToTuple(item)

    def validateItem(self, item):
        # TupleField Validation
        Tuple.restfulJsonDictToTupleWithValidation(
            item.tupleToRestfulJsonDict(), item.__class__
        )
        # Tuple Validation
        for validator in self.Validators():
            validator.validate(self, item)

    def expungeItem(self, item: StorageTuple):
        # noinspection PyProtectedMember
        item._unbind()

    def expireItem(self, item: StorageTuple) -> None:
        # noinspection PyProtectedMember
        item._expire()

    def reloadItem(self, item: StorageTuple) -> StorageTuple:
        freshItem = self.__readItem(item.__class__, item.key)
        self.__storeReferenceToTuple(freshItem)
        freshItem._bind(self)
        item._expire()
        return freshItem

    def mergeItem(self, item: StorageTuple) -> StorageTuple:
        try:
            existingItem = self.getItem(item.storageGroup, item.key)

            # If it's the same item we have in our store, then there is
            # nothing to do.
            if item is existingItem:
                # Rebind the item, and any member tuples it has
                item._bind(self)
                self.__writeItem(item)
                return item

        except ItemNotFoundError:
            existingItem = None

        if existingItem is None:
            raise ItemNotFoundError("Item does not yet exist in context")

        if item.tupleType() != existingItem.tupleType():
            raise TypeError("Items need to be of same type for merging")

        # Unbind the oldItem, bind the item
        self.expungeItem(existingItem)
        self.expireItem(existingItem)

        # noinspection PyProtectedMember
        item._bind(self)

        # Merge item in storage. We just need to store the item
        self.__writeItem(item)
        self.__storeReferenceToTuple(item)

        return item

    def updateItemKey(self, item: StorageTuple, newKey: str) -> None:
        if not item.storageContext:
            raise Exception(
                "Item must be merged using old key before updating to new key"
            )
        oldKey = item.key

        self.validateKeyDoesNotExist(item.storageGroup, newKey)

        # Update all the objects that reference this key
        self._cascadeUpdateKey(item, newKey)

        # Rename the item from the instance cache
        self.__removeReferenceToTuple(item)

        # Update the key
        item.key = newKey

        # Move the whole tree of contents over first, to ensure we include
        # any non-json content (EG, the versioned file archives)
        self.__moveItemDirectory(item.storageGroup, oldKey, newKey)

        # Move any unversioned storage, their storage is based on the key
        self.__moveItemUnversionedStorage(item.storageGroup, oldKey, newKey)

        # Write the updated json files, overwriting some of the files we just
        # moved
        self.__writeItem(item)

        # Store the new reference
        self.__storeReferenceToTuple(item)

    def __storeReferenceToTuple(self, item):
        assert (
            item.storageContext is self
        ), "Item must be bound before it is cached"
        self.__instanceByKeyByGroup[item.storageGroup][item.key] = item

    def __removeReferenceToTuple(self, item):
        self.__instanceByKeyByGroup[item.storageGroup].pop(item.key, None)

    def __loadItems(self, group: ItemStorageGroupEnum) -> None:
        startTime = datetime.now(pytz.utc)
        try:
            tree = self._getTree(Path(group.value))
        except FileNotFoundError:
            return

        BaseClass = GitObjectStorageContext._BaseClassByGroup[group]

        errors = []
        for object_tree in tree:
            # object_tree.name is the sanitized key (i.e. folder name) and not
            # the name of the tuple
            try:
                item = self.__readItem(BaseClass, object_tree.name)
            except (TypeError, ItemNotFoundError) as e:
                errors.append(
                    "Group %s, Key %s, Error: %s"
                    % (group.value, object_tree.name, str(e))
                )
                continue

            item._bind(self)
            self.__storeReferenceToTuple(item)

        if errors:
            raise ProjectValidationError(errors)

        logger.debug(
            "Completed loading group %s in %s",
            group,
            datetime.now(pytz.utc) - startTime,
        )

    def __writeItem(self, item: type[StorageTuple]) -> None:
        fields = item.tupleToRestfulJsonDict()
        comment = fields.pop("comment", None)
        script = fields.pop("script", None)

        # FIXME If the name isn't suitable for storage
        #  then an exception needs raising instead.
        sanitizedItemKey = makeStorageKey(item.key)
        group = item.storageGroup.value
        itemPath = Path(f"{group}/{sanitizedItemKey}")

        self._writeFile(
            str(itemPath / "metadata.json"),
            json.dumps(
                fields,
                indent=4,
                sort_keys=True,
                separators=(", ", ": "),
            ).encode(),
        )

        if comment:
            self._writeFile(str(itemPath / "comment.md"), comment.encode())
        if script:
            self._writeFile(str(itemPath / "script.txt"), script.encode())

    def __moveItemDirectory(
        self, group: ItemStorageGroupEnum, oldKey: str, newKey: str
    ):
        oldKeyPath = Path(f"{group.value}/{oldKey}")
        newKeyPath = Path(f"{group.value}/{newKey}")
        self._moveDirectory(oldKeyPath, newKeyPath)

    def __moveItemUnversionedStorage(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        newKey: str,
    ) -> None:
        oldPath = self.getItemLargeFilesPath(group, key)
        newPath = self.getItemLargeFilesPath(group, newKey)

        if oldPath.exists():
            newPath.parent.mkdir(
                mode=DIR_CREATE_MODE, parents=True, exist_ok=True
            )
            if newPath.exists():
                shutil.rmtree(newPath)

            shutil.move(oldPath, newPath.parent)

            if oldPath.parent.exists():
                shutil.rmtree(oldPath.parent)

    def __deleteItem(self, item: type[StorageTuple]) -> None:
        group = item.storageGroup.value
        itemPath = Path(f"{group}/{item.key}")
        self._deleteDirectory(itemPath)

    def __readItem(
        self, ItemClass: type[StorageTuple], key: str
    ) -> StorageTuple:
        groupStr = ItemClass.storageGroup.value
        path = Path(f"{groupStr}/{makeStorageKey(key)}")
        try:
            data = self._readFile(path / "metadata.json")
            metadataStr = data.decode()
            metadata = json.loads(metadataStr)
        except FileNotFoundError:
            raise ItemNotFoundError(f"{key} does not exist in {groupStr}")

        try:
            commentData = self._readFile(path / "comment.md")
            if commentData is None:
                # Every item has an comment associated with it. If it does not
                # exist we need to set it to None
                metadata["comment"] = None
            else:
                metadata["comment"] = commentData.decode()
        except FileNotFoundError:
            metadata["comment"] = ""

        try:
            scriptData = self._readFile(path / "script.txt")
            # Not every item has target 'script' associated with it
            if scriptData is not None:
                metadata["script"] = scriptData.decode()
        except FileNotFoundError:
            pass

        # noinspection PyTypeChecker
        return Tuple.restfulJsonDictToTupleWithValidation(metadata, ItemClass)

    def deleteItem(self, item: StorageTuple):
        if item.storageContext is None:
            raise ValueError(f"ObjectStorageContext not bound to {item.name}")

        self.__deleteItem(item)

        self.__removeReferenceToTuple(item)
        self.expungeItem(item)
        self.expireItem(item)
        self._cascadeDelete(item)
