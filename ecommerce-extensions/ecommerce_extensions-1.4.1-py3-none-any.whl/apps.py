"""
App configuration for ecommerce_extensions.
"""

from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings

try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
except ImportError:
    sentry_sdk = DjangoIntegration = None


class EcommerceExtensionsConfig(AppConfig):
    """
    Django eduNEXT ecommerce-extensions configuration.
    """
    name = 'ecommerce_extensions'
    verbose_name = 'Django eduNEXT ecommerce-extensions app.'

    def ready(self):
        """
        Method to perform actions after apps registry is ended
        """
        sentry_integration_dsn = getattr(settings, 'ECOMMERCE_EXTENSIONS_SENTRY_INTEGRATION_DSN', None)
        if sentry_sdk and sentry_integration_dsn:
            sentry_sdk.init(
                dsn=sentry_integration_dsn,
                integrations=[
                    DjangoIntegration(),
                ],
                # Set traces_sample_rate to 1.0 to capture 100%
                # of transactions for performance monitoring.
                # We recommend adjusting this value in production.
                traces_sample_rate=0.1,
                # If you wish to associate users to errors (assuming you are using
                # django.contrib.auth) you may enable sending PII data.
                send_default_pii=True,
            )
