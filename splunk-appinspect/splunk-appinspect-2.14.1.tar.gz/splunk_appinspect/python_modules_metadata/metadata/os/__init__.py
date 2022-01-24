"""
execute filesystem commands
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

from . import path  # noqa: F401

__tags__ = [TagConsts.CRITICAL_SYSTEM_MODULE]


@tags(TagConsts.FILE_READ_AND_WRITE, TagConsts.EXTERNAL_COMMAND_EXECUTION)
def system():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE, TagConsts.EXTERNAL_COMMAND_EXECUTION)
def popen():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE, TagConsts.EXTERNAL_COMMAND_EXECUTION)
def popen2():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE, TagConsts.EXTERNAL_COMMAND_EXECUTION)
def popen3():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE, TagConsts.EXTERNAL_COMMAND_EXECUTION)
def popen4():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def execle():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def execlp():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def execlpe():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def execv():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def execve():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def execvp():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def execvpe():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def _execvpe():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def spawnl():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def spawnle():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def spawnlp():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def spawnlpe():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def spawnv():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def spawnve():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def spawnvp():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def spawnvpe():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def unlink():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def makedirs():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def mkdir():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def removedirs():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def renames():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def rename():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def write():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def read():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def tmpfile():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def open():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def mknod():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def dup():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def dup2():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def fdopen():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def remove():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def _spawnvef():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def rmdir():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def symlink():
    """execute filesystem commands"""
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def link():
    """execute filesystem commands"""
    pass


@tags(TagConsts.THREAD_SECURITY)
def fork():
    """execute filesystem commands"""
    pass


@tags(TagConsts.THREAD_SECURITY)
def forkpty():
    """execute filesystem commands"""
    pass


@tags(TagConsts.THREAD_SECURITY)
def kill():
    """execute filesystem commands"""
    pass


@tags(TagConsts.THREAD_SECURITY)
def killpg():
    """execute filesystem commands"""
    pass
