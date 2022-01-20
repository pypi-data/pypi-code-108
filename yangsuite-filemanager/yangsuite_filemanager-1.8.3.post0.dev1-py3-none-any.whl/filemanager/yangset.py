# Copyright 2016-2021 Cisco Systems, Inc
from __future__ import unicode_literals

import errno
import json
import os
import traceback
from datetime import datetime

from yangsuite import get_logger, get_path
from .base import _YSYangSetBase
from .repository import YSYangRepository
from .utility import yangset_path, merge_user_set

log = get_logger(__name__)


class YSYangSet(_YSYangSetBase):
    """A Repository containing a specific subset of YANG modules.

    Unlike a pyang.FileRepository or a YSYangRepository, a YSYangSet contains
    specific files, rather than simply providing all YANG files in a given
    directory(s).

    In general use in YANGSuite, a user may have many YSYangSets, all of which
    operate against a given YSYangRepository, but each of which describes a
    different subset of interesting files within that repository.

    Instances of this class are immutable (modules cannot be added to or
    removed from this set once initialized). This is intentional as this class
    is designed for consumption by users (YSContext, etc.). When defining a new
    set or editing an existing set, use the YSMutableYangSet class instead.

    Ways to create a YSYangSet instance:

    - load() - by owner and name (instance saved by YSMutableYangSet.write())
    - from_file() - by path to the file written by YSMutableYangSet.write()
    """

    #
    # Additional public methods and properties
    #

    def __init__(self, owner, setname, modules, repository=None, reponame=None,
                 **kwargs):
        """Create a YSYangSet.

        This should not generally be called directly -- instead, use the
        appropriate constructor API such as load() or from_file().

        Args:
          owner (str): User owning this set definition
          setname (str): Name of this set, for saving/loading purposes.
          modules (list): List of [absfilepath], [module, revision],
            or [module, revision, absfilepath] lists of interest.
          reponame (str): Name of repository to find files in
          repository (str): Slug for repository to find files in
        """
        self.setname = setname
        if reponame and not repository:
            # Assume same owner as yangset
            self.repository = YSYangRepository(owner, reponame)
            self.reponame = self.repository.reponame
        elif repository and not reponame:
            self.repository = YSYangRepository(repository)
            self.reponame = self.repository.reponame
        else:
            raise TypeError("Either repository or reponame must be given")
        super(YSYangSet, self).__init__(owner, modules)

    @property
    def datastore_mtime(self):
        """Datetime when the underlying yangset definition was last changed.

        Note that although the instance is otherwise immutable, a change
        to the underlying JSON file (via YSMutableYangSet) will result
        in a live update to ``self.datastore_mtime``. This is key to the
        ``is_stale`` API.

        If this time exists and is newer than ``self.mtime``, that means that
        this instance has become stale (no longer in sync with the underlying
        yangset and repository definition) and hence ``is_stale`` will be True.
        """
        path = yangset_path(self.owner, self.setname)
        if os.path.exists(path):
            return datetime.utcfromtimestamp(os.stat(path).st_mtime)
        else:
            return None

    @property
    def modules(self):
        """Sorted list of (mod, rev, path) that this YSYangSet contains."""
        return self._modules

    @property
    def slug(self):
        return merge_user_set(self.owner, self.setname)

    @modules.setter
    def modules(self, values):
        """Given various input formats, sanitize to the format pyang wants.

        Note that while a YSYangRepository can contain multiple revisions
        of the same module, a YSYangSet can only contain one revision of any
        given module. RFC 6020, 7.1.5::

            Multiple revisions of the same module MUST NOT be imported

        Args:
          values (list):
            - [(mod, rev, path), (mod, rev, path)] - will be used as-is
            - [(mod, rev), (mod, rev)] - as returned from load();
              paths will be looked up in owner file repository
            - [path, path, path] - as from list_yang_files();
              module/revision will be determined from file name/contents.

        Raises:
          RuntimeError: if trying to change the modules once already set
            (use a YSMutableYangSet if such changes are intended)
          ValueError: if:
            1. any entry in the values list is not understood
            2. multiple revisions of any given module are present
            Note that an error is NOT raised if unable to locate the specified
            module file(s) in the repository. (TODO, should it be?)
        """
        if self._modules:
            raise RuntimeError("YSYangSet modules list is immutable and "
                               "may not be changed once set.")
        if values is None:
            values = []
        modules = []
        module_names = {}
        missing_file_errors = []
        input_errors = []
        multirev_errors = {}
        for item in values:
            name = None
            rev = None
            path = None
            if isinstance(item, str):
                path = item
            else:
                # Not a string - is it a list, tuple, or other iterable?
                try:
                    length = len(item)
                    if length == 3:
                        name, rev, path = item
                        if not name or not rev or not path:
                            raise TypeError
                    elif length == 2:
                        name, rev = item
                        if not name or not rev:
                            raise TypeError
                    else:
                        raise TypeError
                except TypeError:
                    # Dunno what it is, then
                    input_errors.append(str(item))
                    continue

            if rev == 'unknown' or not rev:
                rev = None

            latest_rev = ''
            for n, r, p in self.repository.modules:
                if name and rev and path:
                    break

                if name and n == name:
                    if rev and r == rev:
                        path = p
                        break
                    elif not rev and r >= latest_rev:
                        path = p
                        latest_rev = r
                        # keep going, we might find a newer revision
                elif path and not name and p == path:
                    name = n
                    rev = r
                    break

            if not rev:
                rev = latest_rev

            if not path:
                missing_file_errors.append(name)
                continue
            elif not name or not os.path.isfile(path):
                missing_file_errors.append(str(path))
                continue

            if name in module_names:
                if name not in multirev_errors:
                    # First pair of revisions
                    multirev_errors[name] = [module_names[name], rev]
                else:
                    # A third, fourth, etc. additional revision
                    multirev_errors[name].append(rev)
            modules.append((name, rev, path))
            module_names[name] = rev

        if missing_file_errors:
            # TODO, raise ValueError?
            log.error('The following modules referenced by yangset "{0}" '
                      'were not found in repository "{1}":\n  {2}'
                      .format(self.setname, self.reponame,
                              "\n  ".join(missing_file_errors)))

        if input_errors:
            raise ValueError("Some entries were not understood:\n  {0}"
                             .format("\n  ".join(input_errors)))
        if multirev_errors:
            raise ValueError(
                "YANG set may not contain multiple revisions of the same "
                "module!\n{0}".format(
                    '\n'.join("{0} {1}".format(name, tuple(revs))
                              for name, revs in multirev_errors.items())))
        if not self.mtime:
            self.mtime = datetime.utcnow()
        self._modules = sorted(modules)

    @classmethod
    def load(cls, owner, setname):
        """Load the requested saved yangset.

        Args:
          owner (str): Owner of the named yangset.
          setname (str): Name of the yangset to locate.
        Returns:
          YSYangSet: instance reconstructed from storage.
        Raises:
          OSError: if the given yangset doesn't exist
          ValueError: if parameters are invalid or the yangset is corrupted
        """
        if not owner or not setname:
            raise ValueError("owner and setname parameters must not be empty!")

        if cls.from_file(yangset_path(owner, setname)):
            return cls.from_file(yangset_path(owner, setname))
        else:
            from ysyangtree.yangsettree import get_yangset_tree
            from ysyangtree.models import YangSetTree
            ysettree = get_yangset_tree(owner, setname, [], owner)
            if ysettree and isinstance(ysettree, YangSetTree):
                return cls.from_file(yangset_path(ysettree.user.username,
                                                  ysettree.setname))

    @classmethod
    def delete(cls, owner, setname):
        """Delete the specified yangset.

        Args:
          owner (str): Owner of the named yangset.
          setname (str): Name of the yangset to locate.
        """
        if setname == '':
            raise ValueError("Deleting the user repository implicit yangset"
                             " is not permitted.")
        path = yangset_path(owner, setname)
        if os.path.exists(path):
            os.remove(path)
        else:
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    @classmethod
    def from_file(cls, src):
        """Load the given YangSet descriptor file into a YSYangSet instance.

        Args:
          src (str): Path to yangset descriptor file.
        Raises:
          OSError: if the given file does not exist
          ValueError: if the file is not valid JSON
        """
        if not os.path.exists(src):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), src)
        elif not os.path.isfile(src):
            raise OSError(errno.EINVAL, os.strerror(errno.EINVAL), src)

        try:
            with open(src, 'r') as fd:
                data = json.load(fd)
        except ValueError:   # e.g. json.decoder.JSONDecodeError
            log.debug(traceback.format_exc())
            raise ValueError("Source '{0}' is not a valid JSON file."
                             .format(src))

        result = cls(**data)
        log.info("Loaded %s from %s", result, src)
        return result

    @staticmethod
    def user_yangsets(owner):
        """Get data for all yangsets owned by the given user.

        Args:
          owner (str): Username
        Returns:
          list: [{'name': 'display name', 'slug': 'owner+display-name'}, ...]
        """
        # As of 0.6.0, yangsuite.get_path will auto-create user directories -
        # so we want to make sure the user actually exists before creating it
        if not os.path.isdir(os.path.join(get_path('users_dir'), owner)):
            raise RuntimeError("No such user")
        path = get_path('yangsets_dir', user=owner)
        result = []
        for filename in sorted(os.listdir(path)):
            fpath = os.path.join(path, filename)
            if os.path.isfile(fpath):
                # Get 'un-slugified' set name from file contents
                try:
                    with open(fpath, 'r') as fd:
                        data = json.load(fd)
                    result.append({
                        'name': data['setname'],
                        'slug': merge_user_set(owner, data['setname']),
                    })
                except ValueError:   # e.g. json.decoder.JSONDecodeError
                    log.debug(traceback.format_exc())
                    log.error("Error in loading yangset %s", fpath)
        return sorted(result, key=lambda item: item['name'])

    @staticmethod
    def all_yangsets():
        """Get data about all yangsets for all users.

        Returns:
          dict: {'user1': [{'name': 'Foo', 'slug': 'foo}, {...}], 'user2': ...}
        """
        sets = {}
        usersdir = get_path('users_dir')
        for user in sorted(os.listdir(usersdir)):
            if os.path.isdir(os.path.join(usersdir, user)):
                sets[user] = YSYangSet.user_yangsets(user)
            else:
                log.debug("Skipping non-directory '%s' in %s", user, usersdir)
        return sets

    #
    # Private methods
    #

    def __eq__(self, other):
        """Equality test, overriding _YSYangSetBase logic to add setname check.

        Since we slugify setnames on the back end, two sets may have differing
        name strings and still be equal if their names slugify to the
        same result.
        """
        return (yangset_path(self.owner, self.setname) ==
                yangset_path(other.owner, other.setname) and
                self.modules == other.modules)

    def __repr__(self):
        """String representation"""
        return "YANG set '{0}' owned by '{1}' ({2} modules)".format(
            self.setname, self.owner, len(self.modules))
