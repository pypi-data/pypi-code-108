# Copyright 2016 Cisco Systems, Inc
from __future__ import unicode_literals

import json
import os
import shutil
import traceback
from datetime import datetime

from yangsuite import get_logger, get_path
from .dir_repository import YSYangDirectoryRepository
from .utility import (
    module_listing, repository_path, list_yang_files, migrate_yang_files,
    merge_user_set, split_user_set
)

log = get_logger(__name__)


class YSYangRepository(YSYangDirectoryRepository):
    """A collection of YANG modules in a directory managed by YANG Suite.

    Note: a YSYangRepository instance's ``modules`` parameter is updated when
    calling add_yang_files() and remove_modules() on this instance, but is
    otherwise *not* updated once instantiated.
    """

    def __init__(self, *args):
        """Get the given file repository for the given user.

        Args:
          *args: Either (repository_slug) or (owner, reponame)
        Returns:
          YSYangRepository: yangset with name = reponame, modules = contents of
            repository.
        """
        if len(args) == 1:
            owner, reponame = split_user_set(args[0])
        elif len(args) == 2:
            owner = args[0]
            reponame = args[1]
        else:
            raise TypeError("Between 1 and 2 args are required, not {0}"
                            .format(len(args)))

        self.reponame = reponame
        repodir = repository_path(owner, reponame)
        repofile = self._repository_file_path(owner, reponame)
        data = None
        if os.path.exists(repofile):
            try:
                with open(repofile, 'r') as fd:
                    data = json.load(fd)
            except ValueError:   # e.g. json.decoder.JSONDecodeError
                log.debug(traceback.format_exc())
                raise ValueError("Repofile {0} is not a valid JSON file."
                                 .format(repofile))

            if 'reponame' in data:
                assert repository_path(owner, data['reponame']) == repodir
                self.reponame = data['reponame']

        super(YSYangRepository, self).__init__(repodir, owner,
                                               assume_correct_name=True)

    def __repr__(self):
        """String representation."""
        return "YANG repository '{0}' owned by '{1}' ({2} modules)".format(
            self.reponame, self.owner, len(self.modules))

    @property
    def datastore_mtime(self):
        """Datetime when the repo contents on disk were last changed.

        If this time exists and is newer than ``self.mtime``, that means that
        this instance has become stale (no longer in sync with the underlying
        datastore) and hence ``is_stale`` will be True.
        """
        repofile = self._repository_file_path(self.owner, self.reponame)
        if os.path.exists(repofile):
            return datetime.utcfromtimestamp(os.stat(repofile).st_mtime)
        else:
            return None

    @property
    def slug(self):
        return merge_user_set(self.owner, self.reponame)

    def associated_yangsets(self, cls=None):
        """Set of YANG sets referencing this repository."""
        if not cls:
            from .yangset import YSYangSet
            cls = YSYangSet
        repo_yangsets = []
        for data in cls.user_yangsets(self.owner):
            try:
                ys = cls.load(self.owner, data['name'])
            except:
                log.warning("Unable to load yangset %s", data['slug'])
                log.debug(traceback.format_exc())
            else:
                if ys.repository == self:
                    repo_yangsets.append(ys)
        return repo_yangsets

    @staticmethod
    def user_repos(owner):
        """Get the list of repo data for the given user.

        Args:
          owner (str): Username
        Returns:
          list: [{'name': 'reponame', 'slug': 'owner+reponame'}, ...]
        """
        # As of 0.6.0, yangsuite.get_path will auto-create user directories -
        # so we want to make sure the user actually exists before creating it
        if not os.path.isdir(os.path.join(get_path('users_dir'), owner)):
            raise RuntimeError("No such user")
        path = get_path('repositories_dir', user=owner)
        result = []
        for f in sorted(os.listdir(path)):
            fdir = os.path.join(path, f)
            if os.path.isdir(fdir):
                fpath = os.path.join(fdir, f + ".json")
                if os.path.isfile(fpath):
                    try:
                        with open(fpath, 'r') as fd:
                            data = json.load(fd)
                        result.append({
                            'name': data['reponame'],
                            'slug': merge_user_set(
                                owner, data['reponame']),
                        })
                    except ValueError:   # e.g. json.decoder.JSONDecodeError
                        log.debug(traceback.format_exc())
                        log.error("Error in loading repository %s", f)
        return sorted(result, key=lambda item: item['name'])

    @staticmethod
    def all_repos():
        """Get all repositories for all users.

        Returns:
          dict : {'user1': [{repodata}, {repodata}], 'user2': ...}
            Users who have no repositories yet created will be omitted.
        """
        repos = {}
        usersdir = get_path('users_dir')
        for user in sorted(os.listdir(usersdir)):
            if os.path.isdir(os.path.join(usersdir, user)):
                userrepos = YSYangRepository.user_repos(user)
                if userrepos:
                    repos[user] = userrepos
            else:
                log.debug("Skipping non-directory '%s' in %s", user, usersdir)
        return repos

    def write(self):
        """Create json file with the actual (non-slugified) repo name, etc."""
        data = {
            'reponame': self.reponame,
            'owner': self.owner,
        }

        with open(self._repository_file_path(self.owner, self.reponame),
                  'w') as fd:
            json.dump(data, fd, indent=2)
        # We're up to date!
        self.mtime = self.datastore_mtime

    @classmethod
    def create(cls, owner, reponame):
        """Create a new repository and return it."""
        path = repository_path(owner, reponame)
        if os.path.exists(path):
            raise OSError("Owner '{0}' repository '{1}' already exists",
                          owner, reponame)
        os.makedirs(path)
        result = cls(owner, reponame)
        result.write()
        log.info("Created YANG repository %s", result)
        return result

    @classmethod
    def delete(cls, owner, reponame):
        """Delete the specified repository.

        Args:
          owner (str): Owner of the named repository.
          reponame (str): Name of the repository to delete.

        Raises:
          ValueError: if invalid parameters are specified
          OSError: if the specified repository doesn't exist.
          RuntimeError: if the repository cannot be deleted at this time.
        """
        if not owner or not reponame:
            raise ValueError("User and repository names must be specified")
        repo = YSYangRepository(owner, reponame)

        # Do we have any yangsets associated with this repository?
        repo_setnames = [ys.setname for ys in repo.associated_yangsets()]

        # For now, we just fail if any such yangsets exist - in future we
        # could add a 'force' option, or even delete the yangsets as well.
        # Note that this is not necessarily fatal to the yangsets - they can
        # be reassigned to a different repository if the user wants to use them
        if repo_setnames:
            raise RuntimeError(
                "Unable to delete repository '{0}' because the following "
                "YANG sets currently reference this repository: {1}"
                .format(repo.reponame, repo_setnames))

        path = repo.path
        # Don't need to check os.path.isdir(path) or similar since the
        # YSYangRepository() above already checked that for us.
        shutil.rmtree(path)
        log.info("Deleted YANG repository %s", repo)

    def add_yang_files(self, src_path, remove=True, include_subdirs=False):
        """Add the YANG file(s) from the given source to this repository.

        Args:
          src_path (str): File or directory to copy from.
          remove (bool): If True (default), delete the files from src_path
            after copying them to the repository.
          include_subdirs (bool): If False (default), only get files from
            the src_path directory itself; if True, get files from any
            subdirectories of src_path as well.

        Returns:
          dict: {'added': [list of (module, revision) added to repository],
                 'updated': [list of (module, rev) updated in repository],
                 'unchanged': [list of (module, rev) already in repository],
                 'errors': [list of (filename, error message)]}
        """
        result = migrate_yang_files(src_path, self.path, remove=remove,
                                    include_subdirs=include_subdirs)
        # Refresh modules list
        self._modules = module_listing(list_yang_files(self.path),
                                       assume_correct_name=True)
        if result['added'] or result['updated']:
            self.write()

        # Update the modification time of any yangsets that use
        # any of the updated modules. Added/unchanged modules are ignored.
        from .mutableyangset import YSMutableYangSet
        for ys in self.associated_yangsets(cls=YSMutableYangSet):
            for name, revision, _ in ys.modules:
                if (name, revision) in result['updated']:
                    ys.write()
                    break

        return result

    def remove_modules(self, modules):
        """Remove the specified modules from this repository.

        Args:
          modules (list): of ['name', 'rev']
        Returns:
          dict: {'deleted': [(name, rev), (name, rev)],
                 'module_errors': [(name, rev, error), (name, rev, error)],
                 'yangset_errors': [(setname, error), (setname, error)]}
        """
        result = {'deleted': [], 'module_errors': [], 'yangset_errors': []}

        yangsets = self.associated_yangsets()
        yangset_errors = {}

        for name, rev in modules:
            if rev != 'unknown':
                path = os.path.join(self.path,
                                    "{0}@{1}.yang".format(name, rev))
            else:
                path = os.path.join(self.path,
                                    "{0}.yang".format(name))
            if not os.path.isfile(path):
                result['module_errors'].append((name, rev, "File not found"))
                continue
            ys_users = [ys for ys in yangsets
                        if (name, rev, path) in ys.modules]
            if ys_users:
                for ys in ys_users:
                    if ys.setname not in yangset_errors:
                        yangset_errors[ys.setname] = []
                    yangset_errors[ys.setname].append((name, rev))
                continue
            try:
                os.remove(path)
                result['deleted'].append((name, rev))
            except OSError as e:
                result['module_errors'].append((name, rev, str(e)))

        for setname, errors in yangset_errors.items():
            result['yangset_errors'].append((setname, errors))

        # Refresh modules list
        self._modules = module_listing(list_yang_files(self.path),
                                       assume_correct_name=True)
        if result['deleted']:
            self.write()
        return result

    #
    # Private methods
    #

    @staticmethod
    def _repository_file_path(owner, reponame):
        """Path to JSON file inside the repository with additional metadata."""
        dirpath = repository_path(owner, reponame)
        filename = os.path.basename(dirpath) + ".json"
        return os.path.join(dirpath, filename)
