# -*- coding: utf-8 -*-
from cpskin.locales import CPSkinMessageFactory as _
from plone.autoform.interfaces import IFormFieldProvider
from plone.event.interfaces import IEvent
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class ICpskinEventViewSettings(model.Schema):
    model.fieldset(
        'eventview',
        label=_(
            u'Event view'),
        fields=(
            'image_banner',
        ),
    )

    model.fieldset(
        'eventview',
        label=_(
            u'Event view'),
        fields=(
            'image_header',
        ),
    )

    image_banner = namedfile.NamedBlobImage(
        title=_(u'label_bannerimage', default=u'Banner image'),
        description=_(
            u'help_bannerimage',
            default=u'Image used as banner replacement when viewing this event.<br/>This image can be crop into banner format'
        ),
        required=False,
    )

    image_header = namedfile.NamedBlobImage(
        title=_(u'label_headerimage', default=u'Header image'),
        description=_(
            u'help_headerimage',
            default=u'Image used as header in the event.<br/>This image can be crop into banner_event or banner format if banner_event is not available.'
        ),
        required=False,
    )

@implementer(ICpskinEventViewSettings)
@adapter(IEvent)
class CpskinEventViewSettings(object):

    def __init__(self, context):
        self.context = context
