"""
Copyright 2021 Adobe
All Rights Reserved.

NOTICE: Adobe permits you to use, modify, and distribute this file in accordance
with the terms of the Adobe license agreement accompanying it.
"""

import glob
import logging
import os
from typing import List


LOGGER = logging.getLogger(__file__)


class VCSUnsupported(Exception):
    """Custom error signifying a specific VCS is not supported"""

class VCSMissingRevision(Exception):
    """Custom error signifying a revision is expected but doesn't exist"""

def search_parent_dirs(directory, filename):
    """
    Search a directory and each parent directory for a filename.
    If found return the full path; otherwise return ''.
    """

    found = ''

    dir_parts = directory.split(os.path.sep)
    while dir_parts:
        filename_parts = dir_parts + [filename]
        filename_path = os.path.sep.join(filename_parts)
        if os.path.exists(filename_path):
            found = filename_path
            break
        dir_parts.pop()

    return found


def last_mtime(files, prefix=None):
    """
    Find the last modified time for a given list of files.
    """
    mtime = None

    if files:
        if prefix:
            _files = [os.path.join(prefix, f) for f in files]
        else:
            _files = files

        # NOTE: If the file doesn't exist then return 0, but then make sure a
        # 0 result gets mapped back to None.
        mtime = int(max([
            os.path.exists(fn) and os.stat(fn).st_mtime or 0 for fn in _files
        ])) or None

    return mtime


ST_MOD = 0
ST_ADD = 1
ST_REM = 2
ST_DEL = 3
ST_UNK = 4
ST_IGN = 5
ST_CLN = 6


class VCS:
    """Base class for a source tree managed by VCS"""

    def __init__(self):
        """Base constructor"""
        # Automatically set the VCS engine name
        self.vcs = self.__class__.__name__
        if self.vcs.startswith('VCS'):
            self.vcs = self.vcs[3:].lower()

        self.source_root = ''
        self._name = ''
        self._upstream_repo = ''

    @property
    def upstream_repo(self):
        """The location of the up-stream VCS repository."""
        return self._upstream_repo

    @property
    def name(self):
        """The name of the VCS project."""
        return self._name

    @property
    # pylint: disable=R0201
    def branch(self):
        """The branch name."""
        return None

    @property
    # pylint: disable=R0201,invalid-name
    def id(self):
        """The native commit identification."""
        return None

    @property
    # pylint: disable=R0201
    def user(self):
        """The user who performed the commit (if applicable)."""
        return 'n/a'

    @property
    def id_short(self):
        """
        Differs from .id for VCS that have large hash values that
        can be abbreviated.
        """
        return self.id

    @property
    def number(self):
        """
        This is the same as .id if commits have increasing commit numbers.
        Otherwise this simulates an increasing commit number.
        """
        return int(self.id)

    @property
    def modified(self):
        """
        Return none if there are no local modifications to the VCS checkout,
        otherwise return epoc seconds of the most recently modified file.

        NOTE: modified will update each time a file in the changeset is
        modified.  It cannot update, however, when a REMOVED file is added
        to the changeset because there may no longer be a file in the
        file system to stat() to get the removed time!  This means that
        modified can only updated with MODIFIED and ADDED files.
        """
        return last_mtime(
            sum(self.status()[ST_MOD:ST_ADD + 1], []),
            prefix=self.source_root
        ) or 0

    @property
    def release(self):
        """
        String representing the current state of the branch, including the
        commit number, id_short, and whether any modifications have been made
        to the local tree.
        """
        modified = self.modified
        modstr = f'.M{modified}'

        rel_str = f'{self.number}.I{self.id_short}{modstr}'

        return rel_str

    @property
    def id_string(self):
        """
        String providing a unique id of the branch and release.
        """
        return str(self.branch) + "-" + str(self.release)

    # pylint: disable=R0201
    def status(self):
        """
        Returns a tuple of lists of modified files in the changeset:
        (
            [MODIFIED, ...], # ST_MOD: changeset is modifying files
            [ADDED, ...],    # ST_ADD: changeset is adding file
            [REMOVED, ...],  # ST_REM: changeset is removing file
            [DELETED, ...],  # ST_DEL: file is missing but not in changeset
            [UNKNOWN, ...],  # ST_UNK: file exists but not in changeset
            [IGNORED, ...],  # ST_IGN: file exists but VCS explicitly ignores
            [CLEAN, ...],    # ST_CLN: file tracked by VCS and unmodified
        )
        """
        return [], [], [], [], [], [], []

    def list_files(self):
        """
        Return a list of files known to the VCS
        (committed + changeset(added, moved) - changeset(deleted))
        """
        raise NotImplementedError(f'VCS module {self.vcs} must implement list_files()')

    def info(self, include_files=False):
        """
        Return vcs information as a dict, optionally including full file
        information.
        """
        info = {
            'type': self.vcs,
            'upstream_repo': self.upstream_repo,
            'name': self.name,
            'branch': self.branch,
            'id': self.id,
            'id_short': self.id_short,
            'id_string': self.id_string,
            'number': self.number,
            'user': self.user,
            'release': self.release,
        }

        if include_files:
            info['files'] = self.list_files()
            # Do not report UNKNOWN or IGNORED files
            status_info = list(self.status())
            status_info[ST_UNK] = []
            status_info[ST_IGN] = []
            info['filestatus'] = status_info

        return info

    def __str__(self):
        """String represenation"""
        return f'{self.__class__.__name__}({self.source_root})'


def load_vcs(name, directory, *args, **argv) -> VCS:
    """
    Load a specific vcs module for the given directory and arguments.

    Args:
        name: the vcs module name
        directory: the directory to load the vcs module for
    Raises:
        VCSUnsupported: if the vcs module does not support the given directory
        TypeError: if the vcs module does not support the given directory
    """
    LOGGER.debug(f'Loading VCS module: {name}')
    vcs_module = __import__('.'.join((__name__, name)), fromlist=[__name__])
    vcs = vcs_module.VCS(directory, *args, **argv)
    return vcs


def detect_vcss(directory, *args, **argv) -> List[VCS]:
    """
    Interrogate the given directory for vcs information, returning an object
    that can be used to obtain information about the current conditions of the
    source tree.
    """
    directory = directory or os.getcwd()
    vcs_dir = os.path.dirname(__file__)
    # Ignore things that don't look like python modules
    # and list archive.py last.
    vcs_files = glob.glob(os.path.join(vcs_dir, '*.py'))
    possible_vcs = []

    errors = []
    for modpath in vcs_files:
        modname, _ = os.path.splitext(os.path.basename(modpath))
        # skip things like '__init__.py'
        if modname.startswith('_') or modname == 'version':
            continue

        try:
            vcs = load_vcs(modname, directory, *args, **argv)
            if hasattr(vcs, 'is_archive') and vcs.is_archive:
                # if an "archive" vcs config is present, it always wins
                return [vcs]

            possible_vcs.append(vcs)
        except (VCSUnsupported, TypeError) as err:
            LOGGER.debug(f'Failed {modname}: {err}')
            errors.append(str(err))

    if not possible_vcs:
        # pylint: disable=C0301
        message = f'No recognized VCS management of source tree "{directory}" - do you need to login to a VCS?'
        for error in errors:
            message += f'\n\tWARNING: {error}'
        raise VCSUnsupported(message)

    return possible_vcs


def detect_vcs(directory, *args, **argv) -> VCS:
    """
    Detects the VCS type for a given directory.
    :param directory: the directory to determine the VCS for
    :return: the VCS type
    """
    possible_vcss = detect_vcss(directory, *args, **argv)
    LOGGER.debug(f'Possible VCSs: {possible_vcss}', possible_vcss)

    if len(possible_vcss) > 1:
        possible_vcss_str = ', '.join([vcs.vcs for vcs in possible_vcss])
        LOGGER.warning(f'WARNING: Multiple VCS matches: {possible_vcss_str}')

    return possible_vcss[0]


try:
    import setuptools.command.egg_info

    # pyline: disable=R0904
    class VCSInfoEggInfo(setuptools.command.egg_info.egg_info):
        """
        Override the egg_info command to appropriately set build tags.
        """

        command_name = 'egg_info'

        def tags(self):
            sourcedir = os.path.dirname(
                os.path.abspath(self.distribution.script_name)
            )

            # first, see if we can get vcs information.
            try:
                vcs = detect_vcs(sourcedir)
                tag_build = f'.{vcs.number}'
                if vcs.modified > 0:
                    tag_build = f'{tag_build}.{vcs.modified}'
                return tag_build
            except TypeError:
                pass
            except VCSUnsupported:
                pass

            # if not fall back to the default routine
            return setuptools.command.egg_info.egg_info.tags(self)


except ImportError:
    pass


# Local Variables:
# fill-column: 100
# End:
