from x_scaffold.steps import ScaffoldStep
from github import Github, Repository, PullRequest

import os
from ruamel.yaml import YAML

from ..plugin import ScaffoldPluginContext
from ..context import ScaffoldContext
from ..runtime import ScaffoldRuntime
from ..rendering import render_options, render_text


def init(context: ScaffoldPluginContext):
    context.add_step('github_repository', GithubRepoStep())
    context.add_step('github_organization', GithubOrgStep())
    context.add_step('github', GithubStep())


def invokeGH(obj, attribute: str, *args, **kwargs):
    return getattr(obj, attribute)(*args, **kwargs)


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


class GithubOrgStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        options = render_options(step, context)
        name = options['name']
        token = fetch_token(options, context)
        g = Github(token)
        org = g.get_organization(name)
        context.set_step(step['__id'], org)
        gh_steps = options.get('steps', [])
        gh_step: dict
        for gh_step in gh_steps:
            for k, v in gh_step.items():
                if 'if' in gh_step:
                    if render_text(gh_step['if']) == False:
                        break
                if k not in ['id', 'if']:
                    result = invokeGH(org, k, **v)
                    if 'id' in gh_step:
                        context.set_step(gh_step['id'], result)
        return org


class GithubStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        options = render_options(step, context)
        token = fetch_token(options, context)
        g = Github(token)
        context.set_step(step['__id'], g)
        gh_steps = options.get('steps', [])
        for gh_step in gh_steps:
            for k, v in gh_step.items():
                if k in ['id', 'if']:
                    continue
                result = invokeGH(g, k, **v)
                if 'id' in gh_step:
                    context.set_step(gh_step['id'], result)
                break
        return g


# https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html
class GithubRepoStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        options = render_options(step, context)
        name = options['name']
        token = fetch_token(options, context)
        g = Github(token)
        repo = g.get_repo(name)
        context.set_step(step['__id'], repo)
        gh_steps = options.get('steps', [])

        for gh_step in gh_steps:
            for k, v in gh_step.items():
                if k in ['id', 'if']:
                    continue
                if 'set_topics' in gh_step:
                    result = self.set_topics(repo, gh_step['set_topics'], context)
                elif 'add_topics' in gh_step:
                    result = self.add_topics(repo, gh_step['add_topics'], context)
                elif 'branch' in gh_step:
                    result = self.run_branch(repo, gh_step['branch'], context)
                else:
                    result = invokeGH(repo, k, **v)
                if 'id' in gh_step:
                    context.set_step(gh_step['id'], result)
                break
        return repo

    def run_branch(self, repo: Repository, step, context):
        name = step['name']
        branch = repo.get_branch(name)
        gh_steps = step.get('steps', [])
        for gh_step in gh_steps:
            for k, v in gh_step.items():
                invokeGH(branch, k, **v)
        return branch
    
    def set_topics(self, repo: Repository, step, context):
        new_topics = step
        repo.replace_topics(new_topics)

    def add_topics(self, repo: Repository, step, context):
        topics = repo.get_topics()
        new_topics = step
        for topic in new_topics:
            if topic not in topics:
                topics.append(topic)
        repo.replace_topics(topics)
    
    def create_pr(self, repo: Repository, step, context):
        opts = render_options(step, context)
        pr: PullRequest.PullRequest = repo.create_pull(**opts)
        context['pr'] = {
            'number': pr.number,
            'url': pr.html_url
        }
    
    def create(self, name: str, github: Github, step, context):
        opts = render_options(step, context)
        parts = name.split('/')
        organization = parts[0]
        name = parts[1]

        github.get_organization(organization).create_repo(name=name, **opts)
