#!/usr/bin/env python

from argparse import ArgumentParser, Namespace
import os
from pathlib import Path
from typing import List, Optional, Union

from github import Github


class ProjectInitializer:
    """ProjectInitializer.
    """

    parser: ArgumentParser
    args: Namespace
    github_token: str
    repo_name: str

    def __init__(self) -> None:
        """Initializes the cli parser, reads args and validates them.
        """
        self.init_parser()

        self.args = self.parser.parse_args()
        self.args.path = Path(
                self.args.path or os.environ.get("PROJECTS") or os.getcwd()
                )

        self.validate()

    def init_parser(self) -> None:
        """Initializes the command line tool
        """
        self.parser = ArgumentParser(
            prog="proj_init",
            description="Automate your workflow with proj_init command."
        )
        self.parser.add_argument(
            "-l",
            "--local",
            dest="local",
            action="store_true",
            help="Creates your repo only locally.",
        )
        self.parser.add_argument(
            "-p",
            "--private",
            dest="private",
            action="store_true",
            help="Creates your repo in private mode.",
        )
        self.parser.add_argument(
            "-d",
            "--directory",
            dest="path",
            action="store",
            help="Path where the repo is going to be created.",
        )
        self.parser.add_argument(
            "repo_name",
            metavar="<repo_name>",
            help="Name of your repo to be created."
        )

    def validate(self) -> None:
        """Validates the input.

        Raises:
            AssertionError: LOCAL and PRIVATE can't be used at same time.
            NameError: Duplicated repos.
        """
        if self.args.local == self.args.private is True:
            raise AssertionError(
                    "LOCAL and PRIVATE can't be used at same time."
                    )

        if (self.args.path/self.args.repo_name).is_dir():
            raise NameError(
                "A directory with this name already exists! Please, try another name."  # noqa
            )

    def create_github_repo(
            self, repo_name: str, private: Optional[bool] = False
            ) -> None:
        """Creates Github repo, public or private.

        Args:
            repo_name (str): Name of the Github repo.
            private (Optional[bool]): Private or not. Defaults to False.
        """
        repo_name_git = repo_name.replace(" ", "-")

        self.github_client = Github(self.github_token)
        print("Github authenticated successfully.")

        user = self.github_client.get_user()
        user.create_repo(repo_name_git, private=private)
        print("Github repo created successfully.")

        self.repo_link = f"https://github.com/{user.login}/{repo_name_git}.git"

    def create_local_repo(self, repo_name: str, path: Path) -> None:
        """Create a local repo.

        Args:
            repo_name (str): Name of repo to be created
            path (Path): Path of the repo
        """
        print(f'Creating "{repo_name}" in "{path.absolute()}"')
        os.mkdir(path/repo_name)
        os.chdir(path/repo_name)

        os_type = {
            "posix": ["touch README.md", "touch .gitignore"],
            "nt": ["cd.> README.md", "cd.> .gitignore"],
        }

        commands = os_type[os.name] + [
            "git init",
            "git add .",
            'git commit -m "Initial commit"',
        ]

        self.run_commands(commands)

    def sync_repos(self) -> None:
        """Syncs the repo with remote.
        """

        sync_commands = [
            f"git remote add origin {self.repo_link}",
            "git branch -M main",
            "git push -u origin main",
        ]

        self.run_commands(sync_commands)

    def open_editor(self) -> None:
        """Open the editor of choice.
        """

        self.run_commands(f"{os.environ.get('EDITOR')} .")

    def run(self) -> None:
        """Run cli tool.
        """
        if not self.args.local:
            self.github_token = os.environ.get("GIT_AUTOMATION")
            self.create_github_repo(self.args.repo_name, self.args.private)

        self.create_local_repo(self.args.repo_name, self.args.path)

        if not self.args.local:
            self.sync_repos()
            print("Git repository created and synced successfully!")
            print(self.repo_link)
        else:
            print("Git repository created successfully!")

    @staticmethod
    def run_commands(*commands: Union[List[str], str]) -> None:
        """Runs the commands on shell.

        Args:
            *commands (Union[List[str], str]): Commands or list of commands.
        """
        for command in commands:
            if isinstance(command, str):
                os.system(command)
            elif isinstance(command, list):
                for com in command:
                    os.system(com)


def proj_init() -> None:
    """Starts the tool.
    """
    ProjectInitializer().run()


if __name__ == "__main__":
    proj_init()
