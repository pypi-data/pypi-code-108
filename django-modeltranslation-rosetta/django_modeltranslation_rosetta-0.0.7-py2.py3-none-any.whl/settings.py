# coding: utf-8
from __future__ import unicode_literals

from django.conf import settings

LANGUAGE_CODES = [code for code, name in settings.LANGUAGES]
LANGUAGES = list(settings.LANGUAGES)

DEFAULT_FROM_LANG = getattr(
    settings, "MODELTRANSLATION_ROSETTA_FROM_LANG", LANGUAGE_CODES[0]
)
DEFAULT_TO_LANG = getattr(
    settings, "MODELTRANSLATION_ROSETTA_TO_LANG", LANGUAGE_CODES[1]
)

EXPORT_FILTERS = getattr(settings, "MODELTRANSLATION_ROSETTA_EXPORT_FILTERS", {})
