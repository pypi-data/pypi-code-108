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
    from mercurial import (
        hg,
        ui,
    )
except ImportError as impe:
    # pylint: disable=C0301
    raise vcsinfo.VCSUnsupported(f'Mercurial VCS module requires mercurial: {impe}')


LOGGER = logging.getLogger(__name__)


class VCSHg(vcsinfo.VCS):
    """Minimal class for querying a source tree managed by Mercurial (Hg)"""

    def __init__(self, dirname):
        vcsinfo.VCS.__init__(self)

        hgui = ui.ui()
        self.detect_source_root(dirname)

        try:
            # pylint: disable=C0301
            self.vcs_obj = hg.repository(hgui, path=self.source_root.encode('utf-8'), create=False)
        except TypeError as err:
            raise TypeError(f'Unable to initialize Hg: {err}') from err
        LOGGER.debug(f'Matched {self.vcs}: {dirname}')

    def detect_source_root(self, dirname):
        """Find the top-most source directory"""
        repo_dir = vcsinfo.search_parent_dirs(dirname, '.hg')
        if not repo_dir:
            raise TypeError(f"Directory '{dirname}' is not managed by hg")
        self.source_root = os.path.dirname(repo_dir)

    @property
    def upstream_repo(self):
        """The location of the up-stream VCS repository."""
        return self.vcs_obj.ui.config(b'paths', b'default')

    @property
    def name(self):
        if not self._name:
            if self.vcs_obj.ui.config(b'paths', b'default'):
                # There's an upstream - use the basename for the name
                # pylint: disable=C0301
                path = self.vcs_obj.ui.config(b'paths', b'default').decode('ascii')
            else:
                # No upstream - the directory is the repo - use the
                # directory basename (without "dot" extensions) as
                # the name.
                path = self.source_root
            self._name = os.path.splitext(os.path.basename(path))[0]
        return self._name

    @property
    def branch(self):
        return self.vcs_obj[b'.'].branch()

    @property
    def id(self):
        return self.vcs_obj[b'.'].hex()

    @property
    def id_short(self):
        return self.id[:6]

    @property
    def number(self):
        return int(self.vcs_obj[b'.'].rev())

    def status(self):
        files = self.vcs_obj.status(ignored=True, clean=True, unknown=True)
        status = []
        for fset in files:
            status.append([f.decode('ascii') for f in fset])
        return status

    def list_files(self):
        status = self.status()
        vcs_files = [f.decode('ascii') for f in
                     set(status[vcsinfo.ST_CLN])
                     | set(status[vcsinfo.ST_ADD])
                     | set(status[vcsinfo.ST_MOD])
                     ]
        vcs_files.sort()
        return vcs_files


VCS = VCSHg
