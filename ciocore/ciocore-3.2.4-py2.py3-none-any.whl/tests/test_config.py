import unittest
import base64
import sys
import os
import logging

try:
    from unittest import mock
except ImportError:
    import mock

APIKEY = '{"auth_provider_x509_cert_url": "https://www.exampleapis.com/oauth2/v1/certs", "auth_uri": "https://accounts.example.com/o/oauth2/auth", "client_email": "account-5641301770895360@eloquent-vector-104019.iam.gserviceaccount.com", "client_id": "106815243682887997903", "client_x509_cert_url": "https://www.exampleapis.com/robot/v1/metadata/x509/account-5641301770895360%40eloquent-vector-104019.iam.gserviceaccount.com", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDcadqRWyd7VpYN\n804fEn07qlqNXU0ihz6g2dfbj9gzZDhHGVCI5QvPFskAQcV91k8cDdFu380m+sh1\nz9wlcdaM/lksRV/DRJiV76qrqyrNi0gSekZUuYhSsyMWUGvG4aSbf5BzVf1j8W4I\nUArH+ht5pgdSjowNc4zQIqmMH2XY+Ntr+NysBBfIv1PI6GoHFgDYOTSzsvz0qFYS\nWuonYGTjzNz4CY9Yh5ki8iq0/ijKzpUWeRUkpK9uF7WBoxrj3EyFFHejtfhVX2l0\n2KxrIF0kkmy5nmxVUck76FqdQ6vyvaHudREd3z/08hgdYogemQUTKFE/0LQmKuBV\nIJipPvORAgMBAAECggEAZvPMozN8LBikC00XstzMgRePp1MqydN5NeG6+TPlrQ+F\nV/RjkSXHT8oZRdTy3dXB6t0rc4n2xdvC0YCvGBBlwkK1vT+EPO2oBfTF99yCKDME\nDZlui3mDyvkgjPYweVuBKx65Bp5mNo4ZMqnMd18EAVxDM9UgZtIPtlJSdoBd7qtk\nyCGr03l+SV0krmvPV+KS9vyDOg/7Km5gMhTMaIveNyS1pG6AmZ0ggQA5djg/P2iF\nxGwYdvfADY5cBzg0OG5ELv9hvyA4CKN6RLfYv3JJS2gbNaMknjmsjaM/p0LtE2HL\n+uFPL0ZjoMwV3BlEFQIHwhNWS63H43ISBa1/2XvGPwKBgQDw4a4kQ9+Ce3edWonz\n3Fm/3no+HrMSVjbv28qphAHMFrSUdbMejQm4QSbNeOW1pEcVvW21u8tYagrJEsaU\ns4DulFXRep36teVDWpc1FrNowWEPPVeC8CO74VfssK1h2Itqis8JPbzXOcNtSH9+\nAg1EvrB9XnyEvJuM6GOGo3juTwKBgQDqP058+H3iSZe6al4P6Ib3g/82nr2dHeN5\n4xxGu1fzTMNX5lopbNji6tQcsMoMVPdOvCQy5c0PEUbvo7mxfZ8fOZwgBjIcXbYg\nzIJkPTSv7nxSE5M5lW5juzLkdq2k5k0qt9ByWuWEA3PSn/DEANa5888phSCoJSw/\nPjpwHhZoHwKBgQDCoQbMxI6e5lYCrToT8PIPhpptAO8dnM2sxoGcsE2ncp0b63H7\n+GdnGjVZBhtMxdyt4y33DjLCUIRAbUxIsDU4EGC67oEhJsGEx3iva5Uwyjc7UgwY\nfyHQV8ZsN2EQUyBqyJd6VwjzOff+n/prfQrthcoisiqYMbDZjJeGHSXEHwKBgAo4\nBsmG4Z78jOTx/PZ+s1ya4ohUdnsjMahAkxw20ghoIeF0yBwkhnWnvucdg0L0dfF2\nXbHmuoJcw5ZyswgeLdHj5n6zJn58TBS0Nz/+N40xPzUpa3PIpA8vvHGhB8Q408b4\nS9yhQH/40pWuqocybiugijoKd7k+HecIZO49MccLAoGBAPDScJHSxKPW6wJKjxDC\nXXWWQ2flbwv4Sja487QV/trWMSRnHJHnCVHqv/F7ThPaoHM+MJSzrJ7wr/CJhk0H\noEt+0Rn6qPd/A36bSjTfXMFLXWi75ovek+IJGKxr7B46jrcS/oe1XIIOlV1+OvOY\nVoO6vgYkPhpMkth2hyZ/luea\n-----END PRIVATE KEY-----\n", "private_key_id": "3dfe3bdc40d4dc431d283bf22feb113c9b622dd3", "project_id": "eloquent-vector-104019", "token_uri": "https://oauth2.exampleapis.com/token", "type": "service_account"}'

PY3 = sys.version_info >= (3, 0)
BUILTIN_OPEN = "builtins.open" if PY3 else "__builtin__.open"


from ciocore import config
from ciocore import loggeria


class ConfigInitTest(unittest.TestCase):
    def up(self, **overrides):
        """
        Call this setup before every test.

        It Mocks the 2 api_key functions, the multiprocessing package, and the os environment.
        """
        self.cpu_count_patcher = mock.patch(
            "multiprocessing.cpu_count", return_value=overrides.get("cpu_count", 4)
        )
        self.mock_cpu_count = self.cpu_count_patcher.start()
        if overrides.get("cpu_count_raise", False):
            self.mock_cpu_count.side_effect = NotImplementedError()

        self.get_api_key_from_variable_patcher = mock.patch.object(
            config.Config,
            "get_api_key_from_variable",
            autospec=True,
            return_value=overrides.get("api_key_from_variable"),
        )
        self.mock_get_api_key_from_variable = self.get_api_key_from_variable_patcher.start()

        self.get_api_key_from_file_patcher = mock.patch.object(
            config.Config,
            "get_api_key_from_file",
            autospec=True,
            return_value=overrides.get("api_key_from_file"),
        )
        self.mock_get_api_key_from_file = self.get_api_key_from_file_patcher.start()

        self.env_patcher = mock.patch.dict("os.environ", overrides.get("env", {}))
        self.mock_env = self.env_patcher.start()

    def down(self):
        self.cpu_count_patcher.stop()
        self.get_api_key_from_variable_patcher.stop()
        self.get_api_key_from_file_patcher.stop()
        self.env_patcher.stop()

    def test_create(self):
        cfg = config.Config()
        self.assertEqual(cfg.__class__.__name__, "Config")

    # THREAD COUNT
    def test_thread_count_is_double_cpu_count(self):
        self.up(cpu_count=2)
        cfg = config.Config()
        self.assertEqual(cfg.config["thread_count"], 4)
        self.down()

    def test_thread_count_is_max_16(self):
        self.up(cpu_count=12)
        cfg = config.Config()
        self.assertEqual(cfg.config["thread_count"], 16)
        self.down()

    def test_thread_count_is_16_if_an_exception_is_thrown(self):
        self.up(cpu_count_raise=True)
        cfg = config.Config()
        self.assertEqual(cfg.config["thread_count"], 16)
        self.down()

    def test_thread_count_variable_overrides_default(self):
        self.up(env={"CONDUCTOR_THREAD_COUNT": "10"})
        cfg = config.Config()
        self.assertEqual(cfg.config["thread_count"], 10)
        self.down()

    # LOG LEVEL
    def test_log_level_default_to_INFO(self):
        self.up()
        cfg = config.Config()
        self.assertEqual(cfg.config["log_level"], "INFO")
        self.down()

    def test_log_level_variable_overrides_default(self):
        self.up(env={"CONDUCTOR_LOG_LEVEL": "DEBUG"})
        cfg = config.Config()
        self.assertEqual(cfg.config["log_level"], "DEBUG")
        self.down()

    def test_log_level_info_if_invalid_level_specified(self):
        self.up(env={"CONDUCTOR_LOG_LEVEL": "JUNK"})
        cfg = config.Config()
        self.assertEqual(cfg.config["log_level"], "INFO")
        self.down()

    def test_sets_up_logging_with_default_level(self):
        self.up()
        with mock.patch("ciocore.loggeria.setup_conductor_logging") as setup_logging_mock:
            config.Config()
            setup_logging_mock.assert_called_with(
                loggeria.LEVEL_MAP.get("INFO"), loggeria.FORMATTER_VERBOSE
            )
        self.down()

    def test_sets_up_logging_with_custom_level(self):
        self.up(env={"CONDUCTOR_LOG_LEVEL": "DEBUG"})
        with mock.patch("ciocore.loggeria.setup_conductor_logging") as setup_logging_mock:
            config.Config()
            setup_logging_mock.assert_called_with(
                loggeria.LEVEL_MAP.get("DEBUG"), loggeria.FORMATTER_VERBOSE
            )
        self.down()

    # PRIORITY
    def test_priority_default_to_5(self):
        self.up()
        cfg = config.Config()
        self.assertEqual(cfg.config["priority"], 5)
        self.down()

    def test_priority_variable_overrides_default(self):
        self.up(env={"CONDUCTOR_PRIORITY": "3"})
        cfg = config.Config()
        self.assertEqual(cfg.config["priority"], 3)
        self.down()

    # MD5
    def test_md5_caching_default_to_true(self):
        self.up()
        cfg = config.Config()
        self.assertTrue(cfg.config["md5_caching"])
        self.down()

    def test_md5_caching_true_if_variable_set_and_is_truthy(self):
        self.up(env={"CONDUCTOR_MD5_CACHING": "TRUE"})
        cfg = config.Config()
        self.assertTrue(cfg.config["md5_caching"])
        self.down()

    def test_md5_caching_true_if_variable_set_and_is_a_mistake(self):
        self.up(env={"CONDUCTOR_MD5_CACHING": "UNKNOWN"})
        cfg = config.Config()
        self.assertTrue(cfg.config["md5_caching"])
        self.down()

    def test_md5_caching_false_if_variable_set_and_is_falsy(self):
        self.up(env={"CONDUCTOR_MD5_CACHING": "FALSE"})
        cfg = config.Config()
        self.assertFalse(cfg.config["md5_caching"])
        self.down()

    # URLS
    def test_project_url_defaults_to_dashboard(self):
        self.up()
        cfg = config.Config()
        expected = "https://dashboard.conductortech.com"
        self.assertEqual(cfg.config["url"], expected)
        self.down()

    def test_api_url_default_derived_from_url(self):
        something = "https://dashboard.something.com"
        self.up(env={"CONDUCTOR_URL": something})
        cfg = config.Config()
        expected = "https://api.something.com"
        self.assertEqual(cfg.config["api_url"], expected)
        self.down()

    # API KEY
    def test_api_key_none_if_none_from_variable_or_file(self):
        self.up()
        cfg = config.Config()
        self.assertEqual(cfg.config["api_key"], None)
        self.down()

    def test_api_key_variable_takes_priority(self):
        self.up(api_key_from_variable="a", api_key_from_file="b")
        cfg = config.Config()
        self.assertEqual(cfg.config["api_key"], "a")
        self.down()

    def test_api_key_set_from_file_if_variable_none(self):
        self.up(api_key_from_file="b")
        cfg = config.Config()
        self.assertEqual(cfg.config["api_key"], "b")
        self.down()

    # GET
    def test_config_method_returns_config_object(self):
        self.up()
        cfg = config.config()
        self.assertEqual(cfg.__class__.__name__, "Config")
        self.down()

    def test_config_returns_same_object_if_not_force(self):
        self.up()
        cfg0 = config.config()
        cfg1 = config.config()
        self.assertEqual(cfg0, cfg1)
        self.down()

    def test_config_returns_fresh_object_if_force(self):
        self.up()
        cfg0 = config.config()
        cfg1 = config.config(force=True)
        self.assertNotEqual(cfg0, cfg1)
        self.down()


class ApiKeyFromVariableTest(unittest.TestCase):
    def up(self, **overrides):
        """
        Mock the os env.
        """
        self.env_patcher = mock.patch.dict("os.environ", overrides.get("env", {}))
        self.mock_env = self.env_patcher.start()

    def down(self):
        self.env_patcher.stop()

    def test_returns_none_if_env_var_missing(self):
        self.up()
        result = config.Config.get_api_key_from_variable()
        self.assertEqual(result, None)
        self.down()

    def test_returns_dict_if_key_is_valid_json(self):
        self.up(env={"CONDUCTOR_API_KEY": '{"a":1}'})
        result = config.Config.get_api_key_from_variable()
        self.assertIsInstance(result, dict)
        self.down()

    def test_returns_dict_if_key_is_b64encoded(self):
        key = APIKEY
        if sys.version_info < (3, 0):
            self.up(env={"CONDUCTOR_API_KEY": base64.b64encode(key)})
        else:
            self.up(
                env={"CONDUCTOR_API_KEY": base64.b64encode(key.encode("ascii")).decode("ascii")}
            )
        result = config.Config.get_api_key_from_variable()
        self.assertIsInstance(result, dict)
        self.down()

    def test_raises_if_key_is_unresolvable(self):
        self.up(env={"CONDUCTOR_API_KEY": "junk"})
        with self.assertRaises(ValueError):
            config.Config.get_api_key_from_variable()
        self.down()


class ApiKeyFromFileTest(unittest.TestCase):
    def up(self, **overrides):
        """
        Mock the os env.
        """
        self.env_patcher = mock.patch.dict("os.environ", overrides.get("env", {}))
        self.mock_env = self.env_patcher.start()

    def down(self):
        self.env_patcher.stop()

    def test_returns_none_if_api_key_path_env_var_missing(self):
        self.up()
        result = config.Config.get_api_key_from_file()
        self.assertEqual(result, None)
        self.down()

    @mock.patch(BUILTIN_OPEN, new_callable=mock.mock_open, read_data=APIKEY, create=True)
    def test_open_called_with_api_key_path(self, mock_file_open):
        self.up(env={"CONDUCTOR_API_KEY_PATH": "path/to/api_key"})
        config.Config.get_api_key_from_file()
        mock_file_open.assert_called_with("path/to/api_key", "r")
        self.down()

    @mock.patch(BUILTIN_OPEN, new_callable=mock.mock_open, read_data="junk", create=True)
    def test_raises_if_key_is_unresolvable(self, mock_file_open):
        self.up(env={"CONDUCTOR_API_KEY_PATH": "path/to/api_key"})
        with self.assertRaises(ValueError):
            config.Config.get_api_key_from_file()
        self.down()

    @mock.patch(BUILTIN_OPEN, new_callable=mock.mock_open, read_data=APIKEY, create=True)
    def test_returns_dict_if_key_is_valid_json(self, mock_file_open):
        self.up(env={"CONDUCTOR_API_KEY_PATH": "path/to/api_key"})
        result = config.Config.get_api_key_from_file()
        self.assertIsInstance(result, dict)
        self.down()
