from collective.iconifieddocumentactions.interfaces import IIconifiedDocumentActionsLayer
from cpskin.core.interfaces import ICPSkinCoreLayer
from cpskin.locales import CPSkinMessageFactory as _
from plone.app.event.interfaces import IBrowserLayer
from zope import schema
from zope.interface import Interface


class ICPSkinNewDreamLayer(ICPSkinCoreLayer, IIconifiedDocumentActionsLayer, IBrowserLayer):
    """
    Marker interface that defines a ZTK browser layer.
    """


class INewDreamSettings(Interface):
    """
    Settings for New Dream
    """
    breadcrumbs_below_title = schema.Bool(
        title=_(u'Breadcrumbs below title'),
        description=_(u'Show breadcrumbs below page title?'),
        required=False,
        default=False
    )
