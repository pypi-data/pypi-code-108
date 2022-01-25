# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Parse git commit messages."""

# import logging
import os
from typing import Any, List, Optional

from pygit2 import (
    GIT_OBJ_COMMIT,
    Commit,
    Repository,
    RemoteCallbacks,
    Signature,
    Tag,
    UserPass
)

from versioning.exception import PromanVersioningException


class Git:
    """Provide settings for git repositories."""

    def __init__(self, repo: Repository) -> None:
        """Initialize git object."""
        self.repo = repo
        self.hooks_dir = os.path.join(self.repo.path, 'hooks')
        self.config = os.path.join(self.repo.path, 'config')

    @property
    def username(self) -> str:
        """Return username from git configuration."""
        usernames = list(self.repo.config.get_multivar('user.name'))
        if usernames == []:
            raise PromanVersioningException('git user.name not configured')
        return usernames[-1]

    @property
    def email(self) -> str:
        """Return email from git configuration."""
        emails = list(self.repo.config.get_multivar('user.email'))
        if emails == []:
            raise PromanVersioningException('git user.email not configured')
        return emails[-1]

    @property
    def repo_dir(self) -> str:
        """Return directory of repository."""
        return self.repo.path

    @property
    def working_dir(self) -> str:
        """Return working directory of project."""
        return os.path.abspath(os.path.join(self.repo_dir, '..'))

    @property
    def ref(self) -> str:
        """Retrieve the current reference."""
        return self.repo.head.name

    def add_remote(
        self,
        name: str,
        url: str,
        fetch: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Add remote."""
        if name not in [x.name for x in self.repo.remotes]:
            if fetch is None:
                fetch = f"+refs/heads/*:refs/remotes/{name}/*"
            self.repo.remotes.create(name, url, fetch)
        elif self.repo.remotes[name].url != url:
            self.repo.remotes.set_url(name, url)
        print('huh', self.repo.remotes[name].credentials)

    def commit(
        self,
        branch: Optional[str] = None,
        filepaths: List[str] = [],
        **kwargs: Any,
    ) -> Optional[Commit]:
        """Create commit."""
        ref = f"refs/heads/{branch}" if branch else self.ref

        author = Signature(self.username, self.email)
        committer = kwargs.get('commiter', author)
        message = kwargs.get('message', 'ci: bump version')

        # populate index
        index = self.repo.index
        if filepaths == []:
            index.add_all()
        else:
            for filepath in filepaths:
                index.add(
                    os.path.relpath(
                        filepath, os.path.join(self.repo.path, '..')
                    )
                )
        index.write()
        tree = index.write_tree()

        # get parent
        parents = kwargs.get('parents', [self.repo.head.target])
        encoding = kwargs.get('encoding', 'utf-8')

        # commit
        if not kwargs.get('dry_run', False):
            commit = self.repo.create_commit(
                ref,
                author,
                committer,
                message,
                tree,
                parents,
                encoding,
            )
            return commit
        # TODO: should a mock commit be created?
        return None

    def tag(
        self, name: str, branch: Optional[str] = None, **kwargs: Any
    ) -> Optional[Tag]:
        """Create tag."""
        ref = f"refs/heads/{branch}" if branch else self.ref
        commit = self.repo.resolve_refish(ref)[0]
        oid = commit.hex
        kind = kwargs.get('kind', GIT_OBJ_COMMIT)

        # XXX: regression from GitPython, signature not available here
        signature = kwargs.get('signature', commit.signature)
        message = kwargs.get('message', f"ci: {name}")
        if not kwargs.get('dry_run', False):
            tag = self.repo.create_tag(name, oid, kind, signature, message)
            return tag
        # TODO: should a mock tag be created?
        return None

    def push(
        self,
        branch: Optional[str] = None,
        remote: str = 'origin',
        remote_branch: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Push commited changes."""
        # TODO: feels like remote should be encapsulated with creds
        remote_branch = remote_branch or branch or self.ref.split('/')[-1]
        # ref = f"refs/heads/{branch}" if branch else self.ref
        # remote_ref = f"refs/remotes/{remote}/{remote_branch}"
        # print(ref, remote_ref)

        remote_repo = self.repo.remotes[remote]
        credentials = UserPass(username, password)
        remote_repo.credentials = credentials

        callbacks = RemoteCallbacks(credentials=credentials)
        remote_repo.push([f'refs/heads/{branch}'], callbacks=callbacks)
