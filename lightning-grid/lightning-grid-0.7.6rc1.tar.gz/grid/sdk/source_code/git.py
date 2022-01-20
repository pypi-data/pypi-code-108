from pathlib import Path
import subprocess
from typing import List, Union

import grid.sdk.env as env


def execute_git_command(args: List[str], cwd=None) -> str:
    """
    Executes a git command. This is expected to return a
    single string back.

    Returns
    -------
    output: str
        String combining stdout and stderr.
    """
    process = subprocess.run(['git'] + args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             cwd=None,
                             check=False)

    output = process.stdout.strip() + process.stderr.strip()
    return output


def check_if_remote_head_is_different() -> Union[bool, None]:
    """
    Checks if remote git repository is different than
    the version available locally. This only compares the
    local SHA to the HEAD commit of a given branch. This
    check won't be used if user isn't in a HEAD locally.

    Original solution:

        * https://stackoverflow.com/questions/\
            3258243/check-if-pull-needed-in-git
    """
    # Check SHA values.
    local_sha = execute_git_command(['rev-parse', '@'])
    remote_sha = execute_git_command(['rev-parse', r"@{u}"])
    base_sha = execute_git_command(['merge-base', '@', r"@{u}"])

    # Whenever a SHA is not avaialble, just return.
    if any('fatal' in f for f in (local_sha, remote_sha, base_sha)):
        return None

    is_different = True
    if local_sha in (remote_sha, base_sha):
        is_different = False

    return is_different


def _check_github_repository() -> None:
    """Checks if the active directory is a GitHub repository."""
    github_repository = execute_git_command(["config", "--get", "remote.origin.url"])

    if not github_repository or 'github.com' not in github_repository:
        # TODO - change error message to advertise `--localdir`
        raise RuntimeError(
            '`grid train` or `grid interactive` can only be run in a git repository '
            'hosted on github.com. See docs for details: https://docs.grid.ai'
        )


def check_if_uncommited_files() -> bool:
    """
    Checks if user has uncommited files in local repository.
    If there are uncommited files, then show a prompt
    indicating that uncommited files exist locally.

    Original solution:

        * https://stackoverflow.com/questions/3878624/how-do-i-programmatically-determine-if-there-are-uncommitted-changes
    """
    files = execute_git_command(['update-index', '--refresh'])
    return bool(files)


def add_git_root_path(file: Union[str, Path]) -> str:
    #  Finds the relative path of the file to train.
    abs_path = Path(file).absolute()
    repository_path = execute_git_command(['rev-parse', '--show-toplevel'], cwd=abs_path)
    return str(abs_path.relative_to(repository_path))


def check_github_repository() -> None:
    """Checks if the active directory is a GitHub repository."""
    github_repository = execute_git_command(["config", "--get", "remote.origin.url"])
    env.logger.debug(github_repository)

    if not github_repository or 'github.com' not in github_repository:
        # TODO - change error message to advertise `--localdir`
        raise ValueError(
            '`grid train` or `grid interactive` can only be run in a git repository '
            f'hosted on github.com. found remote origin url={github_repository}. '
            f'See docs for details: https://docs.grid.ai'
        )
