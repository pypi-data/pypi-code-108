# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.smartweb.common.utils import geocode_object
from imio.events.core.contents.event.content import IEvent
from imio.events.core.interfaces import IImioEventsCoreLayer
from imio.events.core.testing import IMIO_EVENTS_CORE_INTEGRATION_TESTING
from imio.events.core.tests.utils import get_leadimage_filename
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.file import NamedBlobFile
from unittest import mock
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationList
from zope.component import createObject
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified
from zope.schema.interfaces import IVocabularyFactory

import geopy
import unittest


class TestEvent(unittest.TestCase):

    layer = IMIO_EVENTS_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.authorized_types_in_event = [
            "File",
            "Image",
        ]
        self.unauthorized_types_in_event = [
            "imio.events.Agenda",
            "imio.events.Folder",
            "imio.events.Event",
            "Document",
        ]
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.parent = self.portal
        self.entity = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            id="imio.events.Entity",
        )
        self.agenda = api.content.create(
            container=self.entity,
            type="imio.events.Agenda",
            id="imio.events.Agenda",
        )
        self.folder = api.content.create(
            container=self.agenda,
            type="imio.events.Folder",
            id="imio.events.Folder",
        )

    def test_ct_event_schema(self):
        fti = queryUtility(IDexterityFTI, name="imio.events.Event")
        schema = fti.lookupSchema()
        self.assertEqual(IEvent, schema)

    def test_ct_event_fti(self):
        fti = queryUtility(IDexterityFTI, name="imio.events.Event")
        self.assertTrue(fti)

    def test_ct_event_factory(self):
        fti = queryUtility(IDexterityFTI, name="imio.events.Event")
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(
            IEvent.providedBy(obj),
            u"IEvent not provided by {0}!".format(
                obj,
            ),
        )

    def test_ct_event_adding(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        obj = api.content.create(
            container=self.folder,
            type="imio.events.Event",
            id="imio.events.Event",
        )

        self.assertTrue(
            IEvent.providedBy(obj),
            u"IEvent not provided by {0}!".format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn("imio.events.Event", parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn("imio.events.Event", parent.objectIds())

    def test_ct_event_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="imio.events.Event")
        self.assertFalse(
            fti.global_allow, u"{0} is not globally addable!".format(fti.id)
        )

    def test_ct_event_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="imio.events.Event")
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.folder,
            "imio.events.Event_id",
            title="imio.events.Event container",
        )
        folder = self.folder[parent_id]
        for t in self.unauthorized_types_in_event:
            with self.assertRaises(InvalidParameterError):
                api.content.create(
                    container=folder,
                    type=t,
                    title="My {}".format(t),
                )
        for t in self.authorized_types_in_event:
            api.content.create(
                container=folder,
                type=t,
                title="My {}".format(t),
            )
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=folder,
                type="imio.events.Entity",
                title="My Entity",
            )

    def test_event_local_category(self):
        event = api.content.create(
            container=self.folder,
            type="imio.events.Event",
            id="my-event",
        )
        factory = getUtility(
            IVocabularyFactory, "imio.events.vocabulary.EventsLocalCategories"
        )
        vocabulary = factory(event)
        self.assertEqual(len(vocabulary), 0)

        self.entity.local_categories = "First\nSecond\nThird"
        vocabulary = factory(event)
        self.assertEqual(len(vocabulary), 3)

    def test_view(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="My event item",
        )
        view = queryMultiAdapter((event, self.request), name="view")
        self.assertIn("My event item", view())

    def test_embed_video(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="My event item",
        )
        event.video_url = "https://www.youtube.com/watch?v=_dOAthafoGQ"
        view = queryMultiAdapter((event, self.request), name="view")
        embedded_video = view.get_embed_video()
        self.assertIn("iframe", embedded_video)
        self.assertIn(
            "https://www.youtube.com/embed/_dOAthafoGQ?feature=oembed", embedded_video
        )

    def test_has_leadimage(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="My event item",
        )
        view = queryMultiAdapter((event, self.request), name="view")
        self.assertEqual(view.has_leadimage(), False)
        event.image = NamedBlobFile("ploneLeadImage", filename=get_leadimage_filename())
        self.assertEqual(view.has_leadimage(), True)

    def test_subscriber_to_select_current_agenda(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="My event item",
        )
        self.assertEqual(event.selected_agendas, [self.agenda.UID()])

    def test_indexes(self):
        event1 = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="Event1",
        )
        agenda2 = api.content.create(
            container=self.entity,
            type="imio.events.Agenda",
            title="Agenda2",
        )
        event2 = api.content.create(
            container=agenda2,
            type="imio.events.Event",
            title="Event2",
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=event1.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("container_uid"), self.agenda.UID())

        # On va requêter sur self.agenda et trouver les 2 événements car event2 vient de s'ajouter dedans aussi.
        event2.selected_agendas = [self.agenda.UID()]
        event2.reindexObject()
        brains = api.content.find(selected_agendas=self.agenda.UID())
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [event1.UID(), event2.UID()])

        # On va requêter sur agenda2 et trouver uniquement event2 car event2 est dans les 2 agendas mais event1 n'est que dans self.agenda
        event2.selected_agendas = [agenda2.UID(), self.agenda.UID()]
        event2.reindexObject()
        brains = api.content.find(selected_agendas=agenda2.UID())
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [event2.UID()])

        # Via une recherche catalog sur les agenda, on va trouver les 2 événements
        brains = api.content.find(selected_agendas=[agenda2.UID(), self.agenda.UID()])
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [event1.UID(), event2.UID()])

        # On va requêter sur les 2 agendas et trouver les 2 événements car 1 dans chaque
        event2.selected_agendas = [agenda2.UID()]
        event2.reindexObject()
        brains = api.content.find(selected_agendas=[agenda2.UID(), self.agenda.UID()])
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [event1.UID(), event2.UID()])

        api.content.move(event1, agenda2)
        brain = api.content.find(UID=event1.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("container_uid"), agenda2.UID())

    def test_searchable_text(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="Title",
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=event.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("SearchableText"), ["title"])

        event.description = "Description"
        event.topics = ["agriculture"]
        event.category = "stroll_discovery"
        event.text = RichTextValue("<p>Text</p>", "text/html", "text/html")
        event.reindexObject()

        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=event.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("SearchableText"),
            [
                "title",
                "description",
                "text",
                "agriculture",
                "balade",
                "et",
                "decouverte",
            ],
        )

    def test_category_title_index(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="Title",
        )
        event.category = "stroll_discovery"
        event.reindexObject()
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=event.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("category_title"), "Balade et découverte")

    def test_referrer_agendas(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        intids = getUtility(IIntIds)
        entity2 = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            id="entity2",
        )
        agenda2 = api.content.create(
            container=entity2,
            type="imio.events.Agenda",
            id="agenda2",
        )
        event2 = api.content.create(
            container=agenda2,
            type="imio.events.Event",
            id="event2",
        )
        setattr(
            self.agenda, "populating_agendas", [RelationValue(intids.getId(agenda2))]
        )
        modified(self.agenda, Attributes(IRelationList, "populating_agendas"))
        self.assertIn(self.agenda.UID(), event2.selected_agendas)

        # if we create an event in an agenda that is referred in another agenda
        # then, referrer agenda UID is in event.selected_agendas list.
        event2b = api.content.create(
            container=agenda2,
            type="imio.events.Event",
            id="event2b",
        )
        self.assertIn(self.agenda.UID(), event2b.selected_agendas)

    def test_automaticaly_readd_container_agenda_uid(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            id="event",
        )
        self.assertIn(self.agenda.UID(), event.selected_agendas)
        event.selected_agendas = []
        event.reindexObject()
        modified(event)
        self.assertIn(self.agenda.UID(), event.selected_agendas)

    def test_geolocation(self):
        attr = {"geocode.return_value": mock.Mock(latitude=1, longitude=2)}
        geopy.geocoders.Nominatim = mock.Mock(return_value=mock.Mock(**attr))

        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="event",
        )

        self.assertFalse(event.is_geolocated)
        event.geolocation = Geolocation(0, 0)
        event.street = "My beautiful street"
        geocode_object(event)
        self.assertTrue(event.is_geolocated)
        self.assertEqual(event.geolocation.latitude, 1)
        self.assertEqual(event.geolocation.longitude, 2)

    def test_geolocation_in_view(self):
        event = api.content.create(
            container=self.folder,
            type="imio.events.Event",
            id="my-event",
        )
        IGeolocatable(event).geolocation = Geolocation(latitude="4.5", longitude="45")
        view = queryMultiAdapter((event, self.request), name="view")
        self.assertIn("map", view())
        self.assertIn('class="pat-leaflet map"', view())

    def test_name_chooser(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="event",
        )
        self.assertEqual(event.id, event.UID())

        entity = api.content.create(
            container=self.portal,
            type="imio.events.Entity",
            title="entity",
        )
        self.assertNotEqual(entity.id, entity.UID())
        self.assertEqual(entity.id, "entity")

    def test_js_bundles(self):
        event = api.content.create(
            container=self.agenda,
            type="imio.events.Event",
            title="Event",
        )

        alsoProvides(self.request, IImioEventsCoreLayer)
        getMultiAdapter((event, self.request), name="view")()
        bundles = getattr(self.request, "enabled_bundles", [])
        self.assertEqual(len(bundles), 0)
        api.content.create(
            container=event,
            type="Image",
            title="Image",
        )
        getMultiAdapter((event, self.request), name="view")()
        bundles = getattr(self.request, "enabled_bundles", [])
        self.assertEqual(len(bundles), 2)
        self.assertListEqual(bundles, ["spotlightjs", "flexbin"])

    def test_has_contact(self):
        event = api.content.create(
            container=self.folder,
            type="imio.events.Event",
            id="my-event",
        )
        view = queryMultiAdapter((event, self.request), name="view")
        self.assertEqual(view.has_contact(), False)
        event.contact_name = "Mike 'Billy' Bainbridge"
        self.assertEqual(view.has_contact(), True)
        event.contact_name = None
        event.contact_email = "billy@plone.org"
        self.assertEqual(view.has_contact(), True)
        event.contact_email = None
        event.contact_phone = "01123456"
        self.assertEqual(view.has_contact(), True)

    def test_address(self):
        event = api.content.create(
            container=self.folder,
            type="imio.events.Event",
            id="my-event",
        )
        view = queryMultiAdapter((event, self.request), name="view")
        self.assertEqual(view.address(), "")
        event.street = "Rue Léon Morel"
        self.assertEqual(view.address(), "Rue Léon Morel")
        event.city = "Gembloux"
        self.assertEqual(view.address(), "Rue Léon Morel Gembloux")
        event.country = "be"
        self.assertEqual(view.address(), "Rue Léon Morel Gembloux Belgique")

    def test_iam(self):
        event = api.content.create(
            container=self.folder,
            type="imio.events.Event",
            id="my-event",
        )
        view = queryMultiAdapter((event, self.request), name="view")
        self.assertEqual(view.iam(), None)
        event.iam = ["young", "parent"]
        self.assertEqual(view.iam(), "Jeune, Parent")

    def test_topics(self):
        event = api.content.create(
            container=self.folder,
            type="imio.events.Event",
            id="my-event",
        )
        view = queryMultiAdapter((event, self.request), name="view")
        self.assertEqual(view.topics(), None)
        event.topics = ["citizen_participation", "sports"]
        self.assertEqual(view.topics(), "Participation citoyenne, Sports")

    def test_category(self):
        event = api.content.create(
            container=self.folder,
            type="imio.events.Event",
            id="my-event",
        )
        view = queryMultiAdapter((event, self.request), name="view")
        self.assertEqual(view.topics(), None)
        event.category = "exhibition_artistic_meeting"
        self.assertEqual(view.category(), "Exposition et rencontre artistique")
