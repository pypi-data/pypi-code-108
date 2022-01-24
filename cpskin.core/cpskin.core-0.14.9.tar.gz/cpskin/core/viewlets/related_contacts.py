# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.contact.core.browser.address import get_address
from collective.contact.core.interfaces import IContactable
from collective.geo.json.browser.jsonview import get_marker_image
from collective.geo.leaflet.interfaces import IGeoMap
from collective.geo.mapwidget import utils
from cpskin.core.utils import format_phone
from plone import api
from plone.app.layout.viewlets import common
from plone.dexterity.utils import safe_unicode
from plone.dexterity.utils import safe_utf8
from plone.outputfilters.filters.resolveuid_and_caption import (
    ResolveUIDAndCaptionFilter,
)  # noqa
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from pygeoif.geometry import as_shape

import geojson
import logging
import Missing


logger = logging.getLogger("cpskin.core related contacts viewlet")


class RelatedContactsViewlet(common.ViewletBase):

    index = ViewPageTemplateFile("related_contacts.pt")
    address_fields = (
        "street",
        "number",
        "zip_code",
        "city",
        "additional_address_details",
        "region",
        "country",
    )
    coordinates_fields = (
        "phone",
        "cell_phone",
        "fax",
        "email",
        "im_handle",
        "website",
        "schedule",
    )
    ignore_fields = ("title",)

    def __init__(
        self, context, request, view, manager=None, field="", selected=""
    ):  # noqa
        super(RelatedContactsViewlet, self).__init__(context, request, view, manager)
        self.field = field
        self.selected = selected
        self.pc = api.portal.get_tool("portal_catalog")

    def available(self):
        context = aq_base(self.context)
        return bool(getattr(context, self.field, None))

    @property
    def selected_fields(self):
        return getattr(self.context, self.selected, None)

    def get_contacts(self):
        contacts = []
        if isinstance(self.field, list):
            related_contacts = []
            for field in self.field:
                related_contacts += getattr(self.context, field, [])
        else:
            related_contacts = getattr(self.context, self.field, [])
        for related_contact in related_contacts:
            if related_contact.isBroken():
                related_contacts.remove(related_contact)
                setattr(self.context, self.field, related_contacts)
            obj = related_contact.to_object
            if obj not in contacts:
                contacts.append(obj)
        return contacts

    def get_title(self, contact):
        if self.in_fields("title"):
            return u'<span class="related-contact-title">{0}</span>'.format(
                contact.title
            )
        else:
            return False

    def in_fields(self, field):
        return field in self.selected_fields

    def get_field(self, contact, field_name):
        if field_name is "id":
            return getattr(contact, field_name, "")
        if field_name not in self.selected_fields:
            return ""
        if field_name in self.address_fields:
            contactable = IContactable(contact)
            details = contactable.get_contact_details()
            return details["address"].get(field_name)
        # field = getattr(contact, field_name, '')
        # find way to check if field is richetext or image or simple field
        if getattr(getattr(contact, field_name, ""), "raw", None):
            if getattr(contact, field_name, ""):
                text = getattr(contact, field_name).raw
                text = text.replace("http://resolveuid/", "resolveuid/")
                parser = ResolveUIDAndCaptionFilter(contact)
                transform_text = parser(text)
                return transform_text if transform_text else ""
        if field_name in ["logo", "photo"]:
            if getattr(contact, field_name, ""):
                img = contact.unrestrictedTraverse("@@images")
                logo = img.scale(field_name)
                return logo.tag() if logo.tag() else ""
        if field_name == "schedule":
            from plone.directives import dexterity

            display = dexterity.DisplayForm(contact, self.request)
            display.update()
            if display.w.get("IScheduledContent.schedule", None):
                return display.w.get("IScheduledContent.schedule").render()
            else:
                return ""
        if field_name in ["phone", "cell_phone", "fax"]:
            phones = getattr(contact, field_name, "")
            if not phones:
                return False
            if not isinstance(phones, list):
                phones = [getattr(contact, field_name)]
            return [format_phone(phone) for phone in phones]
        if field_name in ["position"]:
            positions = [pos.title.strip() for pos in contact.get_held_positions()]
            return ", ".join(positions)
        return getattr(contact, field_name, "")

    def has_address(self):
        i = 0
        for address_field in self.address_fields:
            if address_field in self.selected_fields:
                i += 1
        return i >= 3

    def fields_without_address(self):
        fields = []
        for selected_field in self.selected_fields:
            if (
                selected_field not in self.address_fields
                and selected_field not in self.ignore_fields
                and selected_field not in self.coordinates_fields
            ):
                fields.append(selected_field)
        return fields

    def get_website(self, contact):
        website = self.get_field(contact, "website")
        if website.startswith("http"):
            url = website
            website_name = website.replace("http://", "")
        elif website.startswith("https"):
            url = website
            website_name = website.replace("https://", "")
        else:
            url = "http://{0}".format(website)
            website_name = website
        html = ""
        html += '<a class="website" href="{0}" target="_blank">{1}</a>'.format(
            url, website_name
        )
        return html

    def see_map_link(self, contact):
        if self.available:
            obj = contact
            if contact.use_parent_address:
                obj = contact.aq_parent
            brain = self.pc.unrestrictedSearchResults(UID=obj.UID())[0]
            if brain.zgeo_geometry == Missing.Value:
                return False
            if not getattr(self.context, "see_map", True):
                return False
            return True
        return False


class AboveRelatedContactsViewlet(RelatedContactsViewlet):
    def __init__(self, context, request, view, manager=None):
        field = "aboveContentContact"
        selected = "aboveVisbileFields"
        super(AboveRelatedContactsViewlet, self).__init__(
            context, request, view, manager, field, selected
        )


class BelowRelatedContactsViewlet(RelatedContactsViewlet):
    def __init__(self, context, request, view, manager=None):
        field = "belowContentContact"
        selected = "belowVisbileFields"
        super(BelowRelatedContactsViewlet, self).__init__(
            context, request, view, manager, field, selected
        )

    def get_title(self, contact):
        if self.in_fields("title"):
            return u'<a href="{0}" target="_blank"><h4>{1}</h4></a>'.format(
                contact.absolute_url(), safe_unicode(contact.title)
            )
        else:
            return False


class RelatedContactsMapViewlet(RelatedContactsViewlet):
    index = ViewPageTemplateFile("related_contacts_map.pt")

    def __init__(self, context, request, view, manager=None):
        self.fields = ["aboveContentContact", "belowContentContact"]
        super(RelatedContactsMapViewlet, self).__init__(
            context, request, view, manager, self.fields
        )

    def available(self):
        context = aq_base(self.context)
        see_map = getattr(context, "see_map", False)
        empty_content = True
        for field in self.fields:
            if len(getattr(context, field, [])) > 0:
                empty_content = False
        return see_map and not empty_content

    @property
    def geomap(self):
        return IGeoMap(self.context)

    def data_geojson(self):
        style = {}
        global_style = utils.get_feature_styles(self.context)
        style["fill"] = global_style["polygoncolor"]
        style["stroke"] = global_style["linecolor"]
        style["width"] = global_style["linewidth"]
        if global_style.get("marker_image", None):
            img = get_marker_image(self.context, global_style["marker_image"])
            style["image"] = img
        else:
            style["image"] = None
        json_result = []
        self.pc = api.portal.get_tool("portal_catalog")
        for contact in self.get_contacts():
            brain = self.pc.unrestrictedSearchResults(UID=contact.UID())[0]
            if contact.use_parent_address:
                brain = self.pc.unrestrictedSearchResults(UID=contact.aq_parent.UID())[
                    0
                ]
            if brain.zgeo_geometry == Missing.Value:
                continue
            if brain.collective_geo_styles == Missing.Value:
                continue
            if brain.collective_geo_styles.get(
                "use_custom_styles", False
            ) and brain.collective_geo_styles.get("marker_image", None):
                img = get_marker_image(
                    self.context, brain.collective_geo_styles["marker_image"]
                )
                style["image"] = img
            geom = {
                "type": brain.zgeo_geometry["type"],
                "coordinates": brain.zgeo_geometry["coordinates"],
            }
            if geom["coordinates"]:
                if geom["type"]:
                    classes = geom["type"].lower() + " "
                else:
                    classes = ""
                address = get_address(contact)
                number = ""
                if address.get("number", None):
                    number = ", {0}".format(address["number"])
                formated_address = "{0}{1}<br />{2} {3}".format(
                    safe_utf8(address.get("street") or ""),
                    number,
                    address.get("zip_code") or "",
                    safe_utf8(address.get("city") or ""),
                )
                img = ""
                if self.context.see_logo_in_popup:
                    acc = getattr(contact, "logo", None)
                    if acc and acc.filename:
                        img = "{0}/@@images/logo/thumb".format(contact.absolute_url())
                classes += brain.getPath().split("/")[-2].replace(".", "-")
                json_result.append(
                    geojson.Feature(
                        id=contact.id.replace(".", "-"),
                        geometry=as_shape(geom),
                        style=style,
                        properties={
                            "title": brain.Title,
                            "description": brain.Description,
                            "style": style,
                            "url": brain.getURL(),
                            "classes": classes,
                            "image": img,
                            "address": formated_address,
                        },
                    )
                )
        feature_collection = geojson.FeatureCollection(json_result)
        feature_collection.update({"title": self.context.title})
        return geojson.dumps(feature_collection)
