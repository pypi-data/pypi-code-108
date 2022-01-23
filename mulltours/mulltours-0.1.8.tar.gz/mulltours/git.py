import logging
import os
import pathlib
import subprocess
import sys
from pathlib import Path
from typing import List

import git


def generate_file_list(path) -> List[Path]:
    lst = []
    for p in path.rglob("*"):
        if ".git/" in str(p):
            continue
        logging.debug(p.resolve())
        if not str(p).lower().startswith(".git/"):
            lst.append(p)
    return lst


def git_found_ok():
    cmd = [
        "git",
        "--version",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        outs, errs = proc.communicate(timeout=15)
        logging.debug(outs.decode())
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        logging.warning(errs.decode())

    if errs:
        logging.warning(f"failed to run {' '.join(cmd)}, error: {errs.decode()}")
        return False
    else:
        logging.debug(f"ran ok: {' '.join(cmd)}")
        return True


def git_init(path):
    cmd = [
        "git",
        "init",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        outs, errs = proc.communicate(timeout=15)
        logging.debug(outs.decode())
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        logging.warning(errs.decode())

    if errs:
        logging.warning(f"failed to run {' '.join(cmd)}, error: {errs.decode()}")
        return False
    else:
        logging.debug(f"ran ok: {' '.join(cmd)}")
        return True


def git_commit(path):
    cmd = [
        "git",
        "commit",
        "--message",
        "Boilerplate",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        outs, errs = proc.communicate(timeout=15)
        logging.debug(outs.decode())
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        logging.warning(errs.decode())

    if errs:
        logging.warning(f"failed to run {' '.join(cmd)}, error: {errs.decode()}")
        return False
    else:
        logging.debug(f"ran ok: {' '.join(cmd)}")
        return True


def git_add_all(path):
    cmd = [
        "git",
        "add",
        "--all",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        outs, errs = proc.communicate(timeout=15)
        logging.debug(outs.decode())
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        logging.warning(errs.decode())

    if errs:
        logging.warning(f"failed to run {' '.join(cmd)}, error: {errs.decode()}")
        return False
    else:
        logging.debug(f"ran ok: {' '.join(cmd)}")
        return True


def git_init_branch(path):
    os.chdir(path.resolve())
    cmd = [
        "git",
        "config",
        "init.defaultBranch",
        "master",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        outs, errs = proc.communicate(timeout=15)
        logging.debug(outs.decode())
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        logging.warning(errs.decode())

    if errs:
        logging.warning(f"failed to run {' '.join(cmd)}, error: {errs.decode()}")
        return False
    else:
        logging.debug(f"ran ok: {' '.join(cmd)}")
        return True


def init(path):
    r = git.Repo.init(path)
    return r


def main(path):
    if not git.git_found_ok():
        sys.exit(-1)

    if not git.git_init(path):
        sys.exit(-1)

    if not git.git_init_branch(path):
        sys.exit(-1)

    if not git.git_add_all(path):
        sys.exit(-1)

    if not git.git_commit(path):
        sys.exit(-1)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{pathlib.Path(__file__).stem}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    main()
