import os
import sys
import traceback
import unittest
from unittest.mock import patch

if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from sumoappclient.common.logger import get_logger
from sumoappclient.configmanager.aws import AWSConfigHandler
from sumoappclient.configmanager.azure import AzureConfigHandler
from sumoappclient.configmanager.ctoc import CtoCConfigHandler
from sumoappclient.configmanager.gcp import GCPConfigHandler
from sumoappclient.configmanager.onprem import OnPremConfigHandler
from sumoappclient.omnistorage.ctoc import CToCKVStorage
from sumoappclient.omnistorage.onprem import OnPremKVStorage
from sumoappclient.omnistorage.gcp import GCPKVStorage
from sumoappclient.omnistorage.azure import AzureKVStorage
from sumoappclient.omnistorage.aws import AWSKVStorage
from sumoappclient.provider.aws import AWSProvider
from sumoappclient.provider.azure import AzureProvider
from sumoappclient.provider.ctoc import CToCProvider
from sumoappclient.provider.factory import ProviderFactory
from sumoappclient.provider.gcp import GCPProvider
from sumoappclient.provider.onprem import OnPremProvider
from tests.base import ParametrizedTestCase, CustomTextTestRunner

logger = get_logger(__name__, force_create=True, ENABLE_LOGFILE=False)


def mocked_table_exists(*args, **kwargs):
    return True


class TestingConfig(ParametrizedTestCase):
    provider_map = {
        "aws": AWSProvider,
        "azure": AzureProvider,
        "gcp": GCPProvider,
        "onprem": OnPremProvider,
        "ctoc": CToCProvider
    }

    config_map = {
        "aws": AWSConfigHandler,
        "azure": AzureConfigHandler,
        "gcp": GCPConfigHandler,
        "onprem": OnPremConfigHandler,
        "ctoc": CtoCConfigHandler
    }

    storage_map = {
        "aws": AWSKVStorage,
        "azure": AzureKVStorage,
        "gcp": GCPKVStorage,
        "onprem": OnPremKVStorage,
        "ctoc": CToCKVStorage
    }

    def test_a_check_provider(self):
        provider_instance = ProviderFactory.get_provider(self.param)
        if self.param in self.provider_map:
            self.assertIsInstance(provider_instance, self.provider_map.get(self.param))
        else:
            raise AssertionError(f"{self.param} is not part of the provider Map {self.provider_map}.")

    def test_b_check_config(self):
        provider_instance = ProviderFactory.get_provider(self.param)
        config_instance = provider_instance.get_config("config")
        if self.param in self.config_map:
            self.assertIsInstance(config_instance, self.config_map.get(self.param))
        else:
            raise AssertionError(f"{self.param} is not part of the Config Map {self.config_map}.")

    @patch('sumoappclient.omnistorage.aws.AWSKVStorage.table_exists', new=mocked_table_exists)
    @patch('sumoappclient.omnistorage.azurestore.AzureKVStorage.get_table_service', new=mocked_table_exists)
    @patch('sumoappclient.omnistorage.azurestore.AzureKVStorage.table_exists', new=mocked_table_exists)
    @patch('sumoappclient.omnistorage.ctocstore.CToCKVStorage._get', new=mocked_table_exists)
    @patch('google.cloud.datastore.Client', new=mocked_table_exists)
    def test_c_check_storage(self):
        provider_instance = ProviderFactory.get_provider(self.param)
        storage_instance = provider_instance.get_storage("keyvalue", name="kvstore")
        if self.param in self.storage_map:
            self.assertIsInstance(storage_instance, self.storage_map.get(self.param))
        else:
            raise AssertionError(f"{self.param} is not part of the Storage Map {self.storage_map}.")


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
