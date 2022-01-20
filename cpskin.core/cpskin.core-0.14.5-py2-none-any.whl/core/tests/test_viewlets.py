# -*- coding: utf-8 -*-
from collective.geo.behaviour.interfaces import ICoordinates
from cpskin.core.testing import CPSKIN_CORE_INTEGRATION_TESTING
from cpskin.core.utils import add_behavior
from cpskin.core.utils import add_keyword
from cpskin.core.utils import add_leadimage_from_file
from imio.gdpr.interfaces import IGDPRSettings
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.Five.browser import BrowserView
from z3c.relationfield.relation import RelationValue
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
from zope.viewlet.interfaces import IViewletManager

import json
import os
import unittest


class TestViewlets(unittest.TestCase):

    layer = CPSKIN_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder = api.content.create(self.portal, 'Folder', 'folder')

    def test_navigation_toggle_viewlet(self):
        folder = api.content.create(
            container=self.portal, type='Folder', id='folder1')
        view = getMultiAdapter(
            (folder, self.request), name='navigation_toggle_activation')
        navtogglesettings = view.settings
        self.assertEqual(navtogglesettings.selectors, ())
        self.assertFalse(view.is_enabled)
        self.assertTrue(view.can_enable_navigation_toggle)
        self.assertFalse(view.can_disable_navigation_toggle)

        view.enable_navigation_toggle()
        self.assertTrue(view.is_enabled)
        self.assertFalse(view.can_enable_navigation_toggle)
        self.assertTrue(view.can_disable_navigation_toggle)
        self.assertEqual(navtogglesettings.selectors, (u'/folder1', ))

        view.disable_navigation_toggle()
        self.assertFalse(view.is_enabled)
        self.assertTrue(view.can_enable_navigation_toggle)
        self.assertFalse(view.can_disable_navigation_toggle)
        self.assertEqual(navtogglesettings.selectors, ())

    def test_set_media_viewlet(self):
        view = getMultiAdapter(
            (self.portal, self.request), name='media_activation')
        self.assertFalse('videos' in self.portal.keys())
        self.assertFalse(view.is_enabled)
        self.assertFalse(view.can_disable_media)

        view.enable_media()
        self.assertTrue(view.is_enabled)
        self.assertTrue(view.can_disable_media)
        self.assertTrue('videos' in self.portal.keys())

        view.disable_media()
        self.assertFalse(view.is_enabled)
        self.assertFalse(view.can_disable_media)
        self.assertTrue('videos' in self.portal.keys())

        view.enable_media()
        self.assertTrue(view.is_enabled)
        self.assertTrue(view.can_disable_media)
        self.assertTrue('videos' in self.portal.keys())

    def test_media_viewlet(self):
        keywords = ['album-a-la-une']
        view = getMultiAdapter(
            (self.portal, self.request), name='media_activation')
        # create video collection used to viewlet
        view.enable_media()
        album_collection = self.portal.albums.index
        query = [
            {
                'i': 'hiddenTags',
                'o': 'plone.app.querystring.operation.selection.is',
                'v': keywords
            },
        ]

        # Set hiddenTags and leadimage behaviors
        add_behavior('Folder', 'cpskin.core.behaviors.metadata.IHiddenTags')
        add_behavior(
            'Folder',
            'plone.app.contenttypes.behaviors.leadimage.ILeadImage')

        album_collection.query = query
        album = api.content.create(
            container=self.portal, type='Folder', id='testalbum')

        # getting viewlet
        view = BrowserView(self.portal, self.request)
        manager_name = 'plone.belowcontent'
        manager = queryMultiAdapter(
            (self.portal, self.request, view),
            IViewletManager,
            manager_name,
            default=None)
        self.assertIsNotNone(manager)
        manager.update()

        my_viewlet = [
            v for v in manager.viewlets if v.__name__ == 'cpskin.media']
        self.assertEqual(len(my_viewlet), 1)
        media_viewlet = my_viewlet[0]

        self.assertTrue(media_viewlet.available())
        self.assertEqual(
            media_viewlet.get_albums_collection().getPhysicalPath(),
            self.portal.albums.index.getPhysicalPath())
        self.assertEqual(len(media_viewlet.get_albums()), 0)

        # Set lead image to album folder
        add_leadimage_from_file(album, 'cpskinlogo.png')
        add_keyword(album, 'hiddenTags', keywords)
        self.assertEqual(len(media_viewlet.get_albums()), 1)

    def test_above_related_contacts_viewlet(self):
        add_behavior(
            'Event', 'cpskin.core.behaviors.metadata.IRelatedContacts')
        event = api.content.create(
            container=self.folder,
            type='Event',
            id='myevent'
        )

        # getting viewlet
        view = BrowserView(event, self.request)
        manager_name = 'plone.abovecontentbody'
        manager = queryMultiAdapter(
            (event, self.request, view),
            IViewletManager,
            manager_name,
            default=None)
        self.assertIsNotNone(manager)
        manager.update()

        my_viewlet = [
            v for v in manager.viewlets if v.__name__ == 'cpskin.above_related_contacts']  # noqa
        self.assertEqual(len(my_viewlet), 1)
        above_viewlet = my_viewlet[0]

        contacts = above_viewlet.get_contacts()
        self.assertEqual(contacts, [])
        self.assertFalse(above_viewlet.available())

        # add some contacts
        applyProfile(self.portal, 'collective.contact.core:default')
        directory = api.content.create(
            container=self.portal, type='directory', id='directory')
        person = api.content.create(
            container=directory, type='person', id='person')
        person.firstname = u'Foo'
        person.lastname = u'Bar'
        person.gender = u'F'
        person.street = u'Zoning Industriel'
        person.number = u'34'
        person.zip_code = u'5190'
        person.city = u'Mornimont'

        # set related contact
        intids = getUtility(IIntIds)
        to_id = intids.getId(person)
        rv = RelationValue(to_id)
        event.aboveContentContact = event.aboveContentContact + [rv]
        self.assertTrue(above_viewlet.available())
        contacts = above_viewlet.get_contacts()
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0], person)

        self.assertIn('Mornimont', above_viewlet.render())
        self.assertNotIn('Foo Bar', above_viewlet.render())

        event.aboveVisbileFields = ('street', 'number', 'zip_code', 'city')
        self.assertIn('5190', above_viewlet.render())
        self.assertIn('Mornimont', above_viewlet.render())

        event.aboveVisbileFields = ('firstname',)
        self.assertIn('Foo', above_viewlet.render())

        # test get_title method
        self.assertFalse(above_viewlet.get_title(person))
        event.aboveVisbileFields = ('title')
        self.assertEqual(
            above_viewlet.get_title(person),
            u'<span class="related-contact-title">Foo Bar</span>')

    def test_below_related_contacts_viewlet(self):
        add_behavior(
            'Event', 'cpskin.core.behaviors.metadata.IRelatedContacts')
        event = api.content.create(
            container=self.folder,
            type='Event',
            id='myevent'
        )

        # getting viewlet
        view = BrowserView(event, self.request)
        manager_name = 'plone.belowcontentbody'
        manager = queryMultiAdapter(
            (event, self.request, view),
            IViewletManager,
            manager_name,
            default=None)
        self.assertIsNotNone(manager)
        manager.update()

        my_viewlet = [
            v for v in manager.viewlets if v.__name__ == 'cpskin.below_related_contacts']  # noqa
        self.assertEqual(len(my_viewlet), 1)
        below_viewlet = my_viewlet[0]

        contacts = below_viewlet.get_contacts()
        self.assertEqual(contacts, [])
        self.assertFalse(below_viewlet.available())

        # add some contacts
        applyProfile(self.portal, 'collective.contact.core:default')
        directory = api.content.create(
            container=self.portal, type='directory', id='directory')
        person = api.content.create(
            container=directory, type='person', id='person')
        person.firstname = u'Foo'
        person.lastname = u'Bar'
        person.gender = u'F'
        person.street = u'Zoning Industriel'
        person.number = u'34'
        person.zip_code = u'5190'
        person.city = u'Mornimont'

        # set related contact
        intids = getUtility(IIntIds)
        to_id = intids.getId(person)
        rv = RelationValue(to_id)
        event.belowContentContact = event.belowContentContact + [rv]
        self.assertTrue(below_viewlet.available())
        contacts = below_viewlet.get_contacts()
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0], person)

        self.assertNotIn('Mornimont', below_viewlet.render())
        self.assertIn('Foo Bar', below_viewlet.render())

        event.belowVisbileFields = ('zip_code',)
        self.assertNotIn('5190', below_viewlet.render())
        self.assertNotIn('Foo', below_viewlet.render())

        # test get_title method
        self.assertFalse(below_viewlet.get_title(person))
        event.belowVisbileFields = ('title')
        self.assertEqual(
            below_viewlet.get_title(person),
            u'<a href="http://nohost/plone/directory/person" target="_blank"><h4>Foo Bar</h4></a>')  # noqa

    def test_use_parent_address(self):
        add_behavior(
            'Event', 'cpskin.core.behaviors.metadata.IRelatedContacts')
        event = api.content.create(
            container=self.folder,
            type='Event',
            id='myevent'
        )

        # getting viewlet
        view = BrowserView(event, self.request)
        manager_name = 'plone.belowcontentbody'
        manager = queryMultiAdapter(
            (event, self.request, view),
            IViewletManager,
            manager_name,
            default=None)
        self.assertIsNotNone(manager)
        manager.update()

        my_viewlet = [
            v for v in manager.viewlets if v.__name__ == 'cpskin.below_related_contacts']  # noqa
        self.assertEqual(len(my_viewlet), 1)
        below_viewlet = my_viewlet[0]

        contacts = below_viewlet.get_contacts()
        self.assertEqual(contacts, [])
        self.assertFalse(below_viewlet.available())

        # add some contacts
        applyProfile(self.portal, 'collective.contact.core:default')
        directory = api.content.create(
            container=self.portal, type='directory', id='directory')
        person = api.content.create(
            container=directory, type='person', id='person')
        person.firstname = u'Foo'
        person.lastname = u'Bar'
        person.gender = u'F'
        person.street = u'Zoning Industriel'
        person.number = u'34'
        person.zip_code = u'5190'
        person.city = u'Mornimont'
        person.use_parent_address = True

        # set related contact
        intids = getUtility(IIntIds)
        to_id = intids.getId(person)
        rv = RelationValue(to_id)
        event.belowContentContact = event.belowContentContact + [rv]
        self.assertTrue(below_viewlet.available())
        contacts = below_viewlet.get_contacts()
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0], person)

        self.assertNotIn('Mornimont', below_viewlet.render())
        self.assertIn('Foo Bar', below_viewlet.render())

        event.belowVisbileFields = ('zip_code',)
        self.assertNotIn('5190', below_viewlet.render())
        self.assertNotIn('Foo', below_viewlet.render())

    def test_use_parent_address_in_map(self):
        add_behavior(
            'Event', 'cpskin.core.behaviors.metadata.IRelatedContacts')
        event = api.content.create(
            container=self.folder,
            type='Event',
            id='myevent'
        )

        # getting viewlet
        view = BrowserView(event, self.request)
        manager_name = 'plone.belowcontentbody'
        manager = queryMultiAdapter(
            (event, self.request, view),
            IViewletManager,
            manager_name,
            default=None)
        self.assertIsNotNone(manager)
        manager.update()

        my_viewlet = [
            v for v in manager.viewlets if v.__name__ == 'cpskin.related_contacts_map']  # noqa
        self.assertEqual(len(my_viewlet), 1)
        map_viewlet = my_viewlet[0]

        contacts = map_viewlet.get_contacts()
        self.assertEqual(contacts, [])
        self.assertFalse(map_viewlet.available())

        # add some contacts
        applyProfile(self.portal, 'collective.contact.core:default')
        directory = api.content.create(
            container=self.portal, type='directory', id='directory')

        organization = api.content.create(
            container=directory, type='organization', id='organization')
        organization.title = u'IMIO'
        organization.street = u'Rue Léon Morel'
        organization.number = u'1'
        organization.zip_code = u'5032'
        organization.city = u'Isnes'
        organization.use_parent_address = False

        orga_child = api.content.create(
            container=organization, type='organization', id='organization')
        orga_child.title = 'DevOps'
        orga_child.use_parent_address = False

        # set related contact
        intids = getUtility(IIntIds)
        to_id = intids.getId(orga_child)
        rv = RelationValue(to_id)
        event.belowContentContact = [rv]
        add_behavior('organization', ICoordinates.__identifier__)
        notify(ObjectModifiedEvent(organization))

        self.assertTrue(map_viewlet.see_map_link(organization))
        self.assertFalse(map_viewlet.see_map_link(orga_child))
        data_geojson = map_viewlet.data_geojson()
        results = json.loads(data_geojson)
        self.assertEqual(len(results['features']), 0)

        orga_child.use_parent_address = True
        notify(ObjectModifiedEvent(orga_child))
        self.assertTrue(map_viewlet.see_map_link(orga_child))
        data_geojson = map_viewlet.data_geojson()
        results = json.loads(data_geojson)
        self.assertEqual(
            results['features'][0]['properties']['address'],
            u'Rue L\xe9on Morel, 1<br />5032 Isnes'
        )

    def test_related_contacts_map_viewlet(self):
        add_behavior(
            'Event', 'cpskin.core.behaviors.metadata.IRelatedContacts')

        event = api.content.create(
            container=self.folder,
            type='Event',
            id='myevent'
        )

        # getting viewlet
        view = BrowserView(event, self.request)
        manager_name = 'plone.belowcontentbody'
        manager = queryMultiAdapter(
            (event, self.request, view),
            IViewletManager,
            manager_name,
            default=None)
        self.assertIsNotNone(manager)
        manager.update()

        my_viewlet = [
            v for v in manager.viewlets if v.__name__ == 'cpskin.related_contacts_map']  # noqa
        self.assertEqual(len(my_viewlet), 1)
        map_viewlet = my_viewlet[0]

        contacts = map_viewlet.get_contacts()
        self.assertEqual(contacts, [])
        self.assertFalse(map_viewlet.available())

        # add some contacts
        applyProfile(self.portal, 'collective.contact.core:default')
        add_behavior('person', ICoordinates.__identifier__)
        from collective.contact.core.behaviors import IContactDetails
        add_behavior('person', IContactDetails.__identifier__)
        directory = api.content.create(
            container=self.portal, type='directory', id='directory')
        person = api.content.create(
            container=directory, type='person', id='person')
        person.firstname = u'Foo'
        person.lastname = u'Bar'
        person.gender = u'F'
        person.street = u'Rue de la Vieille Sambre'
        person.number = u'34'
        person.zip_code = u'5190'
        person.city = u'Mornimont'
        person.use_parent_address = False
        notify(ObjectModifiedEvent(person))
        person.street = u'Zoning Industriel'
        person.number = u'34'
        person.zip_code = u'5190'
        person.city = u'Mornimont'
        # set related contact
        intids = getUtility(IIntIds)
        to_id = intids.getId(person)
        rv = RelationValue(to_id)
        event.belowContentContact = event.belowContentContact + [rv]
        self.assertTrue(map_viewlet.available())
        contacts = map_viewlet.get_contacts()
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0], person)

        # Do not see duplicate
        event.aboveContentContact = event.aboveContentContact + [rv]
        contacts = map_viewlet.get_contacts()
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0], person)

        person2 = api.content.create(directory, 'person', 'person2')
        person2.firstname = u'James'
        person2.lastname = u'Bond'
        person2.gender = u'M'
        person2.street = u"Boulevard d'avroy"
        person2.number = u'007'
        person2.zip_code = u'4000'
        person2.city = u'Liège'
        notify(ObjectModifiedEvent(person2))
        person2.street = u"Boulevard d'avroy"
        person2.number = u'007'
        person2.zip_code = u'4000'
        person2.city = u'Liège'
        person2.use_parent_address = False
        to_id2 = intids.getId(person2)
        rv2 = RelationValue(to_id2)
        event.aboveContentContact = event.aboveContentContact + [rv2]
        contacts = map_viewlet.get_contacts()
        self.assertEqual(len(contacts), 2)
        event.see_map = False
        self.assertFalse(map_viewlet.available())
        event.see_map = True

        geojson = map_viewlet.data_geojson()
        results = json.loads(geojson)
        self.assertEqual(results['type'], u'FeatureCollection')
        self.assertEqual(len(results['features']), 2)
        self.assertEqual(u'', results['features'][0]['properties']['image'])

        # add a logo
        core_path = '/'.join(os.path.dirname(__file__).split('/')[:-1])
        data_path = os.path.join(core_path, 'data')
        file_path = os.path.join(data_path, 'cpskinlogo.png')
        from plone.namedfile.file import NamedBlobImage
        namedblobimage = NamedBlobImage(
            data=open(file_path, 'r').read(),
            filename=unicode('cpskinlogo.png')
        )
        person.logo = namedblobimage
        geojson = map_viewlet.data_geojson()
        results = json.loads(geojson)
        self.assertEqual(
            u'http://nohost/plone/directory/person/@@images/logo/thumb',
            results['features'][0]['properties']['image'])

    def test_footer_viewlet(self):
        # getting viewlet
        view = BrowserView(self.portal, self.request)
        manager_name = 'plone.portalfooter'
        manager = queryMultiAdapter(
            (self.portal, self.request, view),
            IViewletManager,
            manager_name,
            default=None)
        self.assertIsNotNone(manager)
        manager.update()

        my_viewlet = [
            v for v in manager.viewlets if v.__name__ == 'cpskin.footer']  # noqa
        self.assertEqual(len(my_viewlet), 1)
        viewlet = my_viewlet[0]
        self.assertNotIn('Legal notice', viewlet.render())
        api.portal.set_registry_record(
            'is_text_ready',
            True,
            interface=IGDPRSettings
        )
        self.assertIn('Legal notice', viewlet.render())
