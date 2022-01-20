from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from z3c.form.interfaces import IForm


class IRERSiteSearchLayer(IDefaultBrowserLayer):
    """A layer specific for rer.sitesearch"""


class IRerSiteSearchSettingsForm(IForm):
    """
    Marker interface
    """
