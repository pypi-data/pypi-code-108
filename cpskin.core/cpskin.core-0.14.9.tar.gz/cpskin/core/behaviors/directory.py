# -*- coding: utf-8 -*-
from cpskin.locales import CPSkinMessageFactory as _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class ICpskinDirectoryViewSettings(model.Schema):
    model.fieldset(
        'directoryview',
        label=_(
            u'Directory view'),
        fields=(
            'taxonomy_category',
            'show_organization_images',
            'organization_image_scale',
        ),
    )

    taxonomy_category = schema.TextLine(
        title=_(u'Which taxonomy id should be use to display category'),
        description=_(u'Please write which taxonomy id should be used.'),
        default=u'',
        required=False,
    )

    show_organization_images = schema.Bool(
        title=_(u'Show organizations images'),
        description=_(u'Do you want to show images for organizations preview in directory ?'),  # noqa
        required=False,
        default=False,
    )

    organization_image_scale = schema.Choice(
        title=_(u'Which image scale use for organizations preview in directory ?'),  # noqa
        description=_(u'Please select the scale.'),
        required=False,
        default='mini',
        vocabulary=u'plone.app.vocabularies.ImagesScales'
    )
