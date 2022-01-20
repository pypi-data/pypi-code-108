# -*- coding: utf-8 -*-
from collective.contact.core.adapters import ContactDetailsVCard
from collective.contact.core.adapters import OrganizationVCard
from collective.contact.core.interfaces import IContactable
from collective.documentgenerator.content.condition import ConfigurablePODTemplateCondition  # noqa
from imio.dashboard.content.pod_template import DashboardPODTemplateCondition as DPTC  # noqa
from Products.CMFPlone.utils import safe_unicode

import vobject


class DashboardPODTemplateCondition(DPTC):

    def evaluate(self):
        return super(ConfigurablePODTemplateCondition, self).evaluate()


def get_vcard(context):
    vcard = vobject.vCard()
    contactable = IContactable(context)
    contact_details = contactable.get_contact_details()

    email = contact_details['email']
    if email:
        vcard.add('email')
        vcard.email.type_param = 'INTERNET'
        vcard.email.value = email

    phones = contact_details['phone']
    if not isinstance(phones, list):
        phones = [phones]
    for phone in phones:
        if phone:
            vcard.add('tel')
            vcard.tel.type_param = 'WORK'
            vcard.tel.value = phone

    cell_phones = contact_details['cell_phone']
    if not isinstance(cell_phones, list):
        cell_phones = [cell_phones]
    for cell_phone in cell_phones:
        if cell_phone:
            vcard.add('tel')
            last_item = len(vcard.tel_list) - 1
            vcard.tel_list[last_item].type_param = 'CELL'
            vcard.tel_list[last_item].value = cell_phone

    im_handle = contact_details['im_handle']
    if im_handle:
        vcard.add('impp')
        vcard.impp.value = im_handle

    address = contact_details['address']

    # if we don't have relevant address information, we don't need address
    if address:
        vcard.add('adr')
        country = safe_unicode(address['country'], encoding='utf8')
        region = safe_unicode(address['region'], encoding='utf8')
        zip_code = safe_unicode(address['zip_code'], encoding='utf8')
        city = safe_unicode(address['city'], encoding='utf8')
        street = safe_unicode(address['street'], encoding='utf8')
        number = safe_unicode(address['number'], encoding='utf8')
        additional = safe_unicode(address['additional_address_details'],
                                  encoding='utf8')
        vcard.adr.value = vobject.vcard.Address(street=street,
                                                city=city,
                                                region=region,
                                                code=zip_code,
                                                country=country,
                                                box=number,
                                                extended=additional)
    return vcard


class CPskinContactDetailsVCard(ContactDetailsVCard):

    def get_vcard(self):
        vcard = get_vcard(self.context)
        vcard.add('fn')
        vcard.fn.value = safe_unicode(self.context.Title())
        vcard.add('n')
        vcard.n.value = vobject.vcard.Name(safe_unicode(self.context.Title()))
        return vcard


class CPskinOrganizationVCard(OrganizationVCard):
    """Override from OrganizationVCard to get multi phones and mutli
    cell_phones on vcard export"""

    def get_vcard(self):
        vcard = get_vcard(self.context)
        vcard.add('kind')
        vcard.kind.value = 'org'

        organization = self.context
        title = safe_unicode(organization.Title(), encoding='utf8')
        vcard.add('n')
        vcard.n.value = vobject.vcard.Name(title)
        vcard.add('fn')
        vcard.fn.value = title
        return vcard
