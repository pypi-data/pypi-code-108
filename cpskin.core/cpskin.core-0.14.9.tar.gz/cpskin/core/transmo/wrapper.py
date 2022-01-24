# -*- coding: utf-8 -*-
from collective.geo.behaviour.behaviour import Coordinates
from collective.geo.geographer.interfaces import IGeoreferenceable
from collective.geo.geographer.interfaces import IWriteGeoreferenced
from collective.jsonify.wrapper import Wrapper
from cpskin.core.interfaces import IAlbumCollection
from cpskin.core.interfaces import IBannerActivated
from cpskin.core.interfaces import IFolderViewSelectedContent
from cpskin.core.interfaces import IFolderViewWithBigImages
from cpskin.core.interfaces import ILocalBannerActivated
from cpskin.core.interfaces import IMediaActivated
from cpskin.core.interfaces import IVideoCollection
from cpskin.core.viewlets.interfaces import IViewletMenuToolsBox
from cpskin.core.viewlets.interfaces import IViewletMenuToolsFaceted
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.portlets.exportimport.interfaces import IPortletAssignmentExportImportHandler  # noqa
from plone.app.portlets.exportimport.portlets import PropertyPortletAssignmentExportImportHandler  # noqa
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletManager
from xml.dom import minidom
from zope.component import getUtilitiesFor
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import providedBy

import base64
import DateTime
import os


class ISerializer(Interface):
    def __call__(value, filestore, extra=None):
        """Convert to a serializable reprentation"""


class Wrapper(Wrapper):
    """ Gets the data in a format that can be used by the
        transmogrifier blueprints in collective.jsonmigrator
    """

    def __init__(self, context):
        pc = api.portal.get_tool('portal_catalog')
        self.has_tg = 'TranslationGroup' in pc.indexes()
        super(Wrapper, self).__init__(context)

    def is_multilingual(self):
        """return true if there is fr folder on top nav"""
        portal = api.portal.get()
        return 'fr' in portal.contentIds()

    def get_archetypes_fields(self):
        """ If Archetypes is used then dump schema
        """

        try:
            from Products.Archetypes.interfaces import IBaseObject
            if not IBaseObject.providedBy(self.context):
                return
        except:
            return
        if self.is_multilingual() and self.has_tg and len(ITranslationManager(self.context).get_translations()) > 1:  # noqa
            translations = ITranslationManager(self.context).get_translations()
            portal_level = len(self.portal.getPhysicalPath())
            trans = {}
            for lang, obj in translations.items():
                trans[lang] = '/'+'/'.join(
                    obj.getPhysicalPath()[portal_level:])
            self['translations'] = trans

        fields = self.context.Schema().fields()
        for field in fields:
            fieldname = unicode(field.__name__)
            type_ = field.__class__.__name__

            fieldnames = [
                'StringField', 'BooleanField', 'LinesField',
                'IntegerField', 'TextField', 'SimpleDataGridField',
                'FloatField', 'FixedPointField', 'TALESString',
                'TALESLines', 'ZPTField', 'DataGridField', 'EmailField',
                '_StringExtensionField', 'LeadimageCaptionField',
                'ExtensionStandardTagsField', 'ExtensionHiddenTagsField',
                'ExtensionIAmTagsField', 'ExtensionISearchTagsField',
                'CheckboxField'
            ]

            if type_ in fieldnames:
                try:
                    value = field.getRaw(self.context)
                except AttributeError:
                    value = self._get_at_field_value(field)

                if callable(value) is True:
                    value = value()

                if value and type_ in ['StringField', 'TextField']:
                    try:
                        value = self.decode(value)
                    except AttributeError:
                        # maybe an int?
                        value = unicode(value)
                    except Exception, e:
                        raise Exception('problems with %s: %s' % (
                            self.context.absolute_url(), str(e))
                        )
                elif value and type_ == 'DataGridField':
                    for i, row in enumerate(value):
                        for col_key in row.keys():
                            col_value = row[col_key]
                            if type(col_value) in (unicode, str):
                                value[i][col_key] = self.decode(col_value)

                try:
                    ct = field.getContentType(self.context)
                except AttributeError:
                    ct = ''
                self[unicode(fieldname)] = value
                self[unicode('_content_type_') + fieldname] = ct

            elif type_ in ['DateTimeField']:
                value = self._get_at_field_value(field)
                if value:
                    value = DateTime.DateTime.strftime(value, '%Y-%m-%d %H:%M')
                    # value = str(self._get_at_field_value(field))
                    # value = self._get_at_field_value(field).ISO8601()
                    self[unicode(fieldname)] = value

            elif type_ in [
                'ImageField',
                'FileField',
                'AttachmentField',
                'ExtensionBlobField',
                'LeadimageBlobImageField'
            ]:

                fieldname = unicode('_datafield_' + fieldname)
                value = self._get_at_field_value(field)
                value2 = value

                if not isinstance(value, str):
                    data = getattr(value, 'data')
                    if data is None:
                        continue
                    if isinstance(data, str):
                        value = base64.b64encode(value.data)
                    else:
                        value = ''
                        while data is not None:
                            value += data.data
                            data = data.next
                        value = base64.b64encode(value)

                try:
                    max_filesize = int(
                        os.environ.get('JSONIFY_MAX_FILESIZE', 20000000)
                    )
                except ValueError:
                    max_filesize = 20000000

                if value and len(value) < max_filesize:
                    size = value2.getSize()
                    try:
                        fname = field.getFilename(self.context)
                    except AttributeError:
                        fname = value2.getFilename()

                    try:
                        fname = self.decode(fname)
                    except AttributeError:
                        # maybe an int?
                        fname = unicode(fname)
                    except Exception, e:
                        raise Exception(
                            'problems with %s: %s' % (
                                self.context.absolute_url(), str(e)
                            )
                        )

                    try:
                        ctype = field.getContentType(self.context)
                    except AttributeError:
                        ctype = value2.getContentType()

                    self[fieldname] = {
                        'data': value,
                        'size': size,
                        'filename': fname or '',
                        'content_type': ctype,
                        'encoding': 'base64'
                    }

            elif type_ in ['QueryField']:
                value = field.getRaw(self.context)
                self[fieldname] = [dict(q) for q in value]

            elif type_ in ['ReferenceField', 'OrderableReferenceField']:
                pass

            elif type_ in ['ComputedField']:
                continue
            else:
                raise TypeError('Unknown field type for ArchetypesWrapper in '
                        '%s %s in %s' % (type_, fieldname, self.context.absolute_url()))  # noqa

    def get_cpskin_interfaces(self):
        from cpskin.menu.interfaces import IDirectAccess
        from cpskin.menu.interfaces import IFourthLevelNavigation
        interfaces = [
            IAlbumCollection,
            IBannerActivated,
            IFolderViewSelectedContent,
            IFolderViewWithBigImages,
            ILocalBannerActivated,
            IMediaActivated,
            IVideoCollection,
            IViewletMenuToolsBox,
            IViewletMenuToolsFaceted,
            IDirectAccess,
            IFourthLevelNavigation
        ]
        inter = []
        for interface in interfaces:
            if interface.providedBy(self.context):
                inter.append(interface.__identifier__)
        self['cpskin_interfaces'] = inter

    def get_facted_criteria(self):
        from eea.facetednavigation.criteria.handler import Criteria
        from eea.facetednavigation.criteria.interfaces import ICriteria
        from eea.facetednavigation.indexes.language.interfaces import ILanguageWidgetAdapter  # noqa
        from eea.facetednavigation.interfaces import IFacetedNavigable
        from eea.facetednavigation.settings.interfaces import IDisableSmartFacets  # noqa
        from eea.facetednavigation.settings.interfaces import IHidePloneLeftColumn  # noqa
        from eea.facetednavigation.settings.interfaces import IHidePloneRightColumn  # noqa
        from eea.facetednavigation.subtypes.interfaces import IFacetedWrapper
        from eea.facetednavigation.views.interfaces import IViewsInfo
        from eea.facetednavigation.widgets.alphabetic.interfaces import IAlphabeticWidget  # noqa
        from eea.facetednavigation.widgets.interfaces import ICriterion
        from eea.facetednavigation.widgets.interfaces import IWidget
        from eea.facetednavigation.widgets.interfaces import IWidgetsInfo
        from eea.facetednavigation.widgets.resultsfilter.interfaces import IResultsFilterWidget  # noqa

        interfaces = [
            IFacetedNavigable,
            IDisableSmartFacets,
            IHidePloneLeftColumn,
            IHidePloneRightColumn,
            ICriteria,
            ILanguageWidgetAdapter,
            IFacetedWrapper,
            IViewsInfo,
            IAlphabeticWidget,
            ICriterion,
            IWidget,
            IWidgetsInfo,
            IResultsFilterWidget,
        ]
        inter = []
        for interface in interfaces:
            if interface.providedBy(self.context):
                inter.append(interface.__identifier__)
        self['faceted_interfaces'] = inter
        if IFacetedNavigable.providedBy(self.context):
            criteria = Criteria(self.context)
            criterias = []
            for crit in criteria.criteria:
                criterias.append(crit.__dict__)
            self['faceted_criteria'] = criterias

    def get_dexterity_fields(self):
        """If dexterity is used then extract fields.
        """
        try:
            from plone.dexterity.interfaces import IDexterityContent
            if not self.providedBy(IDexterityContent, self.context):
                return
            from plone.dexterity.utils import iterSchemata
            # from plone.uuid.interfaces import IUUID
            from zope.schema import getFieldsInOrder
            from datetime import date
        except:
            return
        # get translation if thereis
        try:
            if self.is_multilingual() and self.has_tg and len(ITranslationManager(self.context).get_translations()) > 1:
                trans = ITranslationManager(self.context).get_translations()
            else:
                trans = {}
        except:
            trans = {}
        if len(trans) > 1:
            translations = ITranslationManager(self.context).get_translations()
            portal_level = len(self.portal.getPhysicalPath())
            trans = {}
            for lang, obj in translations.items():
                trans[lang] = '/'+'/'.join(
                    obj.getPhysicalPath()[portal_level:])
            self['translations'] = trans
        # get all fields for this obj
        for schemata in iterSchemata(self.context):
            for fieldname, field in getFieldsInOrder(schemata):
                try:
                    value = field.get(schemata(self.context))
                    # value = getattr(context, name).__class__.__name__
                except AttributeError:
                    continue
                if value is field.missing_value:
                    continue

                field_type = field.__class__.__name__

                if field_type in ('RichText',):
                    # XXX: content_type missing
                    try:
                        value = unicode(value.raw)
                    except:
                        value = u''

                elif field_type in (
                    'NamedImage',
                    'NamedBlobImage',
                    'NamedFile',
                    'NamedBlobFile'
                ):
                    # still to test above with NamedFile & NamedBlobFile
                    fieldname = unicode('_datafield_' + fieldname)

                    if hasattr(value, 'open'):
                        data = value.open().read()
                    else:
                        data = value.data

                    try:
                        max_filesize = int(
                            os.environ.get('JSONIFY_MAX_FILESIZE', 20000000))
                    except ValueError:
                        max_filesize = 20000000

                    if data and len(data) > max_filesize:
                        continue

                    import base64
                    ctype = value.contentType
                    size = value.getSize()
                    dvalue = {
                        'data': base64.b64encode(data),
                        'size': size,
                        'filename': value.filename or '',
                        'content_type': ctype,
                        'encoding': 'base64'
                    }
                    value = dvalue

                elif field_type == 'GeolocationField':
                    # super special plone.formwidget.geolocation case
                    self['latitude'] = getattr(value, 'latitude', 0)
                    self['longitude'] = getattr(value, 'longitude', 0)
                    continue
                elif field_type == 'ContactChoice':
                    pos = getattr(self.context, fieldname, None)
                    if pos:
                        value = unicode(pos.to_path)
                elif isinstance(value, date):
                    value = value.isoformat()

                # elif field_type in ('TextLine',):
                else:
                    BASIC_TYPES = (
                        unicode, int, long, float, bool, type(None),
                        list, tuple, dict
                    )
                    if type(value) in BASIC_TYPES:
                        pass
                    else:
                        # E.g. DateTime or datetime are nicely representated
                        value = unicode(value)

                self[unicode(fieldname)] = value

    def get_portlets(self):
        """If there is portlets then extract its.
        """

        self.doc = minidom.Document()
        self.portlet_schemata = dict([(iface, name,) for name, iface in getUtilitiesFor(IPortletTypeInterface)])  # noqa
        self.portlet_managers = list(getUtilitiesFor(IPortletManager))
        if ILocalPortletAssignable.providedBy(self.context):
            data = None

            root = self.doc.createElement('portlets')

            for elem in self.exportAssignments(self.context):
                root.appendChild(elem)
            for elem in self.exportBlacklists(self.context):
                root.appendChild(elem)
            if root.hasChildNodes():
                self.doc.appendChild(root)
                data = self.doc.toprettyxml(indent='  ', encoding='utf-8')
                self.doc.unlink()

            if data:
                self['portlets'] = data

    def exportAssignments(self, obj):
        assignments = []
        for manager_name, manager in self.portlet_managers:
            mapping = queryMultiAdapter(
                (obj, manager),
                IPortletAssignmentMapping)
            if mapping is None:
                continue

            mapping = mapping.__of__(obj)
            if len(mapping.items()) > 0:
                for name, assignment in mapping.items():
                    type_ = None
                    for schema in providedBy(assignment).flattened():
                        type_ = self.portlet_schemata.get(schema, None)
                        if type_ is not None:
                            break

                    if type_ is not None:
                        child = self.doc.createElement('assignment')
                        child.setAttribute('manager', manager_name)
                        child.setAttribute('category', CONTEXT_CATEGORY)
                        child.setAttribute('key', '/'.join(
                            obj.getPhysicalPath()))
                        child.setAttribute('type', type_)
                        child.setAttribute('name', name)
                        settings = IPortletAssignmentSettings(assignment)
                        if not settings.get('visible', True):
                            child.setAttribute('visible', 'False')

                        assignment = assignment.__of__(mapping)
                        # use existing adapter for exporting a portlet assignment  # noqa
                        handler = IPortletAssignmentExportImportHandler(assignment)  # noqa
                        handler.export_assignment(schema, self.doc, child)

                        assignments.append(child)

        return assignments

    def exportBlacklists(self, obj):
        assignments = []
        for manager_name, manager in self.portlet_managers:
            assignable = queryMultiAdapter(
                (obj, manager),
                ILocalPortletAssignmentManager)
            if assignable is None:
                continue
            for category in (
                USER_CATEGORY,
                GROUP_CATEGORY,
                CONTENT_TYPE_CATEGORY,
                CONTEXT_CATEGORY
            ):
                child = self.doc.createElement('blacklist')
                child.setAttribute('manager', manager_name)
                child.setAttribute('category', category)

                status = assignable.getBlacklistStatus(category)
                if status is True:
                    child.setAttribute('status', u'block')
                elif status is False:
                    child.setAttribute('status', u'show')
                else:
                    child.setAttribute('status', u'acquire')

                assignments.append(child)

        return assignments

    def get_georeference(self):
        if IGeoreferenceable.providedBy(self.context):
            try:
                IWriteGeoreferenced(self.context)
                coord = Coordinates(self.context).coordinates
                self['coordinates'] = coord
            except:
                pass

    def get_comments(self):
        if self.context.portal_type == 'Discussion Item':
            self['author_email'] = getattr(self.context, 'author_email', None)
            self['author_name'] = getattr(self.context, 'author_name', None)
            self['author_username'] = getattr(self.context, 'author_username', None)

    def get_newsletter(self):
        pt = self.context.portal_type
        if pt == 'NewsletterTheme':
            self['testEmail'] = getattr(self.context, 'testEmail', None)
            self['authorEmail'] = getattr(self.context, 'authorEmail', None)
            self['replyto'] = getattr(self.context, 'replyto', None)
            self['activationMailSubject'] = getattr(self.context, 'activationMailSubject', None)
            self['activationMailTemplate'] = getattr(self.context, 'activationMailTemplate', None)
            self['newsletterHeader'] = getattr(self.context, 'newsletterHeader', None)
            self['newsletterFooter'] = getattr(self.context, 'newsletterFooter', None)
            self['newsletterStyle'] = getattr(self.context, 'newsletterStyle', None)
            self['notify'] = getattr(self.context, 'notify', False)
            self['renderTemplate'] = getattr(self.context, 'renderTemplate', None)
            self['extraRecipients'] = getattr(self.context, 'extraRecipients', None)
            self['subscriber_folder_id'] = getattr(self.context, 'subscriber_folder_id', None)
            self['alternative_portal_url'] = getattr(self.context, 'alternative_portal_url', None)
        if pt == 'Newsletter':
            self['setFormat'] = getattr(self.context, 'setFormat', None)
            self['dateEmitted'] = getattr(self.context, 'dateEmitted', None)
