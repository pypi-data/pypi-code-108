"""
interfaces that are unique to the Unix operating system, or in some cases to some or many variants of it.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def chdir():
    """
    Change the current working directory to path.
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def chmod():
    """
    Change the mode of path to the numeric mode.
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def execv():
    """
    Execute the executable path with argument list args, replacing the current process
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def execve():
    """
    Execute the executable path with argument list args, and environment env, replacing the current process
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def fdopen():
    """
    Return an open file object connected to the file descriptor fd
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def fork():
    """
    Fork a child process
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def mkdir():
    """
    Create a directory named path with numeric mode mode
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def open():
    """
    Open the file
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def popen():
    """
    Open a pipe to or from command.
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def read():
    """
    Read bytes from files
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def readlink():
    """
    Return a string representing the path to which the symbolic link points
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def rename():
    """
    Rename the file or directory src to dst
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def rmdir():
    """
    Remove the directory path
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def system():
    """
    Execute the command (a string) in a subshell
    """
    pass


@tags(TagConsts.UNIX_SPECIFIX_SERVICES)
def write():
    """
    Write the string str to file descriptor fd
    """
    pass
