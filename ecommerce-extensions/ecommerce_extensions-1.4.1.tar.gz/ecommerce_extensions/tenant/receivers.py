"""Receiver file, contains all the methods which should be connected to a signal.

Receivers:
    update_tenant_settings: Connected to django.core.signals.request_started, will update
    the settings values.
"""
import importlib
import logging
from datetime import datetime

import six
from compressor import conf
from django.conf import settings as base_settings

from ecommerce_extensions.tenant.conf import TenantAwareSettings

LOG = logging.getLogger(__name__)


def update_tenant_settings(sender, environ, **kwargs):  # pylint: disable=unused-argument
    """Perform update and reset actions."""
    http_host = environ.get("HTTP_HOST")

    if not http_host:
        LOG.warning("Could not find the host information.")
        return

    domain = http_host.split(":")[0]

    if _ttl_reached() or _reset_settings(domain):
        _perform_reset()
        _update_settings(domain)


def _update_settings(domain):
    """Update the general django settings with the found values in TenantOptions."""
    setattr(base_settings, "EDNX_TENANT_DOMAIN", domain)
    setattr(base_settings, "EDNX_TENANT_SETUP_TIME", datetime.now())
    options = TenantAwareSettings.get_tenant_options(domain)

    for key, value in six.iteritems(options):
        if isinstance(value, dict):
            merged = getattr(base_settings, key, {}).copy()
            merged.update(value)
            value = merged

        setattr(base_settings, key, value)


def _reset_settings(domain):
    """Verify if the given domain is different from EDNX_TENANT_DOMAIN."""
    return getattr(base_settings, "EDNX_TENANT_DOMAIN", "") != domain


def _perform_reset():
    """Defers to the original django.conf.settings to a new initialization."""
    base_settings._setup()  # pylint: disable=protected-access
    importlib.reload(conf)


def _ttl_reached():
    """Determines if the current settings object has been configured too long ago
    as defined in the MAX_CONFIG_OVERRIDE_SECONDS settings variable
    """
    try:
        return (datetime.now() - base_settings.EDNX_TENANT_SETUP_TIME).seconds > 300
    except AttributeError:
        pass

    return False
