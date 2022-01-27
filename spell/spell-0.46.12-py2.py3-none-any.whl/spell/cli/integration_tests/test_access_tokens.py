import os
from spell.cli.integration_tests.testing_utils import verify_exit_code, parse_raw


class TestAccessTokens:
    def test_access_tokens(self, user_info, run):
        result = run(["access-tokens", "list", "--raw"])
        verify_exit_code(result, 0)
        vals = parse_raw(result.stdout)
        assert vals[0][0] == "", "Expected 0 access tokens at first"

        result = run(["access-tokens", "create", "at1", "--raw"])
        verify_exit_code(result, 0)

        # Ensure this new token works
        os.environ["SPELL_TOKEN"] = result.stdout.strip()
        os.environ["SPELL_OWNER"] = "cli_test"
        result = run(["whoami"])
        verify_exit_code(result, 0)

        # Ensure a bad token DOESN'T work
        os.environ["SPELL_TOKEN"] = "bad token"
        result = run(["whoami"])
        verify_exit_code(result, 1)

        # Revert to no token override to continue testing
        del os.environ["SPELL_TOKEN"]
        del os.environ["SPELL_OWNER"]

        result = run(["access-tokens", "list", "--raw"])
        verify_exit_code(result, 0)
        vals = parse_raw(result.stdout)
        assert len(vals) == 1, "Expected 1 access tokens after creation"
        assert vals[0][0] == "at1", "Expected access token to be named at1"

        result = run(["access-tokens", "create", "at1"])
        verify_exit_code(result, 1)

        result = run(["access-tokens", "delete", "at1"])
        verify_exit_code(result, 0)

        result = run(["access-tokens", "list", "--raw"])
        verify_exit_code(result, 0)
        vals = parse_raw(result.stdout)
        assert vals[0][0] == "", "Expected 0 access tokens after deletion"
