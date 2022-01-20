from spell.cli.integration_tests.testing_utils import (
    parse_run_id,
    verify_exit_code,
    wait_for_run_complete,
)


def verify_project_details(run_func, name, description=None):
    result = run_func(["project", "get", name])
    verify_exit_code(result, 0)

    for line in result.output.split("\n"):
        if line.startswith("Name") and name not in line:
            print(f"Project {name}: wrong name found in details - '{line}'")
            assert False
        if description and line.startswith("Description") and description not in line:
            print(f"Project {name}: wrong description found in details - '{line}'")
            assert False


class TestProject:
    def test_project(self, run):
        result = run(["project", "create", "-n", "a_project"])
        verify_exit_code(result, 0)
        verify_project_details(run, "a_project")

    def test_project_with_description_and_metric(self, run):
        result = run(["project", "create", "-n", "with_details", "-d", "This is a description."])
        verify_exit_code(result, 0)
        verify_project_details(run, "with_details", description="This is a description.")

    def test_project_edit(self, run):
        result = run(["project", "create", "-n", "to_edit"])
        verify_exit_code(result, 0)
        verify_project_details(run, "to_edit")

        result = run(["project", "edit", "to_edit", "-d", "This is a description"])
        verify_exit_code(result, 0)
        verify_project_details(run, "to_edit", description="This is a description")

        result = run(["project", "edit", "to_edit", "-d", "New description"])
        verify_exit_code(result, 0)
        verify_project_details(run, "to_edit", description="New description")

        result = run(["project", "edit", "to_edit", "-n", "to_edit_new_name"])
        verify_exit_code(result, 0)
        verify_project_details(run, "to_edit_new_name", description="New description")

    def test_project_list(self, run):
        # Make sure it works with no projects
        result = run(["project", "list"])
        verify_exit_code(result, 0)

        result = run(["project", "create", "-n", "to_list"])
        verify_exit_code(result, 0)

        result = run(["project", "list"])
        verify_exit_code(result, 0)
        assert "to_list" in result.output

    def test_archive(self, run):
        result = run(["project", "create", "-n", "to_archive"])
        verify_exit_code(result, 0)

        # archive
        result = run(["project", "archive", "to_archive"])
        verify_exit_code(result, 0)

        # not in list
        result = run(["project", "list"])
        verify_exit_code(result, 0)
        assert "to_archive" not in result.output

        # is in list --archived
        result = run(["project", "list", "--archived"])
        verify_exit_code(result, 0)
        assert "to_archive" in result.output

        # unarchive
        result = run(["project", "unarchive", "to_archive"])
        verify_exit_code(result, 0)

        # is in list
        result = run(["project", "list"])
        verify_exit_code(result, 0)
        assert "to_archive" in result.output

        # not in list --archived
        result = run(["project", "list", "--archived"])
        verify_exit_code(result, 0)
        assert "to_archive" not in result.output

    def test_project_with_run(self, git_factory, run):
        repo_name = "test_project"
        repo_dir = git_factory.init_repo(repo_name, commit=True)

        # create run and make sure it doesn't fail
        with repo_dir.as_cwd():
            command = "echo hello"
            result = run(["run", "--background", "--from", "alpine:latest", command])
            verify_exit_code(result, 0)
            run_id = parse_run_id(result.output)
            wait_for_run_complete(run_id, run)

        # create project with run
        result = run(["project", "create", "-n", "with_run", "-r", run_id])
        verify_exit_code(result, 0)

        # remove run
        result = run(["project", "remove-runs", "with_run", run_id])
        verify_exit_code(result, 0)

        # add run to a different project
        result = run(["project", "create", "-n", "without_run"])
        verify_exit_code(result, 0)

        result = run(["project", "add-runs", "without_run", run_id])
        verify_exit_code(result, 0)

        # make sure you can't add run to both projects
        result = run(["project", "add-runs", "with_run", run_id])
        verify_exit_code(result, 1)

        # make sure you can't remove from a project the run is not in
        result = run(["project", "remove-runs", "with_run", run_id])
        verify_exit_code(result, 1)
