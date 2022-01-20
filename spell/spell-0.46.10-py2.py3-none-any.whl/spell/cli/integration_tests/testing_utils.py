from contextlib import contextmanager
from builtins import str
import os
import re
import time

import sh
from sh import git


def verify_exit_code(result, code=0):
    if result.exit_code != code:
        print("UNEXPECTED EXIT CODE! Output:", result.output)
        print("just for testing: ", result.__dict__)
    assert result.exit_code == code


def parse_raw(text):
    """return a tuple of tuples for the commas separated value lines in result.output"""
    return tuple(tuple(row.split(",")) for row in text.strip().split("\n"))


def parse_run_id(log_text):
    m = re.search(r"Casting spell #(\d+)", log_text)
    return m.group(1)


def parse_workflow_id(log_text):
    m = re.search(r"Casting workflow #(\d+)", log_text)
    return m.group(1)


def parse_hypersearch_id(log_text):
    m = re.search(r"Casting hyperparameter search #(\d+)", log_text)
    return m.group(1)


def wait_for_run_complete(run_id, run_func):
    # wait until the run completes, a max of 50*6s = 5m
    for i in range(100):
        result = run_func(["ps", "--raw"])
        verify_exit_code(result, 0)
        vals = parse_raw(result.output)
        for val in vals:
            if val[0] == run_id and ("Complete" in val[3] or "Failed" in val[3]):
                return
        time.sleep(6)
    else:
        assert False, "Run {} did not Complete in a timely fashion, PS returns: {}".format(
            run_id, parse_raw(run_func(["ps", "--raw"]).output)
        )


def verify_user_exit_code(run_id, run, desired_code=0):
    found_line = False
    for val in parse_raw(run(["ps", "--raw"]).output):
        if val[0] == run_id:
            found_line = True
            m = re.search(r"Complete \((\d+)\)", val[3])
            if m is None:
                assert False, "Run {} did not complete successfully: {}".format(run_id, val[3])
            found_code = int(m.group(1))
            assert found_code == desired_code, "Unexpected user exit code {} expected {} for run_id {}".format(
                found_code, desired_code, run_id
            )
            break
    assert found_line


@contextmanager
def assert_git_commit(msg=None, branch="HEAD", remote=None, cwd=None, invert=False):
    """Assert that a commit occurs within the context manager

    Params:
        - msg (str): assert that commit message matches given fixed-string
        - branch (str): assert that commit occurs on given branch
        - remote (str): assert that commit occurs on given remote
        - cwd (str): working directory for the git commands
        - invert (bool): assert that no commit was made
    """
    # build the ref
    if remote is None:
        ref = "heads/{}".format(branch)
    else:
        ref = "remotes/{}/{}".format(remote, branch)

    # get the most recent commit hash
    try:
        curr_hash = git(["--no-pager", "rev-parse", ref], _cwd=cwd).stdout.decode("utf-8").strip()
    except Exception:
        curr_hash = None

    yield

    # get the commits since the yield
    log_args = [
        "--no-pager",
        "log",
        "--no-color",
        "--oneline",
    ]
    if curr_hash is not None:
        log_args += ["{}..{}".format(curr_hash, ref)]
    elif remote is not None:
        log_args.append(ref)
    if msg is not None:
        log_args += [
            "--grep={}".format(msg),
            "--fixed-strings",
        ]
    try:
        commits = git(log_args, _cwd=cwd).stdout.decode("utf-8").strip().split("\n")
    except sh.ErrorReturnCode_128:
        # current branch doesn't have any commits yet
        if curr_hash is not None:
            raise
        commits = [""]
    if invert:
        assert len(commits) == 1 and commits[0] == ""
    else:
        assert len(commits) > 0 and commits[0] != ""


class GitFactory:
    """factory for git repos"""

    def __init__(self, tmpdir_factory):
        self.tmpdir_factory = tmpdir_factory

    def init_repo(self, name, commit=False, commit_suffix=""):
        """create a new repo in a temporary directory
        if commit=True, adds a single commit
        """
        repo_dir = self.tmpdir_factory.mktemp(name)
        git.init(_cwd=str(repo_dir))
        if not commit:
            return repo_dir

        test_fname = os.path.join(str(repo_dir), "test.txt")
        with open(test_fname, "w") as test_f:
            test_f.write("test contents")
        git.add(test_fname, _cwd=str(repo_dir))

        commit_msg = "initial commit"
        if commit_suffix:
            commit_msg += " " + commit_suffix
        git.commit("-m", commit_msg, _cwd=str(repo_dir))

        return repo_dir

    def detached_head(self, name):
        repo_dir = self.init_repo(name, commit=True)
        test_fname2 = os.path.join(str(repo_dir), "test2.txt")
        with open(test_fname2, "w") as test_f:
            test_f.write("test contents 2")
        git.add(test_fname2, _cwd=str(repo_dir))

        commit_msg = "second commit"
        git.commit("-m", commit_msg, _cwd=str(repo_dir))
        ref = git("symbolic-ref", "-q", "HEAD", _cwd=str(repo_dir))
        ref = ref.strip()
        assert ref == "refs/heads/master", "unexpected repo state creating detached head -- HEAD: {}".format(ref)
        # checkout previous commit
        git.checkout("HEAD^1", _cwd=str(repo_dir))
        # ensure head is detached (command should fail since repo is not on a branch)
        try:
            out = git("symbolic-ref", "-q", "HEAD", _cwd=str(repo_dir))
            assert False, "failed to create detached head state -- HEAD: {}".format(out.strip())
        except sh.ErrorReturnCode:
            pass
        return repo_dir
