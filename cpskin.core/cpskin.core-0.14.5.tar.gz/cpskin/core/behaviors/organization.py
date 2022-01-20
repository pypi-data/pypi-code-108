# -*- coding: utf-8 -*-
from cpskin.locales import CPSkinMessageFactory as _
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedImage
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope.interface import provider


@provider(IFormFieldProvider)
class IOrganizationImages(model.Schema):

    fieldset(
        'images',
        label=_(u'Images'),
        fields=['image1', 'image2'],
    )

    image1 = NamedImage(
        title=_('Image 1'),
        description=_(u'This image is shown on directory view.'),
        required=False,
    )

    image2 = NamedImage(
        title=_('Image 2'),
        description=_(u'This image is shown on directory view when mouse hovers the card.'),  # noqa
        required=False,
    )
