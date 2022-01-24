"""
copy/move/remove/create files/directories
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
def copyfileobj():
    """copy files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def copyfile():
    """copy files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def copymode():
    """copy files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def copystat():
    """copy files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def copy():
    """copy files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def copy2():
    """copy files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def copytree():
    """copy files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def rmtree():
    """remove files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def make_archive():
    """create tar files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def _make_tarball():
    """create tar files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def _make_zipfile():
    """create tar files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def _call_external_zip():
    """create tar files/directories"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def move():
    """move files/directories"""
    pass
