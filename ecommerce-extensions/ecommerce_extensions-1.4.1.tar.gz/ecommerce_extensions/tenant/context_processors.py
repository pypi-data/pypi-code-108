# -*- coding: utf-8 -*-
"""
This file contains django context_processors needed by edunext.
"""
import logging

from ecommerce_extensions.tenant.extra_html import process_html
from ecommerce_extensions.tenant.extra_scripts import process_scripts
from ecommerce_extensions.tenant.models import TenantOptions

LOG = logging.getLogger(__name__)


def theme_options(request):
    """
    This context processor lets us add extra context to the themeable templates
    in a way that is unobtrusive and easy to migrate between releases
    """
    try:
        options = request.site.tenantoptions.options_blob
    except TenantOptions.DoesNotExist:  # pylint: disable=no-member
        LOG.warning("The site %s has no associated TenantOptions register.", request.site.domain)
        options = {}

    try:
        site_theme_name = request.site_theme.theme_dir_name
    except AttributeError:
        site_theme_name = None

    theme_options_values = options.get("THEME_OPTIONS", {})

    return {
        "theme_dir_name": site_theme_name,
        "site_configuration": request.site.siteconfiguration,
        "options": options,
        "scripts": process_scripts(request.path_info, theme_options_values),
        "html": process_html(request.path_info, theme_options_values)
    }
