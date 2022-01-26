from spell.cli.integration_tests.testing_utils import (
    parse_raw,
    parse_run_id,
    verify_exit_code,
    wait_for_run_complete,
)


class TestArchive:
    def test_archive_existing_run(self, git_factory, run):
        repo_name = "test_archive_existing_run_repository"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # create run and make sure it doesn't fail
        with repo_dir.as_cwd():
            result = run(["run", "--background", "--from", "alpine:latest", "echo test_archive_existing_run"])
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

            # remove run
            result = run(["archive", run_id])
            verify_exit_code(result, 0)

            # query for runs and see none returned
            result = run(["ps", "--raw"])
            verify_exit_code(result, 0)
            vals = parse_raw(result.output)
            for val in vals:
                if val[0] == run_id:
                    assert False, "Run id {} still in `spell ps`".format(run_id)

            # try to remove run a second time and expect failure
            result = run(["archive", run_id])
            verify_exit_code(result, 1)

    def test_archive_nonexistant(self, run):
        # attempt to delete non-existant run and it should fail
        result = run(["archive", "10000"])
        verify_exit_code(result, 1)
