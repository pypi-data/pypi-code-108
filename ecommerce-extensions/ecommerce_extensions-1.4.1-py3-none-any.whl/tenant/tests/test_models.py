"""
Test file for SiteOptions model.
"""
from django.contrib.sites.models import Site
from django.test import TestCase
from mock import patch

from ecommerce_extensions.tenant.models import TenantOptions, clear_site_cache


def _make_site_options(blob_str, site_id=1):
    site, _ = Site.objects.get_or_create(id=site_id)

    return TenantOptions(
        site=site,
        options_blob=blob_str,
    )


class TenantOptionsTests(TestCase):
    """
    Test class for TenantOptions Model.
    """
    def test_options_blob_validation_success(self):
        """
        Tests that validation passes when creating a field with a correct value
        """
        site_options = _make_site_options({"ThisIs": "ValidJson"})
        site_options.clean_fields()

    @patch.object(Site, "objects")
    def test_clear_site_cache(self, objects_mock):
        """
        This method tests that Site.objects.clear_cache() is called

        Expected behavior:
            - Site.objects.clear_cache() is called
        """
        clear_site_cache("TenantOptions")

        objects_mock.clear_cache.called_once()
