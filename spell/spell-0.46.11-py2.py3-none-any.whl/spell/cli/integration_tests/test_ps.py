from spell.cli.integration_tests.testing_utils import (
    parse_run_id,
    verify_exit_code,
    wait_for_run_complete,
)


class TestPs:
    def test_ps_with_unicode_command(self, git_factory, run):
        repo_name = "test_ps"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # create run and make sure it doesn't fail
        with repo_dir.as_cwd():
            command = "echo hellö"
            result = run(["run", "--background", "--from", "alpine:latest", command])
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

            # run ps
            result = run(["ps"])
            verify_exit_code(result, 0)

            # Loop through ps lines and make sure this run number exists with
            # the correct command
            for line in result.output.split("\n"):
                parts = [x for x in line.split(" ") if len(x) > 0]
                if len(parts) > 4 and parts[0] == run_id:
                    if parts[1].startswith(repo_name) and parts[2:4] == command.split(" "):
                        return
                    else:
                        print("Wrong repository and command in spell ps: {}".format(line))
                        assert False

            # Didn't find the line in the logs
            print(result.output)
            assert False
