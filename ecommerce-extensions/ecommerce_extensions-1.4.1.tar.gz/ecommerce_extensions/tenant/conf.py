"""
This file implements a class which is a handy utility to make any
call to the settings completely site aware by replacing the:

from django.conf import settings

with:

from ecommerce.edunext.conf import settings

"""
import logging

from django.contrib.sites.models import Site

from ecommerce_extensions.tenant.models import TenantOptions

LOG = logging.getLogger(__name__)


class TenantAwareSettings():
    """
    This class is a proxy object of the settings object from django.
    It will try to get a value from the microsite and default to the
    django settings
    """

    @classmethod
    def get_site_by_domain(cls, domain):
        """
        Returns the associated site for the given domain.

        Arguments:
            domain: String.

        Return:
            django.contrib.sites.models.Site instance.
        """
        try:
            return Site.objects.get(domain=domain)
        except Site.DoesNotExist:  # pylint: disable=no-member
            return None

    @classmethod
    def get_tenant_options(cls, domain):
        """
        This method retrieves the edunext options for current request site
        """
        site = cls.get_site_by_domain(domain)

        try:
            options = site.tenantoptions.options_blob if site else {}
        except TenantOptions.DoesNotExist:  # pylint: disable=no-member
            LOG.warning("The site %s has no associated TenantOptions register.", site.domain)
            options = {}

        return options
