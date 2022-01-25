# -*- coding: utf-8 -*-
from collective.geo.behaviour.interfaces import ICoordinates
from collective.taxonomy.interfaces import ITaxonomy
from cpskin.core.behaviors.indexview import ICpskinIndexViewSettings
from cpskin.core.browser.folderview import configure_folderviews
from cpskin.core.interfaces import ICPSkinCoreLayer
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from cpskin.core.utils import add_behavior
from cpskin.core.utils import add_leadimage_from_file
from cpskin.menu.interfaces import IDirectAccess
from datetime import datetime
from DateTime import DateTime
from datetime import timedelta
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.schemaeditor.utils import FieldAddedEvent
from plone.schemaeditor.utils import IEditableSchema
from plone.uuid.interfaces import IUUID
from Products.statusmessages.interfaces import IStatusMessage
from zope import schema
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.lifecycleevent import ObjectAddedEvent

import pytz
import unittest


class TestViews(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        fti = api.portal.get_tool('portal_types')['Plone Site']
        fti.allowed_content_types = fti.allowed_content_types + ('directory',)
        self.folder = api.content.create(self.portal, 'Folder', 'folder')

    def test_opendata_view(self):
        directlyProvides(self.request, ICPSkinCoreLayer)  # noqa
        configure_folderviews(self.portal)
        view = self.portal.restrictedTraverse('opendata')
        links = view.get_links()
        self.assertEqual(len(links), 3)

    def test_folderview_setting_named_link(self):
        add_behavior(
            'Collection',
            'cpskin.core.behaviors.indexview.ICpskinIndexViewSettings')
        configure_folderviews(self.portal)
        news = api.content.create(
            container=self.folder,
            type='News Item',
            id='testnewsitem')
        api.content.transition(obj=news, transition='publish')
        api.content.transition(obj=self.portal.actualites.actualites,
                               transition='publish')
        api.content.transition(obj=self.portal.actualites,
                               transition='publish')
        collection = self.portal.actualites.actualites
        link_text = getattr(collection, 'link_text')
        self.assertEqual(link_text, '')
        view = getMultiAdapter((self.portal, self.request), name='folderview')
        voir_lensemble_des = view.see_all(collection)
        self.assertEqual(voir_lensemble_des,
                         "Voir l'ensemble des actualit\xc3\xa9s")

        collection.link_text = u'Voir toutes les actualit\xc3\xa9s'
        voir_lensemble_des = view.see_all(collection)
        self.assertEqual(voir_lensemble_des,
                         'Voir toutes les actualit\xc3\x83\xc2\xa9s')
        self.assertTrue('Voir toutes les actualit' in view.index())

    def test_folderview_setting_image_scale(self):
        add_behavior(
            'Collection',
            'cpskin.core.behaviors.indexview.ICpskinIndexViewSettings')
        configure_folderviews(self.portal)
        news = api.content.create(
            container=self.folder,
            type='News Item',
            id='testnewsitem')
        api.content.transition(obj=news, transition='publish')
        collection = self.portal.actualites.actualites
        view = getMultiAdapter(
            (self.portal, self.request), name='folderview')
        self.assertEqual(collection.collection_image_scale, 'collection')
        self.assertEqual(collection.slider_image_scale, 'slider')
        self.assertEqual(collection.carousel_image_scale, 'carousel')
        scale = view.collection_image_scale(collection, news)
        self.assertFalse(scale)
        add_leadimage_from_file(news, 'visuel.png')
        scale = view.collection_image_scale(collection, news)
        self.assertTrue('height="116"' in scale)

        collection.collection_image_scale = 'thumb'
        scale = view.collection_image_scale(collection, news)
        self.assertTrue('height="250"' in scale)

    def test_folderview_add_remove_content(self):
        configure_folderviews(self.portal)
        request = self.portal.actualites.REQUEST
        api.content.create(
            container=self.folder,
            type='News Item',
            id='testnewsitem')
        view = getMultiAdapter(
            (self.portal.actualites, request), name='folderview')
        self.assertTrue(view.canRemoveContent())
        self.assertFalse(view.canAddContent())
        view.removeContent()
        self.assertFalse(view.canRemoveContent())
        self.assertTrue(view.canAddContent())
        view.addContent()
        self.assertTrue(view.canRemoveContent())
        self.assertFalse(view.canAddContent())

    def test_folderview_render(self):
        configure_folderviews(self.portal)
        request = self.portal.REQUEST
        testnewsitem = api.content.create(
            container=self.folder,
            type='News Item',
            id='testnewsitem')
        api.content.transition(obj=testnewsitem, transition='publish')
        api.content.transition(obj=self.portal.actualites,
                               transition='publish')
        view = getMultiAdapter((self.portal, request), name='folderview')
        self.assertIn(
            u'<a href="http://nohost/plone/actualites/actualites" title="">Actualit\xe9s',
            view.index())

    def test_folderview_event_category(self):
        applyProfile(self.portal, 'collective.taxonomy:default')
        add_behavior('Collection', ICpskinIndexViewSettings.__identifier__)

        utility = queryUtility(ITaxonomy, name='collective.taxonomy.test')
        collection = api.content.create(container=self.folder,
                                        type='Collection',
                                        id='collection')
        collection.taxonomy_category = 'taxonomy_test'
        collection.reindexObject()

        taxonomy_test = schema.Set(
            title=u'taxonomy_test',
            description=u'taxonomy description schema',
            required=False,
            value_type=schema.Choice(
                vocabulary=u'collective.taxonomy.test'),
        )
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types.get('Event')
        event_schema = fti.lookupSchema()
        schemaeditor = IEditableSchema(event_schema)
        schemaeditor.addField(taxonomy_test, name='taxonomy_test')
        notify(ObjectAddedEvent(taxonomy_test, event_schema))
        notify(FieldAddedEvent(fti, taxonomy_test))
        event = api.content.create(
            container=self.folder,
            type='Event',
            id='testevent')
        simple_tax = [val for val in utility.data['en'].values()]
        event.taxonomy_test = set(simple_tax[0])

        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='folderview')

        see_categories = view.see_categories(collection)
        self.assertTrue(see_categories)
        collection.taxonomy_category = ''
        see_categories = view.see_categories(collection)
        self.assertFalse(see_categories)
        collection.taxonomy_category = 'taxonomy_test'
        categories = view.get_categories(collection, event)
        self.assertEqual(categories, 'Information Science')

        event.taxonomy_test = set(simple_tax[0:2])
        categories = view.get_categories(collection, event)
        self.assertEqual(
            categories,
            'Book Collecting, Information Science')

        event.taxonomy_test = set()
        categories = view.get_categories(collection, event)
        self.assertEqual(categories, '')

    def test_folderview_event_item_count_homepage(self):
        add_behavior('Collection', ICpskinIndexViewSettings.__identifier__)

        collection = api.content.create(container=self.folder,
                                        type='Collection',
                                        id='collection')

        collection.setQuery(
            [{u'i': u'portal_type',
              u'o': u'plone.app.querystring.operation.selection.is',
              u'v': [u'News Item']}, ]
        )
        collection.item_count_homepage = 1
        api.content.create(
            container=self.folder,
            type='News Item',
            id='testnews')
        api.content.create(
            container=self.folder,
            type='News Item',
            id='testnews2')

        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='folderview')

        result = view.getResults(collection)
        self.assertEqual(len(result['standard-results']), 1)

        collection.item_count_homepage = 2
        result = view.getResults(collection)
        self.assertEqual(len(result['standard-results']), 2)

    def test_folderview_event_localizedtime(self):
        utc = pytz.utc
        start = datetime(2001, 1, 1, 10, 0, tzinfo=utc)
        end = datetime(2001, 1, 1, 11, 0, tzinfo=utc)
        event = api.content.create(
            container=self.folder,
            type='Event',
            id='testevent',
            start=start,
            end=end,
            timezone='UTC')

        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='folderview')

        oneday = view.is_one_day(event)
        self.assertTrue(oneday)

        event.end = datetime(2001, 1, 2, 11, 0, tzinfo=utc)
        oneday = view.is_one_day(event)
        self.assertFalse(oneday)

        withhours = view.is_with_hours(event)
        self.assertTrue(withhours)

    def test_event_geo_contents_view(self):
        add_behavior('Event', ICoordinates.__identifier__)
        event = api.content.create(container=self.folder,
                                   type='Event', title='document')
        event.location = 'Rue Léon Morel, 1 5032 Isnes'
        form = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='set-geo-contents-form')
        form.request.form = {'form.widgets.content_types': [u'Event']}
        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
        coord = ICoordinates(event).coordinates
        self.assertFalse(coord.startswith('POINT '))
        form.handleApply(form, 'Ok')
        coord = ICoordinates(event).coordinates
        self.assertTrue(coord.startswith('POINT '))

    def test_orga_geo_contents_view(self):
        # add some contacts
        applyProfile(self.portal, 'collective.contact.core:default')
        directory = api.content.create(
            container=self.portal, type='directory', id='directory')
        person = api.content.create(
            container=directory, type='person', id='person')
        person.street = u'Rue de la Vieille Sambre'
        person.number = u'34'
        person.zip_code = u'5190'
        person.city = u'Mornimont'

        add_behavior('person', ICoordinates.__identifier__)

        form = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='set-geo-contents-form')
        form.request.form = {'form.widgets.content_types': [u'person']}
        form.update()

        coord = ICoordinates(person).coordinates
        self.assertFalse(coord.startswith('POINT '))
        form.handleApply(form, 'Ok')
        coord = ICoordinates(person).coordinates
        self.assertTrue(coord.startswith('POINT '))

    def test_bad_orga_geo_contents_view(self):
        # add some contacts
        applyProfile(self.portal, 'collective.contact.core:default')
        add_behavior('person', ICoordinates.__identifier__)
        directory = api.content.create(
            container=self.portal, type='directory', id='directory')
        person = api.content.create(
            container=directory, type='person', id='person')

        form = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='set-geo-contents-form')
        form.request.form = {'form.widgets.content_types': [u'person']}
        form.update()
        form.handleApply(form, 'Ok')
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()  # noqa
        self.assertEqual(
            messages[0].message,
            u'No address for http://nohost/plone/directory/person')  # noqa
        self.assertEqual(messages[1].message, u'0 person are updated')
        person.street = u'Rue de l\'hôtel de ville'
        person.number = u'34'
        person.zip_code = u'5190'
        person.city = u'Mornimont'

        form = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='set-geo-contents-form')
        form.request.form = {'form.widgets.content_types': [u'person']}
        form.update()

        coord = ICoordinates(person).coordinates
        self.assertFalse(coord.startswith('POINT '))
        form.handleApply(form, 'Ok')
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()  # noqa
        self.assertEqual(messages[0].message, u'1 person are updated')
        coord = ICoordinates(person).coordinates
        self.assertTrue(coord.startswith('POINT '))

    def test_date_event_generation_helper_view(self):
        applyProfile(self.portal, 'collective.documentgenerator:default')
        utc = pytz.utc
        start = datetime(2001, 1, 1, 10, 0, tzinfo=utc)
        end = datetime(2001, 1, 1, 11, 0, tzinfo=utc)
        event = api.content.create(container=self.folder,
                                   type='Event', title='my_event',
                                   start=start, end=end, timezone='UTC')
        view = getMultiAdapter(
            (event, self.portal.REQUEST),
            name='document_generation_helper_view')
        view.real_context = event
        self.assertEqual(
            view.get_formatted_date(), u'1 January 2001 de 10:00 \xe0 11:00')

        event.end = datetime(2001, 1, 3, 11, 0, tzinfo=utc)
        view = getMultiAdapter(
            (event, self.portal.REQUEST),
            name='document_generation_helper_view')
        self.assertEqual(
            view.get_formatted_date(), u'1 au 3 January 2001 de 10:00 \xe0 11:00')

        event.end = datetime(2001, 2, 1, 11, 0, tzinfo=utc)
        view = getMultiAdapter(
            (event, self.portal.REQUEST),
            name='document_generation_helper_view')
        self.assertEqual(
            view.get_formatted_date(),
            u'1 January 2001 au 1 February 2001 de 10:00 \xe0 11:00')

        event.end = datetime(2001, 1, 1, 11, 0, tzinfo=utc)
        event.open_end = True
        view = getMultiAdapter(
            (event, self.portal.REQUEST),
            name='document_generation_helper_view')
        self.assertEqual(
            view.get_formatted_date(), u'1 January 2001 \xe0 10:00')

        event.contact = 'Imio'
        event.phone = '081/586.100'
        info = view.get_info()
        self.assertEqual(info, 'Info : my_event - 081 58 61 00')

    def test_folderview_hide_title(self):
        # directlyProvides(self.portal.REQUEST, ICPSkinCoreLayer)  # noqa
        add_behavior('Collection', ICpskinIndexViewSettings.__identifier__)
        configure_folderviews(self.portal)
        collection = self.portal.actualites.actualites
        collection.title = u'My test collection'
        collection.setQuery(
            [{u'i': u'portal_type',
              u'o': u'plone.app.querystring.operation.selection.is',
              u'v': [u'News Item']}, ]
        )
        collection.reindexObject()
        news = api.content.create(
            container=self.folder,
            type='News Item',
            id='testnews')
        news.title = u'My test news'

        api.content.transition(obj=collection, transition='publish')
        api.content.transition(obj=self.portal.actualites,
                               transition='publish')
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='folderview')
        self.assertFalse(view.hide_title(collection))
        self.assertIn('<h2>My test collection</h2>', view())

        collection.hide_title = True
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='folderview')
        self.assertTrue(view.hide_title(collection))
        self.assertNotIn('<h2>My test collection</h2>', view())

    def test_folderview_hide_see_all_link(self):
        add_behavior('Collection', ICpskinIndexViewSettings.__identifier__)
        configure_folderviews(self.portal)
        collection = self.portal.actualites.actualites
        collection.setQuery(
            [{u'i': u'portal_type',
              u'o': u'plone.app.querystring.operation.selection.is',
              u'v': [u'News Item']}, ]
        )
        api.content.create(
            container=self.folder,
            type='News Item',
            id='testnews')
        api.content.transition(obj=collection, transition='publish')
        api.content.transition(obj=self.portal.actualites,
                               transition='publish')
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='folderview')
        self.assertFalse(view.hide_see_all_link(collection))
        self.assertIn(u"Voir l\'ensemble des actualit\xe9s", view())

        collection.hide_see_all_link = True
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='folderview')
        self.assertTrue(view.hide_see_all_link(collection))
        self.assertNotIn(u"Voir l\'ensemble des actualit\xe9s", view())

    def test_folderview_hide_date(self):
        add_behavior('Collection', ICpskinIndexViewSettings.__identifier__)
        configure_folderviews(self.portal)
        collection = self.portal.actualites.actualites
        collection.setQuery(
            [{u'i': u'portal_type',
              u'o': u'plone.app.querystring.operation.selection.is',
              u'v': [u'News Item']}, ]
        )
        news = api.content.create(
            container=self.folder,
            type='News Item',
            id='testnews')
        api.content.transition(obj=news, transition='publish')
        news.setEffectiveDate(DateTime('2016/07/26'))
        news.reindexObject()
        api.content.transition(obj=collection, transition='publish')
        api.content.transition(obj=self.portal.actualites,
                               transition='publish')
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='folderview')
        news_brain = view.getResults(collection)['standard-results'][0]
        self.assertFalse(view.hide_date(news_brain, collection))
        self.assertIn(u'Jul 26, 2016', view())

        collection.hide_date = True
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='folderview')
        self.assertTrue(view.hide_date(news_brain, collection))
        self.assertNotIn(u'Jul 26, 2016', view())

    def test_teleservice_template(self):
        view = api.content.get_view(
            name='teleservice-template',
            context=self.portal,
            request=self.request)
        self.assertIn('id="teleservice-nav"', view())

    def test_folderview_old_new_template(self):
        add_behavior(
            'Collection',
            'cpskin.core.behaviors.indexview.ICpskinIndexViewSettings')
        configure_folderviews(self.portal)
        news = api.content.create(
            container=self.folder,
            type='News Item',
            id='testnewsitem')
        api.content.transition(obj=news, transition='publish')
        collection = self.portal.actualites.actualites
        view = getMultiAdapter(
            (self.portal, self.request), name='folderview')
        self.assertEqual(collection.collection_image_scale, 'collection')
        add_leadimage_from_file(news, 'visuel.png')
        scale = view.collection_image_scale(collection, news)
        self.assertTrue('height="116"' in scale)

        collection.use_new_template = True
        scale = view.collection_image_scale(collection, news)
        self.assertEqual(scale.height, 116)
        self.assertEqual(scale.width, 77)

    def test_cpskin_navigation_view(self):
        applyProfile(self.portal, 'cpskin.workflow:default')
        self.portal.portal_workflow.setDefaultChain('cpskin_workflow')
        subfolder = api.content.create(self.folder, 'Folder', 'subfolder')
        subsubfolder = api.content.create(subfolder, 'Folder', 'subfolder')
        alsoProvides(subsubfolder, IDirectAccess)
        subsubfolder.reindexObject()
        view = api.content.get_view(
            name='cpskin_navigation_view',
            context=self.folder,
            request=self.folder.REQUEST)
        self.assertEqual(0, len(view.menus()))
        api.content.transition(obj=subfolder, transition='publish_and_show')
        self.assertEqual(1, len(view.menus()))
        self.assertEqual(0, len(view.accesses()))
        view = api.content.get_view(
            name='cpskin_navigation_view',
            context=subfolder,
            request=subfolder.REQUEST)
        self.assertEqual(1, len(view.accesses()))

    def test_cpskinhealthy_view(self):
        applyProfile(self.portal, 'cpskin.workflow:default')
        view = self.portal.restrictedTraverse('cpskinhealthy')
        contacts = view.contacts()
        self.assertEqual(contacts['is_installed'], False)
        view.install_contact_core()
        contacts = view.contacts()
        self.assertEqual(contacts['is_installed'], True)
        self.assertEqual(contacts['is_cpskin_workflow'], False)
        view.set_contact_worflow()
        contacts = view.contacts()
        self.assertEqual(contacts['is_cpskin_workflow'], True)

        self.assertEqual(view.get_site_language(), 'en')
        self.assertFalse(view.is_site_language_fr())
        view.set_site_language()
        self.assertEqual(view.get_site_language(), 'fr')
        self.assertTrue(view.is_site_language_fr())

    def test_cpskin_navigation_with_leadimage_view(self):
        applyProfile(self.portal, 'cpskin.workflow:default')
        add_behavior(
            'Folder',
            'plone.app.contenttypes.behaviors.leadimage.ILeadImage')
        self.portal.portal_workflow.setDefaultChain('cpskin_workflow')
        subfolder = api.content.create(self.folder, 'Folder', 'subfolder')
        view = api.content.get_view(
            name='cpskin_navigation_view_with_leadimage',
            context=self.folder,
            request=self.folder.REQUEST)
        self.assertEqual(0, len(view.menus()))
        api.content.transition(obj=subfolder, transition='publish_and_show')
        self.assertEqual(1, len(view.menus()))
        brain = api.content.find(UID=IUUID(subfolder))[0]
        self.assertFalse(view.image(brain))
        add_leadimage_from_file(subfolder, 'visuel.png')
        self.assertTrue(view.image(brain).startswith(
            u'http://nohost/plone/folder/subfolder/@@images'
        ))

    def test_cpskin_search_view(self):
        api.content.create(
            container=self.portal,
            type='Document',
            id='document',
            title='My testing document'
        )
        request = self.portal.REQUEST
        request.form = {'SearchableText': 'testi'}
        view = api.content.get_view(
            name='search',
            context=self.portal,
            request=request)
        query = view.filter_query({})
        self.assertEqual(query['SearchableText'], 'testi*')
        self.assertEqual(len(view.results()), 1)

    def test_replace_rich_text_view(self):
        doc = api.content.create(self.portal, 'Document', 'doc')
        text = '<a href="http://nohost/plone/at_download/file">link</a>'
        doc.text = RichTextValue(text)
        form = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='replace-richtext-form')
        form.request.form = {
            'form.widgets.old_text': '/at_download/file',
            'form.widgets.new_text': ''
        }
        form.update()
        self.assertTrue('at_download/file' in doc.text.raw)
        form.handleApply(form, 'Ok')
        self.assertFalse('at_download/file' in doc.text.raw)
