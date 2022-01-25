# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from embeddify import Embedder
from imio.smartweb.common.utils import translate_vocabulary_term
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.event.browser.event_view import EventView
from Products.CMFPlone.resources import add_bundle_on_request
from zope.i18n import translate

import json


class View(EventView, FolderView):
    def __call__(self):
        images = self.context.listFolderContents(contentFilter={"portal_type": "Image"})
        if len(images) > 0:
            add_bundle_on_request(self.request, "spotlightjs")
            add_bundle_on_request(self.request, "flexbin")
        return self.index()

    def files(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "File"})

    def images(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "Image"})

    def has_leadimage(self):
        if ILeadImage.providedBy(self.context) and getattr(
            self.context, "image", False
        ):
            return True
        return False

    def get_embed_video(self):
        embedder = Embedder(width=800, height=600)
        return embedder(self.context.video_url, params=dict(autoplay=False))

    def category(self):
        title = translate_vocabulary_term(
            "imio.events.vocabulary.EventsCategories", self.context.category
        )
        if title:
            return title

    def topics(self):
        topics = self.context.topics
        if topics is None:
            return
        items = []
        for item in topics:
            title = translate_vocabulary_term("imio.smartweb.vocabulary.Topics", item)
            items.append(title)
        return ", ".join(items)

    def iam(self):
        iam = self.context.iam
        if iam is None:
            return
        items = []
        for item in iam:
            title = translate_vocabulary_term("imio.smartweb.vocabulary.IAm", item)
            items.append(title)
        return ", ".join(items)

    def data_geojson(self):
        """Return the contact geolocation as GeoJSON string."""
        current_lang = api.portal.get_current_language()[:2]
        coordinates = IGeolocatable(self.context).geolocation
        longitude = coordinates.longitude
        latitude = coordinates.latitude
        link_text = translate(_("Itinerary"), target_language=current_lang)
        geo_json = {
            "type": "Feature",
            "properties": {
                "popup": '<a href="{}">{}</a>'.format(
                    self.get_itinerary_link(), link_text
                ),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    longitude,
                    latitude,
                ],
            },
        }
        return json.dumps(geo_json)

    def get_itinerary_link(self):
        if not self.context.is_geolocated:
            return
        if not self.address or self.address() == "":
            return
        return "https://www.google.com/maps/dir/?api=1&destination={}".format(
            self.address("+")
        )

    def address(self, separator=" "):
        address_parts = [
            self.context.street,
            self.context.number and str(self.context.number) or "",
            self.context.complement,
            self.context.zipcode and str(self.context.zipcode) or "",
            self.context.city,
        ]
        if self.context.country:
            term = translate_vocabulary_term(
                "imio.smartweb.vocabulary.Countries", self.context.country
            )
            address_parts.append(term)
        address = f"{separator}".join(filter(None, address_parts))
        return address

    def has_contact(self):
        name = self.context.contact_name
        mail = self.context.contact_email
        phone = self.context.contact_phone
        return True if name or mail or phone is not None else False
