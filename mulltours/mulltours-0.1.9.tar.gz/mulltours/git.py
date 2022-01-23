import logging
import os
import pathlib
import sys
import tempfile
import time

import executor

from mulltours import git


def git_found_ok():
    cmd = [
        "git",
        "--version",
        ">",
        "/dev/null",
    ]
    s = " ".join(cmd)
    executor.execute(s)


def git_init(path):
    cmd = [
        "git",
        "init",
        "--quiet",
    ]
    s = " ".join(cmd)
    executor.execute(s)


def git_commit(path):
    cmd = [
        "git",
        "commit",
        "--quiet",
        "--message",
        "Boilerplate",
    ]
    s = " ".join(cmd)
    executor.execute(s)


def git_add_all(path):
    cmd = [
        "git",
        "add",
        "--all",
    ]
    s = " ".join(cmd)
    executor.execute(s)


def git_init_branch(path):
    cmd = [
        "git",
        "config",
        "init.defaultBranch",
        "master",
    ]
    s = " ".join(cmd)
    executor.execute(s)


def main(path):
    os.chdir(path)
    git.git_found_ok()
    git.git_init(path)
    git.git_init_branch(path)
    git.git_add_all(path)
    git.git_commit(path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{pathlib.Path(__file__).stem}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    path = pathlib.Path(tempfile.gettempdir()) / str(int(time.time()))
    path.mkdir()
    f1 = path / "test.txt"
    open(f1, "w").close()

    logging.debug(path)

    main(path)
