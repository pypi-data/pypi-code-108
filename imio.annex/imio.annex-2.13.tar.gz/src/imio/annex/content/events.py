# -*- coding: utf-8 -*-
"""
imio.annex
----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.utils import allowedDocumentType
from collective.iconifiedcategory.utils import get_category_object
from collective.iconifiedcategory.utils import update_categorized_elements
from plone import api
from zope.event import notify

from imio.annex.events import AnnexFileChangedEvent
from imio.annex.content.annex import IAnnex


def annex_content_created(event):
    obj = event.object
    if not IAnnex.providedBy(obj):
        return
    notify(AnnexFileChangedEvent(obj, obj.file))


def annex_content_updated(event):
    obj = event.object
    if not IAnnex.providedBy(obj):
        return
    if obj.file._blob._p_blob_uncommitted is not None:
        notify(AnnexFileChangedEvent(obj, obj.file))


def annex_file_changed(event):
    obj = event.object
    settings = GlobalSettings(api.portal.get())
    if not allowedDocumentType(obj, settings.auto_layout_file_types):
        return
    # do something?


def annex_conversion_started(obj, event):
    container = obj.aq_parent
    if obj.UID() not in getattr(container, 'categorized_elements', {}):
        return
    target = get_category_object(obj, obj.content_category)
    update_categorized_elements(container, obj, target)


def annex_conversion_finished(obj, event):
    if not event.status:
        return
    container = obj.aq_parent
    if obj.UID() not in getattr(container, 'categorized_elements', {}):
        return
    target = get_category_object(obj, obj.content_category)
    update_categorized_elements(container, obj, target)
