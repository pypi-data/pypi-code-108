# -*- coding: utf-8 -*-
"""
cpskin.core
-----------

Created by mpeeters
:copyright: (c) 2015 by Affinitic SPRL
:license: GPL, see LICENCE.txt for more details.
"""
from cpskin.locales import CPSkinMessageFactory as _
from eea.facetednavigation import EEAMessageFactory as EEAMF
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import logging


logger = logging.getLogger('eea.facetednavigation.widgets.portlet')

EditSchema = Schema((
    StringField(
        'values',
        schemata='default',
        required=True,
        vocabulary_factory='cpskin.vocabularies.faceted_layout',
        widget=MultiSelectionWidget(
            label=_(u'Views'),
            i18n_domain='cpskin',
        ),
    ),
    StringField(
        'default',
        schemata='default',
        widget=StringWidget(
            size=25,
            label=EEAMF(u'Default value'),
            description=EEAMF(u'Default selected item'),
            i18n_domain='eea',
        )
    ),
))


class Widget(AbstractWidget):
    """ Widget
    """
    # Widget properties
    widget_type = 'layout'
    widget_label = _('Layout selection')
    view_js = '++resource++cpskin.faceted.widgets.layout.view.js'
    edit_js = '++resource++cpskin.faceted.widgets.layout.edit.js'
    view_css = '++resource++cpskin.faceted.widgets.layout.view.css'
    edit_css = '++resource++cpskin.faceted.widgets.layout.edit.css'

    index = ZopeTwoPageTemplateFile('layout.pt', globals())
    edit_schema = AbstractWidget.edit_schema.copy() + EditSchema
    edit_schema['title'].default = 'Layout'

    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        self.voc = getUtility(
            IVocabularyFactory,
            name='cpskin.vocabularies.faceted_layout',
        )(self.context)

    @property
    def values(self):
        return [self.voc.getTerm(v) for v in self.data.get('values', [])]
