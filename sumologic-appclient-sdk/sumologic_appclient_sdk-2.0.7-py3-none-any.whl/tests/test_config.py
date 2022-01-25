import os
import sys
import traceback
import unittest
from unittest.mock import patch


if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from sumoappclient.common.errors import InValidConfigException
from sumoappclient.common.logger import get_logger
from sumoappclient.provider.factory import ProviderFactory
from sumoappclient.common.utils import read_yaml_file

from tests.base import ParametrizedTestCase, CustomTextTestRunner

logger = get_logger(__name__, force_create=True, ENABLE_LOGFILE=False)


def get_current_dir():
    cur_dir = os.path.dirname(__file__)
    return cur_dir


def mocked_requests_get(*args, **kwargs):
    if args[0] == 'http://localhost/config':
        return True, {
            'config': {'Collection|ENVIRONMENT': 'ctoc', 'Collection|BACKFILL_DAYS': '5', 'Slack|TOKEN': 'Token-ctoc'},
            'systemConfig': {'name': 'test-name', 'fields': {'service': 'okta', '_siemForward': True},
                             'category': 'test-category'}}

    return False, "Invalid URL"


def mocked_requests_another(*args, **kwargs):
    if args[0] == 'http://localhost/config':
        return True, {
            'config': {'Collection|ENVIRONMENT': 'ctoc', 'Collection|BACKFILL_DAYS': '5', 'Slack|TOKEN': 'Token-ctoc',
                       'Secrets|DECRYPT_KEYS': True},
            'systemConfig': {'name': 'test-name', 'fields': {'service': 'okta', '_siemForward': True},
                             'category': 'test-category'}}

    return False, "Invalid URL"


class TestingConfig(ParametrizedTestCase):
    WITH_ENVIRONMENT = "resources/with_environment.yaml"
    WITH_DECRYPT = "resources/with_decrypt.yaml"

    ROOT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    ENVIRONMENT_SPECIFIC_KEYS = {"ENVIRONMENT": "", "TOKEN": "test-token", "BACKFILL_DAYS": '3',
                                 "HTTP_LOGS_ENDPOINT": "http://localhost"}
    # Set this on the resources/with_environment.yaml created in home/sumo folder
    ONPREM_SPECIFIC_KEYS = {"TOKEN": "onprem-token", "BACKFILL_DAYS": '10',
                            "HTTP_LOGS_ENDPOINT": "https://collectors.sumologic.com/"}
    CTOC_KEYS = {"BACKFILL_DAYS": "5", "TOKEN": 'Token-ctoc', "HTTP_LOGS_ENDPOINT": "http://localhost"}

    # the encrypted values is the ARN of the secrets manager, so add secret manager in your AWS account
    # as {"TOKEN": "test-token", "HTTP_LOGS_ENDPOINT": "http://localhost"}
    DECRYPT_KEYS = {"ENVIRONMENT": "", "TOKEN": "arn:aws:secretsmanager:eu-west-2:668508221233:secret:prod/test/config-Xt7SSQ", "BACKFILL_DAYS": '3',
                    "HTTP_LOGS_ENDPOINT": "arn:aws:secretsmanager:eu-west-2:668508221233:secret:prod/test/config-Xt7SSQ"}

    @classmethod
    def get_config_file_paths(cls, decrypt):
        filename = cls.WITH_ENVIRONMENT
        if decrypt:
            filename = cls.WITH_DECRYPT
        cfgpath = sys.argv[1] if len(sys.argv) > 1 else ''
        return filename, get_current_dir(), cfgpath

    def read_mock_data(self):
        self.with_config = read_yaml_file(os.path.join(self.ROOT_FOLDER, self.WITH_ENVIRONMENT))
        self.with_decrypt = read_yaml_file(os.path.join(self.ROOT_FOLDER, self.WITH_DECRYPT))

    def setUp(self):
        super(ParametrizedTestCase, self).setUp()
        self.decrypt = False
        if self._testMethodName.startswith("test_e_with_decryption"):
            self.decrypt = True
        self.config_filename, self.root_dir, self.input_cfgpath = self.get_config_file_paths(self.decrypt)
        self.read_mock_data()

    def test_b_with_empty_keys(self):
        op_cli = ProviderFactory.get_provider(self.param)
        os.environ["ENVIRONMENT"] = self.param
        config_instance = op_cli.get_config("config", filename=self.config_filename, root_dir=self.root_dir,
                                            cfgpath=self.input_cfgpath)
        try:
            config = config_instance.get_config()
        except InValidConfigException as e:
            if self.param == "ctoc":
                self.assertEqual("Base URL not found", e.args[0])
            else:
                self.assertRegex(e.args[0], "Missing Parameters are \\[.*\\]")

    # For onprem to pass, create a file in home with resources/with_environment.yaml
    @patch('sumoappclient.sumoclient.httputils.ClientMixin.make_request', new=mocked_requests_get)
    def test_c_Invalid_URL(self):
        op_cli = ProviderFactory.get_provider(self.param)
        os.environ["ENVIRONMENT"] = self.param
        config_instance = op_cli.get_config("config", filename=self.config_filename, root_dir=self.root_dir,
                                            cfgpath=self.input_cfgpath)
        if self.param == "ctoc":
            os.environ["BASE_URL"] = "http://localhost"
        if self.param != "onprem":
            os.environ["TOKEN"] = "test-token"
            os.environ["BACKFILL_DAYS"] = "3"
            os.environ["HTTP_LOGS_ENDPOINT"] = "asd"
        try:
            config = config_instance.get_config()
        except InValidConfigException as e:
            if self.param == "ctoc":
                self.assertEqual("Invalid URL", e.args[0])
            else:
                self.assertEqual("asd does not match valid url regex", e.args[0])

    # For onprem to pass, create a file in home with resources/with_environment.yaml
    @patch('sumoappclient.sumoclient.httputils.ClientMixin.make_request', new=mocked_requests_get)
    def test_d_without_decryption(self):
        op_cli = ProviderFactory.get_provider(self.param)
        os.environ["ENVIRONMENT"] = self.param
        config_instance = op_cli.get_config("config", filename=self.config_filename, root_dir=self.root_dir,
                                            cfgpath=self.input_cfgpath)
        if self.param == "ctoc":
            os.environ["BASE_URL"] = self.ENVIRONMENT_SPECIFIC_KEYS["HTTP_LOGS_ENDPOINT"]
        if self.param != "onprem":
            os.environ["TOKEN"] = self.ENVIRONMENT_SPECIFIC_KEYS["TOKEN"]
            os.environ["BACKFILL_DAYS"] = self.ENVIRONMENT_SPECIFIC_KEYS["BACKFILL_DAYS"]
            os.environ["HTTP_LOGS_ENDPOINT"] = self.ENVIRONMENT_SPECIFIC_KEYS["HTTP_LOGS_ENDPOINT"]

        configuration = config_instance.get_config()
        self.assert_config(configuration)

    def assert_config(self, configuration):
        for section_name, section_keys in self.with_config.items():
            assert section_name in configuration
            created_config_for_section = configuration[section_name]
            for key, value in section_keys.items():
                if key not in self.ENVIRONMENT_SPECIFIC_KEYS.keys():
                    assert key in created_config_for_section
                    self.assertEqual(value, created_config_for_section[key])
                else:
                    if key == "ENVIRONMENT":
                        self.assertEqual(self.param, created_config_for_section[key])
                    elif self.param == "ctoc":
                        if key == "BACKFILL_DAYS":
                            self.assertEqual(self.CTOC_KEYS[key], str(created_config_for_section[key]))
                        else:
                            self.assertEqual(self.CTOC_KEYS[key], created_config_for_section[key])
                    elif self.param == "onprem":
                        if key == "BACKFILL_DAYS":
                            self.assertEqual(self.ONPREM_SPECIFIC_KEYS[key], str(created_config_for_section[key]))
                        else:
                            self.assertEqual(self.ONPREM_SPECIFIC_KEYS[key], created_config_for_section[key])
                    else:
                        if key == "BACKFILL_DAYS":
                            self.assertEqual(self.ENVIRONMENT_SPECIFIC_KEYS[key], str(created_config_for_section[key]))
                        else:
                            self.assertEqual(self.ENVIRONMENT_SPECIFIC_KEYS[key], created_config_for_section[key])

    # For onprem to pass, create a file in home with resources/with_decrypt.yaml
    @patch('sumoappclient.sumoclient.httputils.ClientMixin.make_request', new=mocked_requests_another)
    def test_e_with_decryption(self):
        op_cli = ProviderFactory.get_provider(self.param, region_name="eu-west-2")
        os.environ["ENVIRONMENT"] = self.param
        os.environ["DECRYPT_KEYS"] = "true"
        config_instance = op_cli.get_config("config", filename=self.config_filename, root_dir=self.root_dir,
                                            cfgpath=self.input_cfgpath)
        if self.param == "ctoc":
            os.environ["BASE_URL"] = self.ENVIRONMENT_SPECIFIC_KEYS["HTTP_LOGS_ENDPOINT"]
        elif self.param == "aws":
            os.environ["TOKEN"] = self.DECRYPT_KEYS["TOKEN"]
            os.environ["BACKFILL_DAYS"] = self.DECRYPT_KEYS["BACKFILL_DAYS"]
            os.environ["HTTP_LOGS_ENDPOINT"] = self.DECRYPT_KEYS["HTTP_LOGS_ENDPOINT"]
        else:
            os.environ["TOKEN"] = self.ENVIRONMENT_SPECIFIC_KEYS["TOKEN"]
            os.environ["BACKFILL_DAYS"] = self.ENVIRONMENT_SPECIFIC_KEYS["BACKFILL_DAYS"]
            os.environ["HTTP_LOGS_ENDPOINT"] = self.ENVIRONMENT_SPECIFIC_KEYS["HTTP_LOGS_ENDPOINT"]

        configuration = config_instance.get_config()
        self.assert_config(configuration)


def run_test():
    suite = unittest.TestSuite()
    result = None
    has_warnings = has_failures = False
    try:
        test_loader = unittest.TestLoader()
        test_names = test_loader.getTestCaseNames(TestingConfig)
        for test_name in test_names:
            for deployment_name in ["ctoc", "aws", "gcp", "azure", "onprem"]:
                suite.addTest(TestingConfig(deployment_name, test_name))

        result = CustomTextTestRunner().run(suite)
    except BaseException as e:
        logger.error("Error in run_test: %s\n%s" % (e, traceback.format_exc()))
    finally:
        if not result:
            has_failures = True  # must have failed on initialization
            logger.debug("Results - Failed to initialize")
        else:
            has_failures = not result.wasSuccessful()
            has_warnings = len(result.warnings) > 0

    logger.info("%s\n" % ("=" * 130))

    return has_failures, has_warnings


if __name__ == "__main__":
    run_test()
