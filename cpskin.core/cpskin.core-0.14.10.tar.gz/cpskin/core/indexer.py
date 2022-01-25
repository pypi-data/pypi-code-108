# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective import dexteritytextindexer
from collective.contact.core.content.organization import IOrganization
from collective.taxonomy.interfaces import ITaxonomy
from OFS.interfaces import IItem
from plone.app.contenttypes.indexers import _unicode_save_string_concat
from plone.app.contenttypes.indexers import SearchableText_document
from plone.app.contenttypes.indexers import SearchableText_file
from plone.app.contenttypes.indexers import SearchableText_link
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import ILink
from plone.indexer.interfaces import IIndexer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.ZCatalog.interfaces import IZCatalog
from plone import api
from zope.component import adapts
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements

import logging
import six


try:
    from plone.dexterity.utils import safe_utf8
except ImportError:
    # Compatibility with Plone 4.3.2 / plone.dexterity 2.1.3
    from cpskin.core.utils import safe_utf8

logger = logging.getLogger('cpskin.core.indexer')


class DocumentExtender(object):
    adapts(IDocument)
    implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return SearchableText_document(self.context)()


class LinkExtender(object):
    adapts(ILink)
    implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return SearchableText_link(self.context)()


class FileExtender(object):
    adapts(IFile)
    implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return SearchableText_file(self.context)()


class OrganizationExtender(object):
    adapts(IOrganization)
    implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        rich_text_ids = ["activity", "informations_complementaires"]
        text_items = []
        for rich_text_id in rich_text_ids:
            rich_text = getattr(self.context, rich_text_id, None)
            if rich_text is None:
                continue
            transforms = getToolByName(self.context, "portal_transforms")
            raw = safe_unicode(rich_text.raw)
            if six.PY2:
                raw = raw.encode("utf-8", "replace")
            text_items.append(
                safe_unicode(
                    transforms.convertTo("text/plain", raw, mimetype=rich_text.mimeType)
                    .getData()
                    .strip()
                )
            )
        text = u" ".join(text_items)

        taxonomy_ids = api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.indexed_taxonomies')  # noqa
        taxonomy_ids = taxonomy_ids.split("\n")
        taxo_items = []
        lang = self.context.language
        for taxonomy_id in taxonomy_ids:
            field_name = taxonomy_id.replace("_", "")
            keys = getattr(self.context, "taxonomy_{0}".format(field_name), None)
            if not keys:
                continue
            try:
                taxonomy = getUtility(
                    ITaxonomy, name="collective.taxonomy.{0}".format(taxonomy_id)
                )
            except ComponentLookupError:
                taxonomy = getUtility(
                    ITaxonomy, name="collective.taxonomy.{0}".format(field_name)
                )
            for key in keys:
                try:
                    taxo_items.append(
                        safe_unicode(
                            taxonomy.translate(
                                key, context=self.context, target_language=lang
                            )
                        )
                    )
                except KeyError:
                    pass
        taxo_text = u" ".join(taxo_items)

        return _unicode_save_string_concat(
            u" ".join(
                (
                    safe_unicode(self.context.id),
                    safe_unicode(self.context.title) or u"",
                    safe_unicode(self.context.description) or u"",
                    text,
                    taxo_text,
                )
            )
        )


class BaseTagIndexer(object):
    """Index the specified tag
    """
    implements(IIndexer)
    adapts(IItem, IZCatalog)

    def __init__(self, context, catalog):
        self.context = context
        self.catalog = catalog

    def _getFieldContent(self, field):
        tags = getattr(aq_base(self.context), field, None)
        if not tags:
            raise AttributeError
        if field not in self.context.contentIds():
            encodedTags = tuple(safe_utf8(s) for s in tags)
            return encodedTags


class StandardTagIndexer(BaseTagIndexer):

    def __call__(self):
        return self._getFieldContent('standardTags')


class IAmTagIndexer(BaseTagIndexer):

    def __call__(self):
        return self._getFieldContent('iamTags')


class ISearchTagIndexer(BaseTagIndexer):

    def __call__(self):
        return self._getFieldContent('isearchTags')


class HiddenTagIndexer(BaseTagIndexer):

    def __call__(self):
        return self._getFieldContent('hiddenTags')
