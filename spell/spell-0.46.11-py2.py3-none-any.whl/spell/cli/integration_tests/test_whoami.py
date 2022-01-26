import dateutil.parser

from spell.cli.integration_tests.testing_utils import verify_exit_code, parse_raw
from spell.api.models import User


class TestWhoami:
    def test_whoami(self, user_info, run):
        (user, password) = user_info
        result = run(["whoami", "--raw"])
        verify_exit_code(result, 0)

        # create new user from response
        vals = parse_raw(result.stdout)
        vals = dict(vals)
        vals["created_at"] = dateutil.parser.parse(vals["created_at"])
        vals["updated_at"] = dateutil.parser.parse(vals["updated_at"])
        new_user = User(**vals)

        assert user == new_user
