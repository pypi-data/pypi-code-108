from sh import git
import tempfile

from spell.cli.exceptions import SPELL_INVALID_COMMIT
from spell.cli.integration_tests.testing_utils import (
    parse_run_id,
    verify_exit_code,
    verify_user_exit_code,
    wait_for_run_complete,
)

CONDA_FILE_CONTENTS = """
name: mycondaenv
channels:
- defaults
dependencies:
- pip
- pip:
  - cowsay
"""


class TestRun:
    def test_run(self, git_factory, run):
        # create a new repo
        repo_name = "test_run_repository"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # run the repo and make sure it doesn't fail
        cmd = ["run", "--background", "--from", "alpine:latest", "echo test_run"]
        with repo_dir.as_cwd():
            result = run(cmd)
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # verify spell info succeeds
        verify_exit_code(run(["info", run_id]), 0)

        # verify that the repository is listed
        result = run(["repos"])
        verify_exit_code(result, 0)
        assert repo_name in result.output

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)

    def test_run_with_no_repository(self, run, tmpdir):
        # run the repo and make sure it doesn't fail
        cmd = [
            "run",
            "--background",
            "--force",
            "--from",
            "alpine:latest",
            "echo test_run_with_no_repository",
        ]
        with tmpdir.as_cwd():
            result = run(cmd)
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)

    def test_run_warns_with_dirty_untracked_repo(self, git_factory, run):
        # create a new repo
        repo_name = "test_run_fails_with_dirty_unstaged_repo"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # Create a file and don't add it
        repo_dir.join("dirty_file.txt").ensure()

        # run the repository
        cmd = [
            "run",
            "--background",
            "--from",
            "alpine:latest",
            "echo test_run_warns_with_dirty_untracked_repo",
        ]
        with repo_dir.as_cwd():
            result = run(cmd, input="y")
            assert "untracked files in repo" in result.output
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)

    def test_run_includes_uncommitted_with_dirty_unstaged_repo(self, git_factory, run):
        # create a new repo
        repo_name = "test_run_fails_with_dirty_unstaged_repo"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # Create a file and add it and commit it
        file_name = repo_dir.join("dirty_file.txt")
        file_name.ensure()
        git.add(["-A"], _cwd=str(repo_dir))
        git.commit("-m", "adding dirty file", _cwd=str(repo_dir))

        # Now edit the committed file (it's tracked) but don't commit it
        with open(str(file_name), "a") as dirty_file:
            dirty_file.write("test contents")

        # run the repository, it should print the uncommitted changes
        cmd = ["run", "--from", "alpine:latest", "cat dirty_file.txt"]
        with repo_dir.as_cwd():
            result = run(cmd)
            assert "Preparing uncommitted changes" in result.output
            verify_exit_code(result, 0)
            assert "test contents" in result.output
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)

    def test_run_fails_with_dirty_staged_repo(self, git_factory, run):
        # create a new repo
        repo_name = "test_run_fails_with_dirty_staged_repo"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # Create a file with contents and add it, but don't commit it
        file_name = repo_dir.join("dirty_file.txt")
        file_name.ensure()
        with open(str(file_name), "a") as dirty_file:
            dirty_file.write("test contents")
        git.add(["-A"], _cwd=str(repo_dir))

        # run the repository, it should print the uncommitted changes
        cmd = ["run", "cat dirty_file.txt"]
        with repo_dir.as_cwd():
            result = run(cmd)
            assert "Preparing uncommitted changes" in result.output
            verify_exit_code(result, 0)
            assert "test contents" in result.output
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)

    def test_run_with_bad_commit(self, git_factory, run):
        # create a new repository
        repo_name = "test_run_with_bad_commit_repository"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # run with HEAD~10, which doesn't exist yet
        cmd = [
            "run",
            "--background",
            "--from",
            "alpine:latest",
            "--commit-ref",
            "HEAD~10",
            "echo test_run_with_bad_commit",
        ]
        with repo_dir.as_cwd():
            result = run(cmd)
            verify_exit_code(result, SPELL_INVALID_COMMIT)

    def test_run_with_detached_head(self, git_factory, run):
        repo_name = "test_run_with_detached_head"
        repo_dir = git_factory.detached_head(repo_name)

        cmd = ["run", "--background", "--from", "alpine:latest", "echo test_run_with_detached_head"]
        with repo_dir.as_cwd():
            result = run(cmd)
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)

    def test_run_with_bad_attached_run_id(self, git_factory, run):
        # create a new repository
        repo_name = "test_run_with_bad_attached_run_id_repository"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # run with mount 100, which doesn't exist yet
        cmd = [
            "run",
            "--background",
            "--from",
            "alpine:latest",
            "--mount",
            "runs/100:/path/to/mount",
            "echo test_run_with_bad_attached_run_id",
        ]
        with repo_dir.as_cwd():
            result = run(cmd)
            assert "Cannot mount resource" in result.stderr and "not a valid resource" in result.stderr
            verify_exit_code(result, 1)

    def test_run_with_bad_attached_run_path(self, git_factory, run):
        # create a new repository
        repo_name = "test_run_with_bad_attached_run_path_repository"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # run with mount 1, but with a relative path which should fail
        cmd = [
            "run",
            "--background",
            "--from",
            "alpine:latest",
            "--mount",
            "runs/1:relative/path/to/mount",
            "echo test_run_with_bad_attached_run_path",
        ]
        with repo_dir.as_cwd():
            result = run(cmd)
            verify_exit_code(result, 1)

    def test_run_with_packages(self, git_factory, run):
        # create a new repository
        repo_name = "test_run_with_packages"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        cmd = [
            "run",
            "--background",
            "--apt",
            "netcat",
            "--pip",
            "cowsay",
            "--force",
            "python -c \"import cowsay; print(cowsay.cow('shall we promote?'))\" && nc -h",
        ]
        with repo_dir.as_cwd():
            result = run(cmd)
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)

    def test_run_with_path_within_resource(self, git_factory, run):
        # create a new repository
        repo_name = "test_run_with_path_within_resource_repository"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        cmd = [
            "run",
            "--background",
            "--mount",
            "public/image/mnist/t10k-images-idx3-ubyte:data",
            "--force",
            "test -f data",
        ]
        with repo_dir.as_cwd():
            result = run(cmd)
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)

    def test_run_with_conda(self, run, tmpdir):
        with tempfile.NamedTemporaryFile(mode="w+") as env_yml:
            env_yml.write(CONDA_FILE_CONTENTS)
            env_yml.flush()
            cmd = [
                "run",
                "-b",
                "--conda-file",
                env_yml.name,
                "python -c \"import cowsay; print(cowsay.cow('test_run_with_no_repository'))\"",
            ]
            with tmpdir.as_cwd():
                result = run(cmd)
                verify_exit_code(result, 0)
                run_id = parse_run_id(result.output)
                wait_for_run_complete(run_id, run)

        # verify the run itself exited 0
        verify_user_exit_code(run_id, run)
