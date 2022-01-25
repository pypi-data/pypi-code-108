import logging

log = logging.getLogger(__name__)


class GitError(Exception):
    pass


class GitLogError(GitError):
    pass


class EmptyLogError(GitError):
    pass


class CommitParseError(GitError):
    pass
