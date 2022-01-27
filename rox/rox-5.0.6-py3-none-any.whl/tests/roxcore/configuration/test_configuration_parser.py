import unittest

from rox.core.client.sdk_settings import SdkSettings
from rox.core.configuration.configuration_fetched_invoker import ConfigurationFetchedInvoker, FetcherError
from rox.core.configuration.configuration_parser import ConfigurationParser
from rox.core.network.configuration_result import ConfigurationFetchResult, ConfigurationSource

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class ConfigurationParserTests(unittest.TestCase):
    def test_will_return_null_when_unexpected_exception(self):
        nested_json = """
        {
           "application":"12345",
           "targetGroups": [{"condition":"eq(true,true)","_id":"12345"},{"_id":"123456","condition":"eq(true,true)"}],
           "experiments": [
               {"deploymentConfiguration":{"condition":"ifThen(and(true, true)"},"featureFlags":[{"name":"FeatureFlags.isFeatureFlagsEnabled"}],"archived":false,"name":"Feature Flags Drawer Item","_id":"1"},
               {"deploymentConfiguration":{"condition":"ifThen(and(true, true)"},"featureFlags":[{"name":"Invitations.isInvitationsEnabled"}],"archived":false,"name":"Enable Modern Invitations","_id":"2"}]
        }
        """
        json = """
        {
            "nodata": "%s",
            "signature_v0":"K/bEQCkRXa6+uFr5H2jCRCaVgmtsTwbgfrFGVJ9NebfMH8CgOhCDIvF4TM1Vyyl0bGS9a4r4Qgi/g63NDBWk0ZbRrKAUkVG56V3/bI2GDHxFvRNrNbiPmFv/wmLLuwgh1mdzU0EwLG4M7yXoNXtMr6Jli8t4xfBOaWW1g0QpASkiWa7kdTamVip/1QygyUuhX5hOyUMpy4Ny9Hi/QPvVBn6GDMxQtxpLfTavU9cBly2D7Ex8Z7sUUOKeoEJcdsoF1QzH14XvA2HQSICESz7D/uld0PNdG0tMj9NlAZfki8eY2KuUe/53Z0Og5WrqQUxiAdPuJoZr6+kSqlASZrrkYw==",
            "signed_date":"2018-01-09T19:02:00.720Z"
        }
        """ % nested_json.replace('\n', r'\n').replace('"', r'\"')
        config_fetch_result = ConfigurationFetchResult(json, ConfigurationSource.CDN)
        sdk_settings = SdkSettings('12345', None)

        error_reporter = Mock()
        signature_verifier = Mock()
        signature_verifier.verify.return_value = True
        cfi = TestConfigurationFetchedInvoker()
        cp = ConfigurationParser(signature_verifier, error_reporter, cfi)
        conf = cp.parse(config_fetch_result, sdk_settings)

        self.assertIsNone(conf)
        self.assertIsNotNone(cfi.event)
        self.assertEqual(FetcherError.UNKNOWN, cfi.event.error_details)

    def test_will_return_null_when_wrong_signature(self):
        nested_json = """
        {
            "application": "12345",
            "targetGroups": [{"condition":"eq(true,true)","_id":"12345"},{"_id":"123456","condition":"eq(true,true)"}],
            "experiments": [
                {"deploymentConfiguration":{"condition":"ifThen(and(true, true)"},"featureFlags":[{"name":"FeatureFlags.isFeatureFlagsEnabled"}],"archived":false,"name":"Feature Flags Drawer Item","_id":"1"},
                {"deploymentConfiguration":{"condition":"ifThen(and(true, true)"},"featureFlags":[{"name":"Invitations.isInvitationsEnabled"}],"archived":false,"name":"Enable Modern Invitations","_id":"2"}]
        }
        """
        json = """
        {
            "data": "%s",
            "signature_v0": "wrongK/bEQCkRXa6+uFr5H2jCRCaVgmtsTwbgfrFGVJ9NebfMH8CgOhCDIvF4TM1Vyyl0bGS9a4r4Qgi/g63NDBWk0ZbRrKAUkVG56V3/bI2GDHxFvRNrNbiPmFv/wmLLuwgh1mdzU0EwLG4M7yXoNXtMr6Jli8t4xfBOaWW1g0QpASkiWa7kdTamVip/1QygyUuhX5hOyUMpy4Ny9Hi/QPvVBn6GDMxQtxpLfTavU9cBly2D7Ex8Z7sUUOKeoEJcdsoF1QzH14XvA2HQSICESz7D/uld0PNdG0tMj9NlAZfki8eY2KuUe/53Z0Og5WrqQUxiAdPuJoZr6+kSqlASZrrkYw==",
            "signed_date":"2018-01-09T19:02:00.720Z"
        }
        """ % nested_json.replace('\n', r'\n').replace('"', r'\"')
        config_fetch_result = ConfigurationFetchResult(json, ConfigurationSource.API)

        error_reporter = Mock()
        signature_verifier = Mock()
        signature_verifier.verify.return_value = False
        cfi = TestConfigurationFetchedInvoker()
        cp = ConfigurationParser(signature_verifier, error_reporter, cfi)
        conf = cp.parse(config_fetch_result, None)

        self.assertIsNone(conf)
        self.assertIsNotNone(cfi.event)
        self.assertEqual(FetcherError.SIGNATURE_VERIFICATION_ERROR, cfi.event.error_details)

    def test_will_return_null_when_wrong_api_key(self):
        nested_json = """
        {
            "application": "12345",
            "targetGroups": [{"condition":"eq(true,true)","_id":"12345"},{"_id":"123456","condition":"eq(true,true)"}],
            "experiments": [
                {"deploymentConfiguration":{"condition":"ifThen(and(true, true)"},"featureFlags":[{"name":"FeatureFlags.isFeatureFlagsEnabled"}],"archived":false,"name":"Feature Flags Drawer Item","_id":"1"},
                {"deploymentConfiguration":{"condition":"ifThen(and(true, true)"},"featureFlags":[{"name":"Invitations.isInvitationsEnabled"}],"archived":false,"name":"Enable Modern Invitations","_id":"2"}]
        }
        """
        json = """
        {
            "data": "%s",
            "signature_v0":"K/bEQCkRXa6+uFr5H2jCRCaVgmtsTwbgfrFGVJ9NebfMH8CgOhCDIvF4TM1Vyyl0bGS9a4r4Qgi/g63NDBWk0ZbRrKAUkVG56V3/bI2GDHxFvRNrNbiPmFv/wmLLuwgh1mdzU0EwLG4M7yXoNXtMr6Jli8t4xfBOaWW1g0QpASkiWa7kdTamVip/1QygyUuhX5hOyUMpy4Ny9Hi/QPvVBn6GDMxQtxpLfTavU9cBly2D7Ex8Z7sUUOKeoEJcdsoF1QzH14XvA2HQSICESz7D/uld0PNdG0tMj9NlAZfki8eY2KuUe/53Z0Og5WrqQUxiAdPuJoZr6+kSqlASZrrkYw==",
            "signed_date":"2018-01-09T19:02:00.720Z"
        }
        """ % nested_json.replace('\n', r'\n').replace('"', r'\"')
        config_fetch_result = ConfigurationFetchResult(json, ConfigurationSource.API)
        sdk_settings = SdkSettings('123', None)

        error_reporter = Mock()
        signature_verifier = Mock()
        signature_verifier.verify.return_value = True
        cfi = TestConfigurationFetchedInvoker()
        cp = ConfigurationParser(signature_verifier, error_reporter, cfi)
        conf = cp.parse(config_fetch_result, sdk_settings)

        self.assertIsNone(conf)
        self.assertIsNotNone(cfi.event)
        self.assertEqual(FetcherError.MISMATCH_APP_KEY, cfi.event.error_details)

    def test_will_parse_experiments_and_target_groups(self):
        nested_json = """
        {
            "application": "12345",
            "targetGroups": [{"condition":"eq(true,true)","_id":"12345"},{"_id":"123456","condition":"eq(true,true)"}],
            "experiments": [
                {"deploymentConfiguration":{"condition":"ifThen(and(true, true)"},"featureFlags":[{"name":"FeatureFlags.isFeatureFlagsEnabled"}],"archived":false,"name":"Feature Flags Drawer Item","_id":"1","labels":["label1"],"stickinessProperty":"stickinessProperty1"},
                {"deploymentConfiguration":{"condition":"ifThen(and(true, true)"},"featureFlags":[{"name":"Invitations.isInvitationsEnabled"}],"archived":false,"name":"Enable Modern Invitations","_id":"2","stickinessProperty":"stickinessProperty2"}]
        }
        """
        json = """
        {
            "data": "%s",
            "signature_v0":"K/bEQCkRXa6+uFr5H2jCRCaVgmtsTwbgfrFGVJ9NebfMH8CgOhCDIvF4TM1Vyyl0bGS9a4r4Qgi/g63NDBWk0ZbRrKAUkVG56V3/bI2GDHxFvRNrNbiPmFv/wmLLuwgh1mdzU0EwLG4M7yXoNXtMr6Jli8t4xfBOaWW1g0QpASkiWa7kdTamVip/1QygyUuhX5hOyUMpy4Ny9Hi/QPvVBn6GDMxQtxpLfTavU9cBly2D7Ex8Z7sUUOKeoEJcdsoF1QzH14XvA2HQSICESz7D/uld0PNdG0tMj9NlAZfki8eY2KuUe/53Z0Og5WrqQUxiAdPuJoZr6+kSqlASZrrkYw==",
            "signed_date":"2018-01-09T19:02:00.720Z"
        }
        """ % nested_json.replace('\n', r'\n').replace('"', r'\"')
        config_fetch_result = ConfigurationFetchResult(json, ConfigurationSource.API)
        sdk_settings = SdkSettings('12345', None)

        error_reporter = Mock()
        signature_verifier = Mock()
        signature_verifier.verify.return_value = True
        cfi = TestConfigurationFetchedInvoker()
        cp = ConfigurationParser(signature_verifier, error_reporter, cfi)
        conf = cp.parse(config_fetch_result, sdk_settings)

        self.assertIsNotNone(conf)
        self.assertEqual(2, len(conf.target_groups))
        self.assertEqual('12345', conf.target_groups[0].id)
        self.assertEqual('eq(true,true)', conf.target_groups[0].condition)
        self.assertEqual('123456', conf.target_groups[1].id)
        self.assertEqual('eq(true,true)', conf.target_groups[1].condition)

        self.assertEqual(2, len(conf.experiments))
        self.assertEqual('ifThen(and(true, true)', conf.experiments[0].condition)
        self.assertEqual('Feature Flags Drawer Item', conf.experiments[0].name)
        self.assertEqual('1', conf.experiments[0].id)
        self.assertEqual(False, conf.experiments[0].is_archived)
        self.assertEqual(1, len(conf.experiments[0].flags))
        self.assertEqual('FeatureFlags.isFeatureFlagsEnabled', conf.experiments[0].flags[0])
        self.assertEqual(1, len(conf.experiments[0].labels))
        self.assertIn('label1', conf.experiments[0].labels)
        self.assertEqual('stickinessProperty1', conf.experiments[0].stickinessProperty)
        self.assertEqual('ifThen(and(true, true)', conf.experiments[1].condition)
        self.assertEqual('Enable Modern Invitations', conf.experiments[1].name)
        self.assertEqual('2', conf.experiments[1].id)
        self.assertEqual(False, conf.experiments[1].is_archived)
        self.assertEqual(1, len(conf.experiments[1].flags))
        self.assertEqual('Invitations.isInvitationsEnabled', conf.experiments[1].flags[0])
        self.assertEqual(0, len(conf.experiments[1].labels))
        self.assertEqual('stickinessProperty2', conf.experiments[1].stickinessProperty)


class TestConfigurationFetchedInvoker:
    def __init__(self):
        self.cfi = ConfigurationFetchedInvoker(None)
        self.cfi.register_configuration_fetched_handler(self.on_configuration_fetched)
        self.event = None

    def invoke(self, fetcher_status, creation_date, has_changes):
        self.cfi.invoke(fetcher_status, creation_date, has_changes)

    def invoke_error(self, error_details):
        self.cfi.invoke_error(error_details)

    def on_configuration_fetched(self, e):
        self.event = e
