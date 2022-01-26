import os

import yaml

from spell.cli.integration_tests.testing_utils import verify_exit_code
from spell.configs.config_classes import GlobalConfig


def verify_global_config(spell_dir, user):
    config_path = os.path.join(spell_dir, "config")
    with open(config_path, "r") as f:
        conf = yaml.safe_load(f)
    valid, error = GlobalConfig.is_valid_dict(conf)
    assert valid
    assert all([getattr(user, field) == conf.get(field) for field in ("user_name", "email")])


def verify_no_global_config(spell_dir):
    config_path = os.path.join(spell_dir, "config")
    assert not os.path.exists(config_path)


class TestLogin:
    def test_login_with_email(self, spell_dir_tmp, user_info, run_logged_out):
        (user, password) = user_info
        result = run_logged_out(spell_dir_tmp, ["login", "--identity", user.email, "--password", password])
        verify_exit_code(result, 0)
        verify_global_config(spell_dir_tmp, user)
        assert "Hello, {}!".format(user.full_name) in result.output

    def test_login_with_username(self, spell_dir_tmp, user_info, run_logged_out):
        (user, password) = user_info
        result = run_logged_out(spell_dir_tmp, ["login", "--identity", user.user_name, "--password", password])
        verify_exit_code(result, 0)
        verify_global_config(spell_dir_tmp, user)

    def test_logout(self, spell_dir_tmp, user_info, run_logged_out):
        # Log in using test_login_with_username() if that fails, then this test will fail
        self.test_login_with_username(spell_dir_tmp, user_info, run_logged_out)
        # Now actually log out
        result = run_logged_out(spell_dir_tmp, ["logout"])
        verify_exit_code(result, 0)
        verify_no_global_config(spell_dir_tmp)

    def test_bad_username(self, spell_dir_tmp, user_info, run_logged_out):
        (user, password) = user_info
        result = run_logged_out(spell_dir_tmp, ["login", "--identity", "bad_user_name", "--password", password])
        verify_exit_code(result, 1)
        verify_no_global_config(spell_dir_tmp)

    def test_bad_password(self, spell_dir_tmp, user_info, run_logged_out):
        (user, password) = user_info
        result = run_logged_out(spell_dir_tmp, ["login", "--identity", user.user_name, "--password", "bad_password"])
        verify_exit_code(result, 1)
        verify_no_global_config(spell_dir_tmp)
