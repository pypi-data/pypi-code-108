from redturtle.chefcookie.defaults import anchor_placeholder
from redturtle.chefcookie.transformers import INodePlaceholder
from zope.component import adapter
from zope.interface import implementer, Interface
from lxml import html
import logging

logger = logging.getLogger(__name__)


@adapter(Interface)
@implementer(INodePlaceholder)
class AnchorPlaceholder(object):
    def __init__(self, context):
        self.context = context

    def transform_anchor(self, provider_name, anchor):
        """ """
        href = anchor.attrib.get("href")
        anchor.attrib.pop("href")
        anchor.set("data-cc-name", provider_name)
        anchor.set("data-cc-href", href)
        anchor.set("hidden", "true")

        twitter = anchor.getnext()
        src = twitter.attrib.get("src")
        twitter.attrib.pop("src")
        # twitter.set("data-cc-name", provider_name)
        twitter.set("data-cc-src", src)
        twitter.set("hidden", "true")
        placeholder = anchor_placeholder(provider_name).prettify()
        anchor.addprevious(html.fromstring(placeholder))
