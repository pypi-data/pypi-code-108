from spell.cli.integration_tests.testing_utils import verify_exit_code


class TestOwner:
    def test_owner(self, run):
        verify_exit_code(run(["owner"]), 0)
