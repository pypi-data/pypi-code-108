from .base_backend import GitBackend
from subprocess import run
from contextlib import contextmanager
from pathlib import Path
import click
import json
import os
from making_with_code_cli.styles import (
    confirm,
)

@contextmanager
def cd(path):
    """Sets the cwd within the context
    """
    origin = Path().resolve()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)

# TODO: Update to use deploy keys!
class GithubBackend(GitBackend):
    """A Github backend. Students own their own repos and grant teachers access via token.
    Note that this gives the teacher account access to the student's entire github account, 
    within scope.
    """

    def init_clone(self, module, modpath):
        url = module["repo_url"]
        cmd = f'gh repo clone "{url}" "{modpath.name}"'
        with cd(modpath.parent):
            run(cmd, shell=True, check=True)

    def init_create_from_template(self, module, modpath):
        """Creates the named repo from a template, or clones an existing repo with. 
        """
        repo_name = modpath.name
        if self.user_has_repo(repo_name):
            cmd = f'gh repo clone "{repo_name}" "{modpath.name}"'
        else:
            url = module["repo_url"]
            cmd = f'gh repo create "{repo_name}" --clone --private --template "{url}"'
        with cd(modpath.parent):
            run(cmd, shell=True, check=True)

    def user_has_repo(self, name):
        "Checks to see whether the user already has the named repo."
        cmd = f"gh repo list --json name --limit 10000"
        result = run(cmd, shell=True, capture_output=True, text=True).stdout
        repo_names = [obj['name'] for obj in json.loads(result)]
        return name in repo_names
