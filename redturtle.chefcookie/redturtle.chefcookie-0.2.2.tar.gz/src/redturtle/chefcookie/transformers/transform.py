# -*- coding: utf-8 -*-
from lxml import etree, html
from plone.transformchain.interfaces import ITransform
from redturtle.chefcookie.defaults import iframe_placeholder
from repoze.xmliter.utils import getHTMLSerializer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from redturtle.chefcookie.interfaces import IChefCookieSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.component import queryAdapter
from redturtle.chefcookie.transformers import INodePlaceholder
from zope.component.interfaces import ComponentLookupError
from redturtle.chefcookie.interfaces import IRedturtleChefcookieLayer


@implementer(ITransform)
@adapter(Interface, IRedturtleChefcookieLayer)  # any context, any request
class ChefcookieIframeTransform(object):

    order = 8887  #  just one less than collective.lazysizes

    def __init__(self, published, request):
        self.published = published
        self.request = request
        self.chefcookie_registry_record = None

    def get_config_name(self, src):
        """
        if the src matches configured domains, return the config name
        """
        iframes_mapping = self.chefcookie_registry_record.iframes_mapping
        for mapping in iframes_mapping:
            name, domains = mapping.split("|")
            if not domains:
                continue
            domains = domains.split(",")
            for domain in domains:
                if domain in src:
                    return name
        return ""

    def transform_iframe(self, iframe):
        src = iframe.attrib.get("src")
        config_name = self.get_config_name(src=src)
        if not config_name:
            # no match, no need to mask it
            return

        placeholder = iframe_placeholder(name=config_name).prettify()
        iframe.attrib.pop("src")
        iframe.set("data-cc-src", src)
        iframe.set("data-cc-name", config_name)
        iframe.set("hidden", "true")
        placeholder = html.fromstring(placeholder)
        iframe.addprevious(placeholder)
        return

    def transformIterable(self, result, encoding):
        # we pass through this code for every call client made to server,
        # so also for resource.
        try:
            registry = getUtility(IRegistry)
        except ComponentLookupError:
            # as far as i can see sometimes this transform is called but it's
            # not able to get the utility. This simply hides useless exception
            # in log
            return
        if not registry:
            # and sometimes getUtility return None... we need to skip this as
            # well
            return

        content_type = self.request.response.getHeader("Content-Type")
        if not content_type or not content_type.startswith("text/html"):
            return

        if not self.published or self.published.__name__ in ["edit", "@@edit"]:
            return result

        try:
            result = getHTMLSerializer(result)
        except (AttributeError, TypeError, etree.ParseError):
            return

        self.chefcookie_registry_record = registry.forInterface(IChefCookieSettings)

        path = "//iframe"
        for iframe in result.tree.xpath(path):
            self.transform_iframe(iframe)

        path = "//a[@class='{}']"
        links_mapping = self.chefcookie_registry_record.links_mapping

        for configuration in links_mapping:
            provider, provider_class = configuration.split("|")
            for anchor in result.tree.xpath(path.format(provider_class)):
                ad = queryAdapter(
                    anchor,
                    interface=INodePlaceholder,
                    name="transform.{}".format(provider),
                )
                if ad:
                    ad.transform_anchor(provider, anchor)
        return result
