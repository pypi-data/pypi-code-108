from plone.restapi.services import Service
from plone import api

from redturtle.chefcookie.interfaces import IChefCookieSettings


class ChefCookieConfiguration(Service):
    def reply(self):
        """
        Return ChefCookie configuration from plone registry
        """
        registry_configuration = api.portal.get_registry_record(
            name="cc_configuration",
            interface=IChefCookieSettings,
            default={},
        )
        return registry_configuration
