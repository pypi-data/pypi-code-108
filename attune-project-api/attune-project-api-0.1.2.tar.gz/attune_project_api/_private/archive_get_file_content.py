from pathlib import Path

from attune_project_api.ObjectStorageContext import ArchiveFileContent
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

MAX_EXTRACT_SIZE = 10 * 1024 * 1024


def __registerArchiveContentGetter(key: str):
    def wrapper(getterMethod):
        __ARCHIVE_LISTER_BY_FORMAT_KEY[key] = getterMethod
        return getterMethod

    return wrapper


def getArchiveFileContent(
    archivePath: Path, memberPath: Path
) -> ArchiveFileContent:
    format = guessArchiveFormat(archivePath)
    getter = __ARCHIVE_LISTER_BY_FORMAT_KEY[format.key]
    return getter(archivePath, memberPath)


def __assureSmallSize(path: Path, size: int) -> None:
    if size > MAX_EXTRACT_SIZE:
        raise Exception(
            "Requested file is more than %s, we're not "
            "loading that into memory. %s (%s)" % (MAX_EXTRACT_SIZE, path, size)
        )


@__registerArchiveContentGetter(ARCHIVE_FORMAT_KEY_7Z)
def _get7z(archivePath: Path, memberPath: Path) -> ArchiveFileContent:
    from py7zr import SevenZipFile

    pathStr = str(memberPath)

    with SevenZipFile(archivePath, "r") as reader:
        info = next(filter(lambda o: o.filename == pathStr, reader.files))
        __assureSmallSize(memberPath, info.uncompressed)
        data = reader.read([pathStr])[pathStr].read()
        return ArchiveFileContent(memberPath, data, False)


@__registerArchiveContentGetter(ARCHIVE_FORMAT_KEY_ZIP)
def _getZip(archivePath: Path, memberPath: Path) -> ArchiveFileContent:
    from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

    pathStr = str(memberPath)

    with ZipFile(archivePath, "r", ZIP_DEFLATED) as reader:
        info: ZipInfo = reader.getinfo(pathStr)
        __assureSmallSize(memberPath, info.file_size)
        data = reader.read(pathStr)
        return ArchiveFileContent(memberPath, data, False)


@__registerArchiveContentGetter(ARCHIVE_FORMAT_KEY_TAR)
@__registerArchiveContentGetter(ARCHIVE_FORMAT_KEY_TAR_GZ)
@__registerArchiveContentGetter(ARCHIVE_FORMAT_KEY_TAR_BZ2)
@__registerArchiveContentGetter(ARCHIVE_FORMAT_KEY_TAR_XZ)
def _getTarFile(archivePath: Path, memberPath: Path) -> ArchiveFileContent:
    from tarfile import TarFile, TarInfo

    pathStr = str(memberPath)

    with TarFile.open(archivePath, "r") as reader:
        info: TarInfo = reader.getmember(pathStr)
        __assureSmallSize(memberPath, info.size)
        data = reader.extractfile(pathStr).read()
        return ArchiveFileContent(memberPath, data, False)
