from typing import Optional

import click

import grid.sdk.env as env
from grid.sdk.source_code.git import execute_git_command


class WorkflowChecksMixin:
    """Encapsulates workflow checks that prevent users from making mistakes."""
    @staticmethod
    def _check_if_remote_head_is_different() -> Optional[bool]:
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
        is_different = None
        if any('fatal' in f for f in (local_sha, remote_sha, base_sha)):
            return

        is_different = True
        if local_sha in (remote_sha, base_sha):
            is_different = False

        # Prompt user about the Github differences.
        warning_str = click.style('WARNING', fg='yellow')
        if is_different:
            message = f"{warning_str} Local git repository seems to be out-of-sync with GitHub. Continue?"
            if not env.IGNORE_WARNINGS:
                click.confirm(message, abort=True)

        return is_different

    @staticmethod
    def _check_github_repository() -> None:
        """Checks if the active directory is a GitHub repository."""
        github_repository = execute_git_command(["config", "--get", "remote.origin.url"])
        env.logger.debug(github_repository)

        if not github_repository or 'github.com' not in github_repository:
            # TODO - change error message to advertise `--localdir`
            raise click.ClickException(
                '`grid train` or `grid interactive` can only be run in a git repository '
                'hosted on github.com. See docs for details: https://docs.grid.ai'
            )

    @staticmethod
    def _check_if_uncommited_files() -> bool:
        """
        Checks if user has uncommited files in local repository.
        If there are uncommited files, then show a prompt
        indicating that uncommited files exist locally.

        Original solution:

            * https://stackoverflow.com/questions/\
                3878624/how-do-i-programmatically-determine-if-there-are-uncommitted-changes
        """
        files = execute_git_command(['update-index', '--refresh'])

        _files = files.split('\n')
        _files = [click.style(f"  {f.replace(': needs update', '')}", fg='red') for f in _files]

        files_str = '\n    '.join(_files)
        docs_str = click.style('https://docs.grid.ai', fg='blue')
        warning_str = click.style('WARNING', fg='yellow')
        message = f"""

    {warning_str}

    The following files are uncommited. Changes made to these
    files will not be avalable to Grid when running an Experiment.

    {files_str}

    Would you like to continue?

    You can use the flag --ignore_warnings to skip this warning.
    See details at: {docs_str}

   """
        has_uncommitted_files = False
        if files and not env.IGNORE_WARNINGS:
            click.confirm(message, abort=True)
            has_uncommitted_files = True

        return has_uncommitted_files
