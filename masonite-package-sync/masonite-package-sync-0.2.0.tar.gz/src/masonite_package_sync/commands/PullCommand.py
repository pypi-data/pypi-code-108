import subprocess
import os
import shutil
import tempfile

from cleo import Command


class PullCommand(Command):
    """
    Pull template project into given directory

    pull
        {--directory=? : By default current directory}
        {--repo=MasoniteFramework/cookie-cutter : Repository to pull from}
        {--branch=? : Repository branch to pull from, default is the default from repo}
        {--switch-branch=patch/package-sync : Branch to put modifications from}
        {--exclude=? : Override default files or folders to exclude (separated by ,)}
    """

    EXCLUDE = [
        "tests",
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

            # remove files or folders to ignore
            for path in paths_to_remove:
                abs_path = os.path.join(source_dir, path)
                try:
                    if os.path.isdir(abs_path):
                        shutil.rmtree(abs_path)
                    else:
                        os.remove(abs_path)
                except FileNotFoundError:
                    pass

            # if all good
            os.chdir(cwd)
            subprocess.run(
                ["git", "checkout", "-b", switch_branch],
                check=True,
                stdout=subprocess.PIPE,
            ).stdout

            # copy all files
            shutil.copytree(source_dir, directory, dirs_exist_ok=True)

        self.line("Pulled !")
