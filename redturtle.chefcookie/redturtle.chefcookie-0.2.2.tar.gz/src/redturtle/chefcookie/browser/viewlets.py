# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize import ram
from redturtle.chefcookie.interfaces import IChefCookieSettings
from time import time

import pkg_resources


CHEFCOOKIE_URL = "{portal_url}/++resource++redturtle.chefcookie/chefcookie/chefcookie.min.js?v={version}"
RT_CHEFCOOKIE_URL = (
    "{portal_url}/++resource++redturtle.chefcookie/{type}.js?v={version}"
)
CONFIG_URL = "{portal_url}/{name}?v={version}"


class GetChefcookieJs(ViewletBase):
    """ """

    @ram.cache(lambda *args: time() // (60 * 60))
    def get_version(self):
        return pkg_resources.get_distribution("redturtle.chefcookie").version

    def have_chefcookie_configuration(self):
        try:
            self.context.portal_registry.forInterface(IChefCookieSettings)
            return True
        except Exception:
            return False

    def get_js_urls(self):
        """
        return the list of javascript files
        """
        version = self.get_version()
        portal_url = api.portal.get().portal_url()

        return (
            CHEFCOOKIE_URL.format(portal_url=portal_url, version=version),
            RT_CHEFCOOKIE_URL.format(
                portal_url=portal_url,
                type=self.get_type(),
                version=version,
            ),
            CONFIG_URL.format(
                portal_url=portal_url,
                name="cookie_config.js",
                version=version,
            ),
        )

    def get_css_link(self):
        return "{portal_url}/++resource++redturtle.chefcookie/styles.css?v={version}".format(
            portal_url=api.portal.get().portal_url(), version=self.get_version()
        )

    def get_type(self):

        only_technical_cookies = api.portal.get_registry_record(
            name="only_technical_cookies", interface=IChefCookieSettings
        )

        type = "redturtle_chefcookie"
        if only_technical_cookies:
            type = "redturtle_chefcookie_tech"
        return type
