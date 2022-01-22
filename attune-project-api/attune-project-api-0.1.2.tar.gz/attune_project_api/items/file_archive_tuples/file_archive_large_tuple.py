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
import logging
from pathlib import Path
from typing import Optional

from attune_project_api.ObjectStorageContext import ArchiveFileContent
from attune_project_api.ObjectStorageContext import ArchiveFileInfo
from attune_project_api._contexts.GitObjectStorageContext import (
    GitObjectStorageContext,
)
from attune_project_api._private.archive_format import (
    ARCHIVE_FORMAT_KEY_UNKNOWN,
)
from attune_project_api._private.archive_format import ArchiveFormat
from attune_project_api._private.archive_format import (
    InvalidArchiveFormatException,
)
from attune_project_api._private.archive_format import archiveFormatByKey
from attune_project_api._private.archive_format import guessArchiveFormat
from attune_project_api._private.archive_hasher import makeArchiveMd5
from attune_project_api.items.file_archive_tuples.file_archive_tuple import (
    FileArchiveTuple,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    FileArchiveTupleTypeEnum,
)
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

logger = logging.getLogger(__name__)


@GitObjectStorageContext.registerItemClass
@addTupleType
class FileArchiveLargeTuple(FileArchiveTuple):
    """Archive Large Tuple

    The contents of these archives are not stored in Attune.


    """

    __tupleType__ = FileArchiveTupleTypeEnum.LARGE.value
    __ARCHIVE_FILE_NAME = "large_file_archive"

    #: This is the md5 hash of the last downloaded file
    md5: Optional[str] = TupleField()

    #: This is the size of the last downloaded file
    size: Optional[int] = TupleField()

    #: This is the name of the file that was last manually uploaded
    fileName: Optional[str] = TupleField()

    #: This is the key of the format of the archive
    # See archive_format.py, ARCHIVE_FORMAT_KEY_*
    formatKey: Optional[str] = TupleField()

    #: The uri to pull this file from.
    # This can be HTTP(S) or SSH
    remoteUri: Optional[str] = TupleField()

    @classmethod
    @property
    def niceName(cls) -> str:
        # This is meant to be an abstract method
        return "Large Archives"

    @property
    def archiveFormat(self) -> Optional[ArchiveFormat]:
        return archiveFormatByKey.get(self.formatKey, None)

    @property
    def archivePath(self) -> Path:
        return (
            self.storageContext.getItemLargeFilesPath(
                self.storageGroup, self.key
            )
            / self.__ARCHIVE_FILE_NAME
        )

    @property
    def listFiles(self) -> list[ArchiveFileInfo]:
        path = self.archivePath
        if not path.exists():
            return []
        from attune_project_api._private.archive_list_files import (
            listArchiveFiles,
        )

        return listArchiveFiles(self.archivePath)

    def getFileContent(self, path: Path) -> ArchiveFileContent:
        archivePath = self.archivePath
        if not archivePath.exists():
            raise FileNotFoundError(
                "Archive file %s doesn't exist" % archivePath
            )

        from attune_project_api._private.archive_get_file_content import (
            getArchiveFileContent,
        )

        return getArchiveFileContent(archivePath, path)

    @property
    def isListable(self) -> bool:
        from attune_project_api._private.archive_list_files import canListFiles

        return canListFiles(self.formatKey)

    @property
    def isTarFile(self) -> bool:
        """Is Tar File"""
        from attune_project_api._private.archive_format import isTarFile

        return isTarFile(self.formatKey)

    @property
    def is7zFile(self) -> bool:
        """Is 7z File"""
        from attune_project_api._private.archive_format import is7zFile

        return is7zFile(self.formatKey)

    def refreshArchiveInfo(self) -> None:
        filePath = self.archivePath

        if not filePath.exists():
            self.md5 = None
            self.size = None
            self.formatKey = None
            return

        self.size = filePath.stat().st_size
        self.md5 = makeArchiveMd5(filePath)
        try:
            self.formatKey = guessArchiveFormat(filePath).key
        except InvalidArchiveFormatException:
            self.formatKey = ARCHIVE_FORMAT_KEY_UNKNOWN

        if not self.fileName:
            self.fileName = self._makeFileName()

    def _makeFileName(self):
        allowedLetters = {chr(i) for i in range(0x30, 0x39)}  # 0-9
        allowedLetters |= {chr(i) for i in range(0x41, 0x5A)}  # A-Z
        allowedLetters |= {chr(i) for i in range(0x61, 0x7A)}  # a-z
        allowedLetters.add("_")

        name = self.name.replace(" ", "_")
        name = "".join([c for c in name if c in allowedLetters])

        return f"{name}.{self.formatKey}"
