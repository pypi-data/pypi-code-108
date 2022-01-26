from __future__ import annotations

import imp
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Dict

import requests
import json

from vectice.utils.ipykernal_hook import notebook_path, get_absolute_path, notebook_name

LOGGER = logging.getLogger("GitVersion")


def _is_git_repo(path: str = ".", search_parent_directories: bool = True) -> bool:
    from git import Repo, InvalidGitRepositoryError

    try:
        Repo(path, search_parent_directories=search_parent_directories)
        return True
    except InvalidGitRepositoryError:
        return False


def _main_is_frozen() -> bool:
    return (
        hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__")  # new py2exe  # old py2exe
    )  # tools/freeze


def _get_executable_path() -> str:
    if _main_is_frozen():
        # print 'Running from path', os.path.dirname(sys.executable)
        return sys.executable
    return sys.argv[0]


def _relative_path(parent_path, child_path) -> str:
    parent_path = Path(os.path.abspath(parent_path))
    child_path = Path(os.path.abspath(child_path))
    try:
        return str(child_path.relative_to(parent_path)).replace("\\", "/")
    except ValueError:
        return str(child_path)


def _extract_git_version(path: str = ".", search_parent_directories: bool = True) -> Optional[GitVersion]:
    try:
        from git import Repo, InvalidGitRepositoryError
    except ModuleNotFoundError:
        return None

    repo = None
    if _check_if_collab():
        try:
            path = get_absolute_path()
            repo = Repo(path=path, search_parent_directories=search_parent_directories)
        except Exception:
            return None

    try:
        if repo is None:
            repo = Repo(path, search_parent_directories=search_parent_directories)
        repository_name = repo.remotes.origin.url.split(".git")[0].split("/")[-1]
        try:
            branch_name = repo.active_branch.name
        except TypeError:
            return None
        commit_hash = repo.head.object.hexsha
        commit_comment = repo.head.object.message
        commit_author_name = repo.head.object.author.name
        commit_author_email = repo.head.object.author.email
        if "ipykernel_launcher.py" in _get_executable_path() and not _check_if_collab():
            entrypoint = _relative_path(os.path.dirname(repo.git_dir), notebook_path())
        # TODO clean up
        elif _check_if_collab():
            entrypoint = get_absolute_path()
            entrypoint = entrypoint.split(str(repo.common_dir).split("/")[-2])[-1]
            entrypoint = entrypoint[1:]
        else:
            entrypoint = _relative_path(os.path.dirname(repo.git_dir), _get_executable_path())
        try:
            repo.active_branch.commit.tree.join(entrypoint)
        except KeyError:
            return None
        is_dirty = repo.is_dirty()
        uri = repo.remotes.origin.url
        return GitVersion(
            repository_name,
            branch_name,
            commit_hash,
            commit_comment,
            commit_author_name,
            commit_author_email,
            is_dirty,
            uri,
            entrypoint,
        )
    except InvalidGitRepositoryError:
        return None


def _extract_github_information_from_uri(uri: str) -> Optional[Tuple[str, str, str]]:
    match = re.search("(?:https://github.com/|git@github.com:)([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)(?:/tree/(.+))?", uri)
    if match:
        return match.group(1), match.group(2), match.group(3)
    else:
        return None


def _extract_bitbucket_cloud_information_from_uri(uri: str) -> Optional[Tuple[str, str, str]]:
    match = re.search("(?:https://bitbucket.org/|git@bitbucket.org:)([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)(?:/src/(.+))?", uri)
    if match:
        return match.group(1), match.group(2), match.group(3)
    else:
        return None


def _extract_gitlab_information_from_uri(uri: str) -> Optional[Tuple[str, str, str]]:
    match = re.search("(?:https://gitlab.com/|git@gitlab.com:)([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)(?:/tree/(.+))?", uri)
    if match:
        return match.group(1), match.group(2), match.group(3)
    else:
        return None


def _create_git_version_from_uri(
    uri: str, script_relative_path: Optional[str] = None, login_or_token=None, password=None, jwt=None
):
    from github import Github

    g = Github(login_or_token=login_or_token, password=password, jwt=jwt)
    result = _extract_github_information_from_uri(uri)
    if result is None:
        return None
    organisation, repository_name, branch = result
    github_repository = g.get_repo(f"{organisation}/{repository_name}")
    if branch is None:
        branch_name = github_repository.default_branch
    else:
        branch_name = branch
    github_branch = github_repository.get_branch(branch_name)
    commit = github_branch.commit
    if github_branch is None:
        raise RuntimeError(f"invalid branch name {branch_name}")
    if script_relative_path and not _is_file_in_git(github_repository, script_relative_path):
        return None
    return GitVersion(
        repository_name,
        branch_name,
        commit.sha,
        commit.commit.message,
        commit.commit.author.name,
        commit.commit.author.email,
        False,
        f"https://www.github.com/{organisation}/{repository_name}",
        script_relative_path,
    )


def _create_bitbucket_version_from_uri(
    uri: str, script_relative_path: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None
):
    from atlassian.bitbucket.cloud import Cloud  # type: ignore

    result = _extract_bitbucket_cloud_information_from_uri(uri)
    if result is None:
        return None
    workspace_name, repository_name, branch = result
    cloud = Cloud(url="https://api.bitbucket.org/", username=username, password=password, cloud=True)
    try:
        workspace = cloud.workspaces.get(workspace_name)
        bit_repository = workspace.repositories.get(repository_name).data
    except Exception as e:
        raise RuntimeError(f"{e}")
    if branch is None:
        branch = bit_repository["mainbranch"]["name"]
    try:
        branches_link = bit_repository["links"]["branches"]["href"]
        response = (
            requests.get(branches_link, auth=(username, password))
            if username and password
            else requests.get(branches_link)
        )
        branches = json.loads(response.text)
        commit = [br for br in branches.get("values") if br.get("name") == branch][0]
    except Exception:
        raise RuntimeError(f"invalid branch name '{branch}'")
    check_file = (
        requests.get(
            f"https://bitbucket.org/{workspace_name}/{repository_name}/full-commit/{commit['target']['hash']}/{script_relative_path}",
            auth=(username, password),
        )
        if username and password
        else requests.get(
            f"https://bitbucket.org/{workspace_name}/{repository_name}/full-commit/{commit['target']['hash']}/{script_relative_path}"
        )
    )
    if check_file.status_code > 200:
        return None
    return GitVersion(
        repository_name,
        branch,
        commit["target"]["hash"],
        commit["target"]["message"],
        commit["target"]["author"]["user"]["display_name"],
        commit["target"]["author"]["raw"],
        False,
        f"https://bitbucket.org/{workspace_name}/{repository_name}/",
        f"{script_relative_path}?at={branch}",
    )


def _create_gitlab_version_from_uri(
    uri: str, script_relative_path: str, private_token: Optional[str] = None, oauth_token: Optional[str] = None
):
    from gitlab import Gitlab

    job_token = os.environ.get("CI_JOB_TOKEN") if os.environ.get("CI_JOB_TOKEN") else None
    glab = Gitlab("https://gitlab.com/", private_token=private_token, oauth_token=oauth_token, job_token=job_token)
    result = _extract_gitlab_information_from_uri(uri)
    if result is None:
        return None
    organisation, repository_name, branch = result
    gitlab_repository = glab.projects.get(f"{organisation}/{repository_name}")
    if branch is None:
        branch_name = gitlab_repository.attributes.get("default_branch")
    else:
        branch_name = branch
    gitlab_branch = gitlab_repository.files.blame(file_path=script_relative_path, ref=branch_name)
    gitlab_file = gitlab_repository.files.get(file_path=script_relative_path, ref=branch_name)
    commit: Dict[str, str] = [
        curr_commit.get("commit")  # type: ignore
        for curr_commit in gitlab_branch
        if curr_commit.get("commit").get("id") == gitlab_file.last_commit_id  # type: ignore
    ][0]
    if gitlab_branch is None:
        raise RuntimeError(f"invalid branch name {branch_name}")
    return GitVersion(
        repository_name,
        branch_name,
        commit["id"],
        commit["message"],
        commit["author_name"],
        commit["author_email"],
        False,
        f"https://www.gitlab.com/{organisation}/{repository_name}",
        script_relative_path,
    )


def _is_file_in_git(github_repository=None, script_relative_path: Optional[str] = None) -> bool:
    if not script_relative_path:
        return False
    elif script_relative_path and github_repository:
        try:
            script_relative_path = script_relative_path.replace("%20", " ")
            github_repository.get_contents(script_relative_path)
        except Exception as e:
            if e.args[0] == 403 and e.args[1].get("errors")[0].get("code") == "too_large":
                return True
            return False
        return True
    else:
        return False


def _check_if_collab():
    try:
        if "fileId" in notebook_name():
            return True
    except Exception:
        return False


@dataclass
class GitVersion:
    repositoryName: str
    branchName: str
    commitHash: str
    commitComment: str
    commitAuthorName: str
    commitAuthorEmail: str
    isDirty: bool
    uri: str
    entrypoint: Optional[str] = None

    @classmethod
    def create(cls, path: str = ".", search_parent_directories: bool = True) -> Optional[GitVersion]:
        code_artifact = _extract_git_version(path, search_parent_directories)
        if code_artifact is None:
            return None
        return code_artifact

    @classmethod
    def create_from_github_uri(
        cls, uri: str, script_relative_path: Optional[str] = None, login_or_token=None, password=None, jwt=None
    ):
        return _create_git_version_from_uri(uri, script_relative_path, login_or_token, password, jwt)

    @classmethod
    def create_from_bitbucket_uri(
        cls,
        uri: str,
        script_relative_path: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        return _create_bitbucket_version_from_uri(uri, script_relative_path, username, password)

    @classmethod
    def create_from_gitlab_uri(
        cls, uri: str, script_relative_path: str, private_token: Optional[str] = None, oauth_token: Optional[str] = None
    ):
        return _create_gitlab_version_from_uri(uri, script_relative_path, private_token, oauth_token)
