# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from contextlib import ContextDecorator
from typing import Optional

from .globals import env
from .lock import vdb_lock


class VDB(ContextDecorator):
    def __init__(self, commit_message: Optional[str] = None):
        # Slow import
        import git

        self.lock = vdb_lock(write=True)
        self.gitrepo = git.Repo.init(env.prefix().INSTALLED_DB)
        self.message = commit_message

    def __enter__(self):
        self.lock.__enter__()
        return self.gitrepo

    def __exit__(self, *exc):
        if self.message is not None:
            self.gitrepo.git.commit(m=self.message)
        self.lock.__exit__()
        return False
