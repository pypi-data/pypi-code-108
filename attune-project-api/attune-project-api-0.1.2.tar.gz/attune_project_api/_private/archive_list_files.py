from pathlib import Path

from attune_project_api.ObjectStorageContext import ArchiveFileInfo
from attune_project_api._private.archive_format import ARCHIVE_FORMAT_KEY_7Z
from attune_project_api._private.archive_format import ARCHIVE_FORMAT_KEY_TAR
from attune_project_api._private.archive_format import (
    ARCHIVE_FORMAT_KEY_TAR_BZ2,
)
from attune_project_api._private.archive_format import ARCHIVE_FORMAT_KEY_TAR_GZ
from attune_project_api._private.archive_format import ARCHIVE_FORMAT_KEY_TAR_XZ
from attune_project_api._private.archive_format import ARCHIVE_FORMAT_KEY_ZIP
from attune_project_api._private.archive_format import guessArchiveFormat

__ARCHIVE_LISTER_BY_FORMAT_KEY = {}


def __registerArchiveLister(key: str):
    def wrapper(listerMethod):
        __ARCHIVE_LISTER_BY_FORMAT_KEY[key] = listerMethod
        return listerMethod

    return wrapper


def canListFiles(archiveFormatKey: str) -> bool:
    return archiveFormatKey in __ARCHIVE_LISTER_BY_FORMAT_KEY


def listArchiveFiles(path: Path) -> list[ArchiveFileInfo]:
    format = guessArchiveFormat(path)
    lister = __ARCHIVE_LISTER_BY_FORMAT_KEY[format.key]
    return lister(path)


@__registerArchiveLister(ARCHIVE_FORMAT_KEY_7Z)
def _list7z(path: Path) -> list[ArchiveFileInfo]:
    from py7zr import SevenZipFile

    with SevenZipFile(path, "r") as reader:
        files = reader.files
        return [
            ArchiveFileInfo(Path(m.filename), m.uncompressed)
            for m in files
            if not m.is_directory
        ]


@__registerArchiveLister(ARCHIVE_FORMAT_KEY_ZIP)
def _listZip(path: Path) -> list[ArchiveFileInfo]:
    from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

    with ZipFile(path, "r", ZIP_DEFLATED) as reader:
        infos: list[ZipInfo] = reader.infolist()
        return [
            ArchiveFileInfo(Path(m.filename), m.file_size)
            for m in infos
            if not m.is_dir()
        ]


@__registerArchiveLister(ARCHIVE_FORMAT_KEY_TAR)
@__registerArchiveLister(ARCHIVE_FORMAT_KEY_TAR_GZ)
@__registerArchiveLister(ARCHIVE_FORMAT_KEY_TAR_BZ2)
@__registerArchiveLister(ARCHIVE_FORMAT_KEY_TAR_XZ)
def _listTarFile(path: Path) -> list[ArchiveFileInfo]:
    from tarfile import TarFile, TarInfo, DIRTYPE

    with TarFile.open(path, "r") as reader:
        members: list[TarInfo] = reader.getmembers()
        return [
            ArchiveFileInfo(Path(m.path), m.size)
            for m in members
            if m.type != DIRTYPE
        ]
