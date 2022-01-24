import logging

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import translation

from pfx.pfxcore.test import APIClient, TestAssertMixin

logger = logging.getLogger(__name__)

test_settings = dict(
    LANGUAGE_CODE='en-us',
    LANGUAGES=[
        ('fr', "French"),
        ('fr-ch', "Swiss French"),
        ('en-us', "English"),
    ],
    USE_I18N=True,
    USE_L10N=True)


class LocaleAPITest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient()

    @override_settings(**test_settings)
    def test_get_langs(self):
        response = self.client.get('/api/locales/languages')

        self.assertRC(response, 200)
        self.assertJE(response, "meta.count", len(settings.LANGUAGES))

    @override_settings(**test_settings)
    def test_default_lang(self):
        """Test default language is taken."""
        response = self.client.get('/api/test-i18n')

        self.assertEqual(response.headers['Content-Language'], 'en-US')
        self.assertEqual(translation.get_language(), 'en-us')
        self.assertJE(response, "Monday", 'Monday')

    @override_settings(**test_settings)
    def test_browser_accept_language(self):
        """Test accept-language is taken."""
        response = self.client.get(
            '/api/test-i18n',
            HTTP_ACCEPT_LANGUAGE='fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7')

        self.assertEqual(response.headers['Content-Language'], 'fr-CH')
        self.assertEqual(translation.get_language(), 'fr-ch')
        self.assertJE(response, "Monday", 'lundi')

    @override_settings(**test_settings)
    def test_browser_undef_accept_language(self):
        """Test fist accept-language is ignored if it is not available."""
        response = self.client.get(
            '/api/test-i18n',
            HTTP_ACCEPT_LANGUAGE=(
                'it-CH,it;q=0.9,fr-CH,fr;q=0.8,en-US;q=0.7,en;q=0.6'))

        self.assertEqual(response.headers['Content-Language'], 'fr-CH')
        self.assertEqual(translation.get_language(), 'fr-ch')
        self.assertJE(response, "Monday", 'lundi')

    @override_settings(**test_settings)
    def test_pfx_custom_language(self):
        """Test x-custom-language has precedence over accept-language."""
        response = self.client.get(
            '/api/test-i18n',
            HTTP_X_CUSTOM_LANGUAGE='fr_CH',
            HTTP_ACCEPT_LANGUAGE='en-US;q=0.9,en;q=0.8')

        self.assertEqual(response.headers['Content-Language'], 'fr-CH')
        self.assertEqual(translation.get_language(), 'fr-ch')
        self.assertJE(response, "Monday", 'lundi')
