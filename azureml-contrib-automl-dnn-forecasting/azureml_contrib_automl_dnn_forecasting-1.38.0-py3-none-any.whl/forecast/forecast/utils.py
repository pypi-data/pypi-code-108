"""Utilities to facilitate experiment logging and reproducible training."""

import datetime as dt
import json
import os
import os.path as osp
import shutil

import git


def log_repo_status(path: str) -> None:
    """Logs a repo's state to file, persists a diff for any changed files, and copies any untracked files.

    Parameters
    ----------
    path: str
        The path at which all logged information should be persisted.

    Returns
    -------
    None

    """
    repo = git.Repo(search_parent_directories=True)
    d = {}

    # get the commit hash. this should always be available.
    d['commit_hash'] = repo.head.object.hexsha

    # get the branch name
    # this is only available if on a branch's head (not detached)
    try:
        d['branch_name'] = repo.active_branch.name
    except TypeError:
        pass

    # write the metadata
    with open(osp.join(path, 'meta.json'), 'w') as f:
        json.dump(d, f)

    # if dirty,
    dirty = repo.is_dirty()
    if dirty:
        # get & write the diff
        with open(osp.join(path, 'patch.diff'), 'w') as f:
            f.write(repo.git.diff())

    # get all untracked files
    if repo.untracked_files:
        for fname in repo.untracked_files:
            # create the directory in which they'll be copied
            # need to also worry about nesting within path/untracked resulting from nesting in repo
            out_fname = osp.join(path, 'untracked', fname)
            os.makedirs(osp.dirname(out_fname), exist_ok=True)
            shutil.copy2(osp.join(repo.working_dir, fname),
                         out_fname)


def create_timestamped_dir(base_path: str) -> str:
    """Creates a uniquely named directory in the form YYYY-MM-DD_HHMMSS (and appends with _i to ensure uniqueness).

    Do not use in a concurrent setting as this is not safe for parallel execution.

    Parameters
    ----------
    base_path: str
        The path in which the directory should be created

    Returns
    -------
    str
        The path of the newly created directory

    """
    append = 0
    while True:
        try:
            out_dir = osp.join(base_path, dt.datetime.now().strftime("%Y-%m-%d_%H%M%S"))
            if append:
                out_dir += f'_{append}'
            os.makedirs(out_dir)
            break
        except FileExistsError:
            append += 1
    return out_dir


class EarlyTerminationException(Exception):
    """An exception that is used to prematurely brake out of a training loop."""

    pass
