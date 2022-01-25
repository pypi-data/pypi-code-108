"""
App configuration for tenant.
"""
from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.signals import request_started


class TenantConfig(AppConfig):
    """
    Django eduNEXT e-commerce tenant configuration.
    """
    name = 'ecommerce_extensions.tenant'
    label = 'edunext'
    verbose_name = 'eduNEXT tenant'

    def ready(self):
        """
        Method to perform actions after apps registry is ended
        """
        # pylint: disable=import-outside-toplevel
        from ecommerce_extensions.tenant.receivers import update_tenant_settings
        request_started.connect(update_tenant_settings)
