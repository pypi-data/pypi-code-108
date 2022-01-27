from x_scaffold.steps import ScaffoldStep
from github import Github

import os
from ruamel.yaml import YAML

from ..plugin import ScaffoldPluginContext


def init(context: ScaffoldPluginContext):
    context.add_step('github', GithubStep())


def fetch_token(options, context):
    if 'token' in options:
        return options['token']

    host = options.get('host', 'github.com')
    gh_hosts = os.path.expanduser('~/.config/gh/hosts.yml')
    if os.path.exists(gh_hosts):
        yaml = YAML()
        with open(gh_hosts, 'r') as f:
            gh_hosts = yaml.load(f)
        if host in gh_hosts:
            return gh_hosts[host]['oauth_token']
    
    return context.environ.get('GITHUB_TOKEN')


class GithubStep(ScaffoldStep):
    def resolve_fn(self, obj_name, fn_name, context):
        token = fetch_token({}, context)
        g = Github(token)
        return getattr(g, fn_name), False
