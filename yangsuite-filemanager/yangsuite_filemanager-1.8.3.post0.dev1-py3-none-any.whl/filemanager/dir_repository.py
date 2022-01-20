# Copyright 2016 Cisco Systems, Inc
import errno
import os

from yangsuite import get_logger
from .base import _YSYangSetBase
from .utility import list_yang_files, module_listing

log = get_logger(__name__)


class YSYangDirectoryRepository(_YSYangSetBase):
    """A collection of YANG modules in an arbitrary directory.

    TODO: optionally include subdirectories as well.

    Useful for console scripts and other code executed outside of the
    core YANG Suite server application, where the filesystem hierarchy provided
    by :func:`yangsuite.paths.get_path` is overly restrictive and cumbersome.
    """

    def __init__(self, path, owner=None, assume_correct_name=False):
        if not os.path.isdir(path):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        self.path = path
        super(YSYangDirectoryRepository, self).__init__(
            owner=owner,
            modules=module_listing(list_yang_files(path),
                                   assume_correct_name=assume_correct_name),
        )

    def __eq__(self, other):
        """Equality test, based on path and modules.

        Unlike _YSYangSetBase.__eq__, we do not check for owner equality.
        """
        return (self.path == other.path and self.modules == other.modules)
