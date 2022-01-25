"""
Test file for theme options.
"""
import ddt
from django.test import RequestFactory, TestCase
from mock import Mock

from ecommerce_extensions.tenant.context_processors import theme_options
from ecommerce_extensions.tenant.models import TenantOptions


@ddt.ddt
class TestThemeOptions(TestCase):
    """
    Test class for theme options.
    """
    def setUp(self):
        self.request = RequestFactory(SERVER_NAME="testserver.fake").get("")
        self.request.site = Mock()

    def test_theme_options_signature(self):
        """
        Tests that theme_options returns a dict no matter what
        """
        result = theme_options(self.request)

        self.assertIsInstance(result, dict)

    def test_theme_options_contains_basics(self):
        """
        Tests that theme_options returns the theme_dir_name, siteconfiguration and options
        """
        result = theme_options(self.request)

        for item in ['theme_dir_name', 'site_configuration', 'options']:
            self.assertIn(item, result)

    @ddt.data(
        {"a": "test"},
        {"theming_var": "http://some.example.com/test.jpg"},
    )
    def test_theme_options_contains_options(self, test_dict):
        """
        Tests that theme_options returns the options dictionary into the options key
        """
        self.request.site.tenantoptions = TenantOptions(
            site_id=1,
            options_blob=test_dict,
        )

        result = theme_options(self.request)

        self.assertIsInstance(result.get("options"), dict)
        self.assertEqual(test_dict, result.get("options"))
