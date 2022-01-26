from sh import (
    git,
    ls,
    sha256sum,
)
from spell.cli.integration_tests.testing_utils import (
    parse_run_id,
    verify_exit_code,
    verify_user_exit_code,
    wait_for_run_complete,
)


class TestRun:
    def test_run_with_non_zero_exit(self, git_factory, run):
        # create a new repo
        repo_name = "test_run_with_non_zero_exit"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # run the repo and make sure it doesn't fail
        with repo_dir.as_cwd():
            result = run(["run", "--background", "--from", "alpine:latest", "exit 66"])
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

            verify_user_exit_code(run_id, run, desired_code=66)

    def test_run_file_output(self, git_factory, run):
        # create a new repo
        repo_name = "test_run_with_non_zero_exit"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # Create a file and add it and commit it
        file_name = repo_dir.join("write_files.py")
        with open(str(file_name), "a") as dirty_file:
            dirty_file.write(
                """
import os
from subprocess import call
os.makedirs("folder_of_files")
with open("file_number_1.txt", 'w') as f:
    f.write("numero uno")
with open("folder_of_files/file_number_2.txt", 'w') as f:
    f.write("numero dos")
print("wrote 2 files")
call("find . -type f | grep -v sums | xargs sha256sum > sums", shell=True)
print("wrote hash sums of files")
"""
            )
        file_name.ensure()
        git.add(["-A"], _cwd=str(repo_dir))
        git.commit("-m", "adding write_files.py", _cwd=str(repo_dir))

        with repo_dir.as_cwd():
            result = run(["run", "--background", "python write_files.py"])
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

            # Ensure user code exited cleanly
            verify_user_exit_code(run_id, run)

            # Ensure `ls` lists the saved files
            result = run(["ls", "runs/" + run_id])
            verify_exit_code(result, 0)
            result_output = result.output
            assert "file_number_1.txt" in result_output, "ls did not have expected files"
            assert "folder_of_files" in result_output, "ls did not have expected files"

            # Ensure `-m` mounts the saved files and they can be listed
            result = run(["run", "-m", "runs/" + run_id + ":/mounted", "ls /mounted && sleep 2"])
            verify_exit_code(result, 0)
            result_output = result.output
            assert "file_number_1.txt" in result_output, "run did not mount expected files"
            assert "folder_of_files" in result_output, "run did not mount expected files"

            run2_id = parse_run_id(result_output)
            result = run(["info", run2_id])
            verify_exit_code(result, 0)
            result_output = result.output
            assert "runs/" + run_id in result_output, "info did not show expected mounts"

            # Ensure `-m` mounts the saved files and they can be read
            result = run(
                [
                    "run",
                    "-m",
                    "runs/" + run_id + ":/mounted",
                    "cat /mounted/file_number_1.txt && \
                          cat /mounted/folder_of_files/file_number_2.txt && \
                          sleep 2",
                ]
            )
            verify_exit_code(result, 0)
            result = run(["logs", parse_run_id(result.output)])
            verify_exit_code(result, 0)
            result_output = result.output
            assert "numero unonumero dos" in result_output, "run did not cat mounted files"

            # Ensure `cp` downloads the saved files and they can be listed
            result = run(["cp", "runs/" + run_id])
            verify_exit_code(result, 0)
            ls_output = str(ls("."))
            assert "sums" in ls_output, "cp did not download expected files"
            sha256sum("--check", "--status", "sums")
