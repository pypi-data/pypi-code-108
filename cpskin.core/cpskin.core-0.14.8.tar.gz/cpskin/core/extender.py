# -*- coding: utf-8 -*-
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from cpskin.core.interfaces import ICPSkinCoreLayer
from cpskin.locales import CPSkinMessageFactory as _
from Products.Archetypes import public as atapi
from Products.Archetypes.interfaces import IBaseContent
from Products.CMFCore import permissions as zope_permissions
from zope.component import adapter
from zope.interface import implementer

import permissions


class ExtensionStandardTagsField(ExtensionField, atapi.LinesField):
    """Derivate from Archetypes basic LinesField"""


class ExtensionIAmTagsField(ExtensionField, atapi.LinesField):
    """Derivate from Archetypes basic LinesField"""


class ExtensionISearchTagsField(ExtensionField, atapi.LinesField):
    """Derivate from Archetypes basic LinesField"""


class ExtensionHiddenTagsField(ExtensionField, atapi.LinesField):
    """Derivate from Archetypes basic LinesField"""


@adapter(IBaseContent)
@implementer(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
class ContentExtender(object):
    layer = ICPSkinCoreLayer

    fields = [
        ExtensionStandardTagsField(
            'standardTags',
            multiValued=1,
            searchable=False,
            schemata='categorization',
            languageIndependent=True,
            widget=atapi.KeywordWidget(
                label=_(u'label_standard_tags', default=u'Standard Tags'),
                description=_(u'help_standard_tags',
                              default=u'Standard Tags are used for webmaster '
                                      u'organization of content.'),
            ),
            read_permission=zope_permissions.View,
            write_permission=permissions.CPSkinEditKeywords,
        ),
        ExtensionIAmTagsField(
            'iamTags',
            multiValued=1,
            searchable=False,
            schemata='categorization',
            languageIndependent=True,
            widget=atapi.KeywordWidget(
                label=_(u'label_iam_tags', default=u'I Am Tags'),
                description=_(u'help_iam_tags',
                              default=u'I Am Tags are used for webmaster '
                                      u'organization of content.'),
            ),
            read_permission=zope_permissions.View,
            write_permission=permissions.CPSkinEditKeywords,
        ),
        ExtensionISearchTagsField(
            'isearchTags',
            multiValued=1,
            searchable=False,
            schemata='categorization',
            languageIndependent=True,
            widget=atapi.KeywordWidget(
                label=_(u'label_isearch_tags', default=u'I Search Tags'),
                description=_(u'help_isearch_tags',
                              default=u'I Search Tags are used for webmaster '
                                      u'organization of content.'),
            ),
            read_permission=zope_permissions.View,
            write_permission=permissions.CPSkinEditKeywords,
        ),
        ExtensionHiddenTagsField(
            'hiddenTags',
            multiValued=1,
            searchable=False,
            schemata='categorization',
            languageIndependent=True,
            widget=atapi.KeywordWidget(
                label=_(u'label_hidden_tags', default=u'Hidden Tags'),
                description=_(u'help_hidden_tags',
                              default=u'Hidden Tags are used for webmaster '
                                      u'organization of content.'),
            ),
            read_permission=zope_permissions.View,
            write_permission=permissions.CPSkinEditKeywords,
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        """
        Make sure that tags are just after subject in categorization schemata
        """
        if 'subject' in schematas['categorization']:
            insertAfterFieldIndex = schematas['categorization'].index('subject')  # noqa
        else:
            insertAfterFieldIndex = -1

        standardTagsIndex = schematas['categorization'].index('standardTags')
        schematas['categorization'].insert(
                           insertAfterFieldIndex + 1,
                           schematas['categorization'].pop(standardTagsIndex)
                           )
        iAmTagsIndex = schematas['categorization'].index('iamTags')
        schematas['categorization'].insert(
                           insertAfterFieldIndex + 2,
                           schematas['categorization'].pop(iAmTagsIndex)
                           )
        iSearchTagsIndex = schematas['categorization'].index('isearchTags')
        schematas['categorization'].insert(
                           insertAfterFieldIndex + 3,
                           schematas['categorization'].pop(iSearchTagsIndex)
                           )
        hiddenTagsIndex = schematas['categorization'].index('hiddenTags')
        schematas['categorization'].insert(
                           insertAfterFieldIndex + 4,
                           schematas['categorization'].pop(hiddenTagsIndex)
                           )
        return schematas

    def getFields(self):
        return self.fields
