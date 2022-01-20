# coding: utf-8
from __future__ import unicode_literals

import posixpath

from django.conf import settings

TEMPLATE_PREFIX = getattr(
    settings,
    "MODELTRANSLATION_ROSETTA_TEMPLATE_PREFIX",
    "modeltranslation_rosetta/default/",
)


def get_template(name):
    return posixpath.join(TEMPLATE_PREFIX, name)
