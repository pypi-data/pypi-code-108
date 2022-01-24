# -*- coding: utf-8 -*-
from Acquisition import aq_get
from binascii import b2a_qp
from collective.geo.behaviour.interfaces import ICoordinates
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.utils import mergedTaggedValueList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.component import getUtility
from zope.component.interface import nameToInterface
from zope.i18n import translate
from zope.interface import implements
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from cpskin.locales import CPSkinMessageFactory as _


class BookingTypesFactory(object):
    """Vocabulary factory listing booking types"""
    implements(IVocabularyFactory)
    indexName = ''

    def __call__(self, context, query=None):
        items = [
            ('no_booking', _(u'No booking')),
            ('mandatory', _(u'Mandatory booking')),
            ('optional', _(u'Optional booking')),
        ]
        terms = [
            SimpleTerm(
                value=pair[0],
                token=pair[0],
                title=pair[1],
            ) for pair in items
        ]
        return SimpleVocabulary(terms)


BookingTypesVocabularyFactory = BookingTypesFactory()


class BaseTagsVocabulary(object):
    """Vocabulary factory listing all catalog keywords from specified tags"""
    implements(IVocabularyFactory)
    indexName = ''

    def __call__(self, context, query=None):
        site = api.portal.get()
        self.catalog = getToolByName(site, 'portal_catalog', None)
        if self.catalog is None:
            return SimpleVocabulary([])
        if self.indexName not in self.catalog._catalog.indexes.keys():
            return SimpleVocabulary([])
        index = self.catalog._catalog.getIndex(self.indexName)

        def safe_encode(term):
            if isinstance(term, unicode):
                # no need to use portal encoding for transitional encoding from
                # unicode to ascii. utf-8 should be fine.
                term = term.encode('utf-8')
            return term

        # Vocabulary term tokens *must* be 7 bit values, titles *must* be
        # unicode
        items = [
            SimpleTerm(safe_unicode(i), b2a_qp(
                safe_encode(i)), safe_unicode(i))
            for i in index._index
            if query is None or safe_encode(query) in safe_encode(i)
        ]
        return SimpleVocabulary(items)


class IStandardTagsVocabulary(BaseTagsVocabulary):
    """Vocabulary factory listing all catalog keywords from standard tags"""
    indexName = 'standardTags'


class IAmTagsVocabulary(BaseTagsVocabulary):
    """Vocabulary factory listing all catalog keywords from I am tags"""
    indexName = 'iamTags'


class ISearchTagsVocabulary(BaseTagsVocabulary):
    """Vocabulary factory listing all catalog keywords from I search tags"""
    indexName = 'isearchTags'


class HiddenTagsVocabulary(BaseTagsVocabulary):
    """Vocabulary factory listing all catalog keywords from hidden tags"""
    indexName = 'hiddenTags'

    def __call__(self, context, query=None):
        voc = super(HiddenTagsVocabulary, self).__call__(context, query)
        # Add a-la-une term if it does not already exist, aka still not used
        # for any document
        if u'a-la-une' not in voc.by_token and u'A la une' not in voc.by_token:
            simpleTerms = [term for term in voc]
            simpleTerms.append(SimpleTerm(u'a-la-une', title=u'A la une'))
            voc = SimpleVocabulary(simpleTerms)
        if u'homepage' not in voc.by_token:
            simpleTerms = [term for term in voc]
            simpleTerms.append(SimpleTerm(u'homepage', title=u'homepage'))
            voc = SimpleVocabulary(simpleTerms)
        return voc


IStandardTagsVocabularyFactory = IStandardTagsVocabulary()
IAmTagsVocabularyFactory = IAmTagsVocabulary()
ISearchTagsVocabularyFactory = ISearchTagsVocabulary()
HiddenTagsVocabularyFactory = HiddenTagsVocabulary()


class ContactFieldsFactory(object):
    """Vocabulary factory listing all fields from contacts"""
    implements(IVocabularyFactory)
    indexName = ''

    def __call__(self, context, query=None):
        results = []
        field_ids = []
        exclude = ['im_handle', 'use_parent_address']
        exclude_behaviors = ['plone.app.content.interfaces.INameFromTitle']
        behaviors = set()
        portal_types = api.portal.get_tool('portal_types')
        contact_portal_types = ['person', 'organization', 'position', 'held_position']  # noqa
        for contact_portal_type in contact_portal_types:
            schema = getUtility(
                IDexterityFTI, name=contact_portal_type).lookupSchema()
            fieldsets = mergedTaggedValueList(schema, FIELDSETS_KEY)
            for name, field in getFieldsInOrder(schema):
                if name not in exclude and name not in field_ids:
                    visible_name = u'{0}: {1}'.format(
                        contact_portal_type, field.title)
                    field_ids.append(name)
                    results.append((name, visible_name))

            portal_type = getattr(portal_types, contact_portal_type)
            behaviors.update(set(portal_type.behaviors))
        try:
            # remove duplicates photo
            results.remove(('photo', u'held_position: Photo'))
        except ValueError:
            pass
        for behavior in behaviors:
            if behavior not in exclude_behaviors:
                try:
                    # not able to get fields from IDirectoryContactDetails
                    # with nameToInterface(context, behavior)
                    if behavior == 'cpskin.core.behaviors.directorycontact.IDirectoryContactDetails':  # noqa
                        from cpskin.core.behaviors.directorycontact import (
                            IDirectoryContactDetails)
                        interface = IDirectoryContactDetails
                    else:
                        interface = nameToInterface(context, behavior)
                    fieldsets = mergedTaggedValueList(interface, FIELDSETS_KEY)
                    for name, field in getFieldsInOrder(interface):
                        if name not in exclude and name not in field_ids:
                            if not fieldsets:
                                visible_name = field.title
                            else:
                                fieldset = [
                                    fieldset for fieldset in fieldsets if name in fieldset.fields  # noqa
                                ][0]
                                field_ids.append(name)
                                visible_name = u'{0}: {1}'.format(
                                    fieldset.label, field.title)
                            results.append((name, visible_name))
                except:
                    pass
        items = [
            SimpleTerm(i, i, j)
            for i, j in results if j
        ]
        return SimpleVocabulary(items)


ContactFieldsVocabularyFactory = ContactFieldsFactory()


class GeoTypesFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context, query=None):
        portal_types = api.portal.get_tool('portal_types')
        request = aq_get(portal_types, 'REQUEST', None)
        if portal_types is None:
            return SimpleVocabulary([])

        items = []

        for k, v in portal_types.items():
            behaviors = getattr(v, 'behaviors', [])
            if ICoordinates.__identifier__ in behaviors:
                items.append(
                        (k, translate(v.Title(), context=request))
                )
        items.sort(key=lambda x: x[1])
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)


GeoTypesVocabularyFactory = GeoTypesFactory()


class ActionMenuEligibleFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context, query=None):
        root = api.portal.get()
        if 'fr' in root.objectIds():
            fr = getattr(root, 'fr')
            root = api.portal.get_navigation_root(fr)

        rootPath = '/'.join(root.getPhysicalPath())
        query = {}
        query['path'] = {'query': rootPath, 'depth': 1}
        query['portal_type'] = ['Folder']
        query['sort_on'] = 'sortable_title'
        query['is_default_page'] = False
        portal_catalog = api.portal.get_tool('portal_catalog')
        results = portal_catalog.searchResults(query)
        items = []
        for result in results:
            if not result.exclude_from_nav:
                continue
            items.append(
                SimpleTerm(
                    safe_unicode(result.id),
                    safe_unicode(result.id),
                    safe_unicode(result.Title),
                )
            )
        return SimpleVocabulary(items)


ActionMenuEligibleVocabularyFactory = ActionMenuEligibleFactory()


DISPLAY_TYPES = {
    u'slider-with-carousel': {
        'value': u'slider-with-carousel',
        'title': _(u'Slider with carousel'),
        'slider': True,
        'class': 'slider-carousel',
        'control-nav': False,
        'show-image': True,
        'show-carousel': True,
    },
    u'slider-with-elements-count-choice': {
        'value': u'slider-with-elements-count-choice',
        'title': _(u'Slider with elements count choice'),
        'slider': True,
        'class': 'slider-multiple',
        'control-nav': True,
        'show-image': True,
        'show-carousel': True,
    },
    u'slider-slick': {
        'value': u'slider-slick',
        'title': _(u'Slider Slick'),
        'slider': True,
        'class': 'slider-slick-mode',
        'control-nav': True,
        'show-image': True,
        'show-carousel': True,
        'slick': True,
    },
    u'slider-slick-full-width': {
        'value': u'slider-slick-full-width',
        'title': _(u'Slider Slick Full Width'),
        'slider': True,
        'class': 'slider-slick-mode',
        'control-nav': True,
        'show-image': True,
        'show-carousel': True,
        'variable-width': True,
        'slick': True,
    },
    u'unique-slider-with-title-carousel': {
        'value': u'unique-slider-with-title-carousel',
        'title': _(u'Unique slider with carousel on title'),
        'slider': True,
        'class': 'slider-unique-titre',
        'control-nav': True,
        'show-image': True,
        'show-carousel': True,
    },
    u'highlighted-unique-item': {
        'value': u'highlighted-unique-item',
        'title': _(u'Unique highlighted item'),
        'slider': False,
        'class': 'element-en-evidence',
        'control-nav': False,
        'show-image': True,
        'show-carousel': True,
    },
    u'slider-without-images': {
        'value': u'slider-without-images',
        'title': _(u'Slider without images'),
        'slider': True,
        'class': 'slider-without-images',
        'control-nav': True,
        'show-image': False,
        'show-carousel': False,
    },
    u'slider-vertical': {
        'value': u'slider-vertical',
        'title': _(u'Slider vertical'),
        'slider': True,
        'class': 'slider-vertical',
        'control-nav': None,
        'show-image': None,
        'show-carousel': None,
    },
    u'slider-count': {
        'value': u'slider-count',
        'title': _(u'Slider count'),
        'slider': True,
        'class': 'slider-count',
        'control-nav': True,
        'show-image': True,
        'show-carousel': False,
    },
    u'slider-top': {
        'value': u'slider-top',
        'title': _(u'Slider top'),
        'slider': True,
        'class': 'slider-top',
        'control-nav': True,
        'show-image': True,
        'show-carousel': False,
    },
}

items = [(disp['value'], disp['title']) for disp in DISPLAY_TYPES.values()]
items.sort(key=lambda x: x[1])
index_view_display_type = SimpleVocabulary(
    [SimpleTerm(i[0], i[0], i[1]) for i in items]
)


class SliderDisplayTypeVocabularyFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        use_slick = api.portal.get_registry_record(
            "cpskin.core.interfaces.ICPSkinSettings.use_slick",
            default=False,
        )
        items = [(disp['value'], disp['title']) for disp in DISPLAY_TYPES.values()]
        if use_slick is True:
            items = [e for e in items if DISPLAY_TYPES[e[0]].get("slick", False)]
        else:
            items = [e for e in items if not DISPLAY_TYPES[e[0]].get("slick", False)]
        items.sort(key=lambda x: x[1])
        return SimpleVocabulary(
            [SimpleTerm(i[0], i[0], i[1]) for i in items]
        )


SliderDisplayTypeVocabulary = SliderDisplayTypeVocabularyFactory()
