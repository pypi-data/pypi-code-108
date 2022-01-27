"""
Copyright 2021 Adobe
All Rights Reserved.

NOTICE: Adobe permits you to use, modify, and distribute this file in accordance
with the terms of the Adobe license agreement accompanying it.
"""

import logging
import os
import vcsinfo

try:
    import P4
except ImportError as err:
    raise vcsinfo.VCSUnsupported(
        "Perforce VCS module requires the P4Python library to be installed."
        # pylint: disable=C0301
        f'  See http://www.perforce.com/perforce/doc.current/manuals/p4script/03_python.html for more details: {err}'
    )


LOGGER = logging.getLogger(__name__)


class VCSPerforce(vcsinfo.VCS):
    """
    Class used to retrieve information about a Perforce managed source tree.
    """
    # pylint: disable=too-many-instance-attributes

    p4_to_vcs_status = {
        'edit': vcsinfo.ST_MOD,
        'integrate': vcsinfo.ST_MOD,
        'add': vcsinfo.ST_ADD,
        'branch': vcsinfo.ST_MOD,
        'move/add': vcsinfo.ST_ADD,
        'delete': vcsinfo.ST_REM,
        'move/delete': vcsinfo.ST_REM,
        # don't know how the below maps
        # ''      : vcsinfo.ST_DEL,
        # ''      : vcsinfo.ST_UNK,
        # ''      : vcsinfo.ST_IGN,
        # ''      : vcsinfo.ST_CLN,
    }

    def __init__(
            self,
            dirname,
            development_path='trunk',
            branches_path='branches',
    ):
        """Constructor"""
        vcsinfo.VCS.__init__(self)
        self._development_path_id = development_path
        self._branches_path_id = branches_path
        self._depot_root = ''

        self.detect_source_root(dirname)
        self.vcs_obj = P4.P4(cwd=self.source_root)
        self.vcs_obj.connect()
        self.client = self.vcs_obj.fetch_client()
        self._map = P4.Map(self.client['View'])
        self._inv_map = self._map.reverse()
        self._branch = None
        LOGGER.debug(f'Matched {self.vcs}: {dirname}')

    def __del__(self):
        """
        Make sure the perforce connection is closed when this object is removed
        """
        if hasattr(self, 'vcs_obj') and self.vcs_obj:
            self.vcs_obj.disconnect()

    def detect_source_root(self, directory):
        """
        Traverse directories to find the perforce source root.
        """
        vcs_obj = None
        try:
            real_directory = os.path.realpath(directory)
            vcs_obj = P4.P4(cwd=real_directory)
            vcs_obj.connect()

            p4_probe = real_directory
            if os.path.isdir(real_directory):
                # Add the '...' because the actual directory may not be
                # mapped, but its contents may be mapped.
                p4_probe = os.path.sep.join((real_directory, '...'))

            mapping = vcs_obj.run("where", p4_probe)[0]

            path_dirs = mapping['path'].split('/')
            depot_path_dirs = mapping['depotFile'].split('/')
            if self._development_path_id in depot_path_dirs:
                dev_path_index = depot_path_dirs.index(
                    self._development_path_id
                )
                pop_idx = dev_path_index - len(depot_path_dirs) + 1
            elif self._branches_path_id in depot_path_dirs:
                branches_path_index = depot_path_dirs.index(
                    self._branches_path_id
                )
                pop_idx = branches_path_index - len(depot_path_dirs) + 2
            else:
                raise TypeError(f"Directory '{real_directory}' not managed by p4 client {self.client}")

            self.source_root = '/'.join(path_dirs[:pop_idx])
            self._depot_root = '/'.join(depot_path_dirs[:pop_idx])

        except P4.P4Exception as exc:
            raise TypeError(f"Directory '{real_directory}' is not managed by p4: {exc}") from exc
        finally:
            if vcs_obj and vcs_obj.connected():
                vcs_obj.disconnect()

    @property
    def upstream_repo(self):
        return self._depot_root

    @property
    def name(self):
        if not self._name:
            dirs = self._depot_root.split('/')
            if self._development_path_id == dirs[-1]:
                self._name = dirs[-2]
            elif self._branches_path_id == dirs[-2]:
                self._name = dirs[-3]
        return self._name

    @property
    def branch(self):
        if not self._branch:
            self._branch = self._depot_root.rsplit('/', maxsplit=1)[-1]
        return self._branch

    @property
    def id(self):
        changes = self.vcs_obj.run(
            "changes",
            "-s",
            "submitted",
            "-m",
            "1",
            self.source_root + '/...',
        )
        vcs_id = None
        if changes:
            vcs_id = changes[0]['change']
        return vcs_id

    @property
    def user(self):
        changes = self.vcs_obj.run(
            "changes",
            "-s",
            "submitted",
            "-m",
            "1",
            self.source_root + '/...',
        )
        vcs_id = None
        if changes:
            vcs_id = changes[0]['user']
        return vcs_id

    def classify_status(self, info_list, status_func):
        """Sort files into status lists."""
        status = ([], [], [], [], [], [], [])

        for info in info_list:
            status[self.p4_to_vcs_status[status_func(info)]].append(info)

        return status

    def status(self):
        status = ([], [], [], [], [], [], [])

        open_file_info = {
            ofi['clientFile']: ofi
            for ofi
            in self.vcs_obj.run("opened", self.source_root + '/...')
        }

        file_map = {
            fmap['clientFile']: fmap
            for fmap
            in self.vcs_obj.run("where", *open_file_info.keys())
        }

        for client_file, change_info in open_file_info.items():
            # pylint: disable=C0301
            source_file = file_map[client_file]['path'][len(self.source_root) + 1:]
            status[self.p4_to_vcs_status[change_info['action']]].append(
                source_file
            )

        return status

    def list_files(self):
        status = ([], [], [], [], [], [], [])

        depot_file_info = {
            ofi['depotFile']: ofi
            for ofi
            in self.vcs_obj.run("files", self.source_root + '/...')
        }

        file_map = {
            fmap['depotFile']: fmap
            for fmap
            in self.vcs_obj.run("where", *depot_file_info.keys())
        }

        for depot_file, change_info in depot_file_info.items():
            # pylint: disable=C0301
            source_file = file_map[depot_file]['path'][len(self.source_root) + 1:]
            status[self.p4_to_vcs_status[change_info['action']]].append(
                source_file
            )

        cur_changeset = self.status()
        source_tree_files = list(
            (set(status[vcsinfo.ST_ADD])
             | set(status[vcsinfo.ST_MOD])
             | set(status[vcsinfo.ST_CLN])
             | set(cur_changeset[vcsinfo.ST_ADD]))
            - set(cur_changeset[vcsinfo.ST_REM])
        )
        source_tree_files.sort()

        return source_tree_files


VCS = VCSPerforce
