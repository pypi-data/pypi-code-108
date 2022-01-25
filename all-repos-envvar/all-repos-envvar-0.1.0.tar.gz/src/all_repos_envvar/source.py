from all_repos.source import github as base

from .mixin import GitHubEnvMixin


class Settings(GitHubEnvMixin, base.Settings):
    pass


list_repos = base.list_repos
