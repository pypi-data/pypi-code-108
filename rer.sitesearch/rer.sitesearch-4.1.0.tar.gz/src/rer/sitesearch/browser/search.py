# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone import api
from plone.memoize import ram
from time import time
from Products.CMFPlone.resources import add_bundle_on_request
import logging
import pkg_resources

logger = logging.getLogger(__name__)


JS_TEMPLATE = (
    "{portal_url}/++plone++rer.sitesearch/dist/{env_mode}/{name}.js?v={version}"  # noqa
)
CSS_TEMPLATE = "{portal_url}/++plone++rer.sitesearch/dist/{env_mode}/{name}.css?v={version}"  # noqa


class View(BrowserView):
    """ """

    def __call__(self):
        add_bundle_on_request(self.request, "sitesearch-bundle")
        return super(View, self).__call__()

    @ram.cache(lambda *args: time() // (60 * 60))
    def get_version(self):
        return pkg_resources.get_distribution("rer.sitesearch").version

    def get_env_mode(self):
        return (
            api.portal.get_registry_record("plone.resources.development")
            and "dev"  # noqa
            or "prod"  # noqa
        )

    def get_resource_js(self, name="main"):
        return JS_TEMPLATE.format(
            portal_url=api.portal.get().absolute_url(),
            env_mode=self.get_env_mode(),
            name=name,
            version=self.get_version(),
        )

    def get_resource_css(self, name="main"):
        return CSS_TEMPLATE.format(
            portal_url=api.portal.get().absolute_url(),
            env_mode=self.get_env_mode(),
            name=name,
            version=self.get_version(),
        )
