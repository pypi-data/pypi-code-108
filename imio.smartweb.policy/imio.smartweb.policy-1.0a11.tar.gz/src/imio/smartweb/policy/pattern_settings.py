# -*- coding: utf-8 -*-

from Products.CMFPlone.patterns.settings import PatternSettingsAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory

import json


EXCLUDED_TINY_MCE_SCALES = ["tile", "icon", "listing"]


class SmartwebPatternSettingsAdapter(PatternSettingsAdapter):
    """
    Provides only useful scales for Tiny MCE image modal.
    """

    @property
    def image_scales(self):
        factory = getUtility(IVocabularyFactory, "plone.app.vocabularies.ImagesScales")
        vocabulary = factory(self.context)
        ret = [
            {"title": translate(it.title), "value": it.value}
            for it in vocabulary
            if it.value not in EXCLUDED_TINY_MCE_SCALES
        ]
        ret = sorted(ret, key=lambda it: it["title"])
        return json.dumps(ret)
