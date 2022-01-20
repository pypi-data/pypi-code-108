# -*- coding: utf-8 -*-
"""
cpskin.core
-----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.contact.core.browser.contactable import ContactDetails
from collective.contact.core.interfaces  import IContactable
from collective.geo.geographer.geoview import GeoView
from cpskin.core import utils
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ua_parser import user_agent_parser

import os
import six


class ContactDetailsView(BrowserView, ContactDetails):

    template_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'templates',
        'address.pt',
    )

    def __call__(self):
        self.update()
        return super(ContactDetailsView, self).__call__()

    def update(self):
        fallback = self.is_contact_core_fallback()
        contactable = IContactable(self.context)
        #noFallbackContactDetails or fallback.
        self.contact_details = contactable.get_contact_details(fallback=fallback)

    def is_contact_core_fallback(self):
        portal_registry = api.portal.get_tool('portal_registry')
        return portal_registry['cpskin.core.interfaces.ICPSkinSettings.person_contact_core_fallback']  # noqa


    @property
    def phones(self):
        phones = self.contact_details.get('phone', [])
        if isinstance(phones, six.string_types):
            phones = [phones]
        return [utils.format_phone(v) for v in phones]

    @property
    def cell_phones(self):
        cell_phones = self.contact_details.get('cell_phone', [])
        if isinstance(cell_phones, six.string_types):
            cell_phones = [cell_phones]
        return [utils.format_phone(v) for v in cell_phones]

    @property
    def fax(self):
        fax = self.contact_details.get('fax')
        if fax:
            return utils.format_phone(fax)

    def geo_converter(self, longitude, latitude):
        infos = user_agent_parser.Parse(self.request.get('HTTP_USER_AGENT'))
        links = {
            'Mac OS X': 'maps:?q={longitude},{latitude}',
            'iOS': 'maps:?q={longitude},{latitude}',
            'Android': 'geo:?q={longitude},{latitude}',
            'Windows Phone': 'maps:?q={longitude},{latitude}',
            'Windows 10': 'maps:?q={longitude},{latitude}',
            'Windows': 'maps:?q={longitude},{latitude}',
        }
        if infos['os']['family'] not in links:
            return '#map'
        return links[infos['os']['family']].format(
            longitude=longitude,
            latitude=latitude,
        )

    @property
    def geo_link(self):
        geo_view = GeoView(self.context, self.request)
        if geo_view.hasCoordinates():
            coordinates = geo_view.getCoordinates()
            return self.geo_converter(
                coordinates[1][1],
                coordinates[1][0],
            )

    def render_address(self):
        link = self.geo_link
        template = ViewPageTemplateFile(self.template_path)
        return template(self, self.contact_details['address'], link)
