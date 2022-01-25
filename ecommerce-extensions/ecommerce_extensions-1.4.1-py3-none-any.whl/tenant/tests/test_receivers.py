"""
Test file for receivers.py.
"""
import logging

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch
from testfixtures import LogCapture

from ecommerce_extensions.tenant.conf import TenantAwareSettings
from ecommerce_extensions.tenant.receivers import update_tenant_settings

MODULE = update_tenant_settings.__module__


class UpdateTenantSettingsTests(TestCase):
    """Test cases for the method update_tenant_settings."""

    def setUp(self):
        self.sender = "fake-sender"
        self.environ = {
            "HTTP_HOST": "https://ilvermorny-school.com",
        }

    def test_update_with_no_domain(self):
        """
        This method tests when there is no "HTTP_HOST" key in the environ.

        Expected behavior:
            - A warning is logged.
        """
        log = "Could not find the host information."

        with LogCapture(level=logging.WARNING) as log_capture:
            update_tenant_settings(
                sender=self.sender,
                environ={},
            )

            log_capture.check(
                (MODULE, "WARNING", log),
            )

    @override_settings(OSCAR_DEFAULT_CURRENCY="CAD")
    @patch.object(TenantAwareSettings, "get_tenant_options")
    def test_override_simple_value(self, get_tenant_options_mock):
        """
        This method tests to override a simple value.

        Expected behavior:
            - get_tenant_options is called once with the "HTTP_HOST" value.
            - A current setting is overridden.
            - A new setting is added.
        """
        options = {
            "OSCAR_DEFAULT_CURRENCY": "EUR",
            "custom_setting": "fake-value",
        }
        get_tenant_options_mock.return_value = options

        update_tenant_settings(
            sender=self.sender,
            environ=self.environ,
        )

        get_tenant_options_mock.called_once_with(self.environ["HTTP_HOST"])
        self.assertEqual(options["OSCAR_DEFAULT_CURRENCY"], settings.OSCAR_DEFAULT_CURRENCY)
        self.assertEqual(options["custom_setting"], settings.custom_setting)

    @override_settings(ANOTHER_SETTING={
        "custom_key": "fake_value",
        "custom_key2": "fake_value2",
    })
    @patch("ecommerce_extensions.tenant.receivers._perform_reset")
    @patch.object(TenantAwareSettings, "get_tenant_options")
    def test_override_dict_value(self, get_tenant_options_mock, _):
        """
        This method tests to override a dict value.

        Expected behavior:
            - get_tenant_options is called once with the "HTTP_HOST" value.
            - A current setting is overridden.
            - A current setting is kept.
        """
        options = {
            "ANOTHER_SETTING": {
                "custom_key": "overriden_value",
            },
        }
        get_tenant_options_mock.return_value = options

        update_tenant_settings(
            sender=self.sender,
            environ=self.environ,
        )

        get_tenant_options_mock.called_once_with(self.environ["HTTP_HOST"])
        self.assertEqual(
            options["ANOTHER_SETTING"]["custom_key"],
            settings.ANOTHER_SETTING["custom_key"],
        )
        self.assertEqual(
            "fake_value2",
            settings.ANOTHER_SETTING["custom_key2"],
        )
