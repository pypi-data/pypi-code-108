import os
import yaml

from github import Github, Repository, PullRequest


class GitContext(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__ = self


def fetch_token(host, options, context):
    if 'token' in options:
        return options['token']

    gh_hosts = os.path.expanduser('~/.config/gh/hosts.yml')
    if os.path.exists(gh_hosts):
        with open(gh_hosts, 'r') as f:
            gh_hosts = yaml.load(f, Loader=yaml.FullLoader)
        if host in gh_hosts:
            return gh_hosts[host]['oauth_token']
    
    return context.environ.get('GITHUB_TOKEN')


# def create_repo():
#     token = fetch_token(host, options, context)
#     g = Github(token)
#     org = g.get_organization(name)


# def clone_new_branch():
#     pass


# def new_pr():
#     pass
