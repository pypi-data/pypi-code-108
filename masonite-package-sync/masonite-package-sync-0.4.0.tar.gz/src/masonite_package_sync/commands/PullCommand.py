import subprocess
import os
import shutil
import tempfile

from cleo import Command

from ..utils import replace_string_in_file


def ignore_files(directory, files):
    import pdb

    pdb.set_trace()


class PullCommand(Command):
    """
    Pull template project into given directory

    pull
        {--directory=? : By default current directory}
        {--repo=MasoniteFramework/cookie-cutter : Repository to pull from}
        {--branch=? : Repository branch to pull from, default is the default from repo}
        {--switch-branch=? : Branch to put modifications from}
        {--exclude=? : Override default files or folders to exclude (separated by ,)}
    """

    EXCLUDE = [
        "tests",
        ".git",
        "README.md",
        ".gitignore",
        ".env-example",
        ".env.testing",
        "craft",
        "makefile",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "setup.cfg",
        "webpack.mix.js",
        "wsgi.py",
    ]

    def handle(self):
        cwd = os.getcwd()
        directory = os.path.abspath(self.option("directory")) or cwd
        repo = self.option("repo")
        branch = self.option("branch")

        switch_branch = self.option("switch-branch")
        excluded_files = self.option("exclude")

        git_clone_args = [
            "git",
            "clone",
            "--depth",
            "1",
            f"https://github.com/{repo}.git",
        ]
        if branch:
            git_clone_args.extend(["-b", branch])
        paths_to_remove = []
        if excluded_files:
            paths_to_remove = excluded_files.split(",")
        else:
            paths_to_remove = self.EXCLUDE

        repo_name = repo.split("/")[-1]
        with tempfile.TemporaryDirectory() as tmp_dir:
            source_dir = os.path.join(tmp_dir, repo_name)
            os.chdir(tmp_dir)
            # Clone into temporary dir
            subprocess.run(git_clone_args, check=True, stdout=subprocess.PIPE).stdout

            # # remove files or folders to ignore
            for path in paths_to_remove:
                abs_path = os.path.join(source_dir, path)
                try:
                    if os.path.isdir(abs_path):
                        shutil.rmtree(abs_path)
                    else:
                        os.remove(abs_path)
                except FileNotFoundError:
                    import pdb

                    pdb.set_trace()
                    pass

            # if all good
            os.chdir(cwd)
            if switch_branch:
                subprocess.run(
                    ["git", "checkout", "-b", switch_branch],
                    check=True,
                    stdout=subprocess.PIPE,
                ).stdout

            # copy all files
            shutil.copytree(source_dir, directory, dirs_exist_ok=True)

        # convert project to work inside given folder
        if directory:
            replace_string_in_file(
                os.path.join(directory, "config/auth.py"),
                "from app.",
                "from tests.integrations.app.",
            )

            replace_string_in_file(
                os.path.join(directory, "databases/seeds/user_table_seeder.py"),
                "from app.",
                "from tests.integrations.app.",
            )

            replace_string_in_file(
                os.path.join(directory, "config/filesystem.py"),
                "storage/",
                "tests/integrations/storage/",
            )

            # Kernel:
            kernel = os.path.join(directory, "Kernel.py")
            tokens = [
                ("from app.", "from tests.integrations.app."),
                (
                    'self.application.bind("config.location", "config")',
                    'self.application.bind("config.location", "tests/integrations/config")',
                ),
                ("app/", "tests/integrations/app/"),
                ("routes/web", "tests/integrations/routes/web"),
                ("resources/", "tests/integrations/resources/"),
                ("databases/", "tests/integrations/databases/"),
                ("templates/", "tests/integrations/templates/"),
            ]
            for search, replace in tokens:
                replace_string_in_file(kernel, search, replace)

        self.line("Pulled !")
