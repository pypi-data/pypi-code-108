from spell.cli.integration_tests.testing_utils import verify_exit_code


class TestLs:
    def test_ls_nonexistant_filepath(self, run):
        result = run(["ls", "public/image/mnist/does-not-exist"])
        verify_exit_code(result, 1)
