# -*- coding: utf-8 -*-
"""This module contains the test for conf.py file."""
from django.contrib.sites.models import Site
from django.test import TestCase

from ecommerce_extensions.tenant.conf import TenantAwareSettings
from ecommerce_extensions.tenant.models import TenantOptions


def _make_site(domain, blob_str=None):
    """
    Returns a site object. If blob_str is passed, a TenantOptions object
    related to the site is created or updated with the blob, otherwise,
    existent TenantOptions object for the site is deleted
    """
    site, _ = Site.objects.get_or_create(domain=domain)

    if blob_str is not None:
        obj, _ = TenantOptions.objects.get_or_create(
            site=site
        )
        obj.options_blob = blob_str
        obj.save()
    else:
        TenantOptions.objects.filter(site=site).delete()

    return site


class TenantAwareSettingsTests(TestCase):
    """
    Test for Edunext tenant aware configurations
    """

    def test_get_site_by_domain_fail(self):
        """
        This method tests when a site is not found for a given domain.

        Expected behavior:
            - None is returned.
        """
        domain = "https://ilvermorny-school.com"

        site = TenantAwareSettings.get_site_by_domain(domain)

        self.assertIsNone(site)

    def test_get_site_by_domain(self):
        """
        This method tests when a site is found for a given domain.

        Expected behavior:
            -Return the right site.
        """
        domain = "https://howgarts-school.com"
        _make_site(domain)

        site = TenantAwareSettings.get_site_by_domain(domain)

        self.assertEqual(domain, site.domain)

    def test_get_tenant_options_no_site(self):
        """
        This method tests when there is no a site.

        Expected behavior:
            - Return empty dict.
        """
        domain = "https://ilvermorny-school.com"

        options = TenantAwareSettings.get_tenant_options(domain)

        self.assertEqual({}, options)

    def test_get_tenant_options_with_site(self):
        """
        This method tests when there is a site and the site has tenant options.

        Expected behavior:
            - Return dict with the option values.
        """
        site_options = {
            "Murtlap": "Murtlaps are ugly, hairless creatures.",
            "Billywig": "Billywigs are vivid sapphire blue Australian insects",
        }
        domain = "https://howgarts-school.com"
        _make_site(domain, site_options)

        options = TenantAwareSettings.get_tenant_options(domain)

        self.assertEqual(site_options, options)

    def test_get_tenant_options_without_options(self):
        """
        This method tests when there is a site but the site has no tenantoptions.

        Expected behavior:
            - Return empty dict.
        """
        domain = "https://howgarts-school.com"
        _make_site(domain)

        options = TenantAwareSettings.get_tenant_options(domain)

        self.assertEqual({}, options)
