# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data Models for Contact Info
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm

from .core import Base, uuid_column


@six.python_2_unicode_compatible
class PhoneNumber(Base):
    """
    Represents a phone (or fax) number associated with a contactable entity.
    """
    __tablename__ = 'phone'
    __table_args__ = (
        sa.Index('phone_ix_parent', 'parent_type', 'parent_uuid'),
    )
    __versioned__= {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    type = sa.Column(sa.String(length=15))
    number = sa.Column(sa.String(length=20), nullable=False)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __str__(self):
        return self.number or ""

    @property
    def preferred(self):
        return self.preference == 1


@six.python_2_unicode_compatible
class EmailAddress(Base):
    """
    Represents an email address associated with a contactable entity.
    """
    __tablename__ = 'email'
    __table_args__ = (
        sa.Index('email_ix_parent', 'parent_type', 'parent_uuid'),
    )
    __versioned__= {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    type = sa.Column(sa.String(length=15))
    address = sa.Column(sa.String(length=255), nullable=False)

    invalid = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the email address is *known* to be invalid.
    Defaults to NULL, meaning the validity is "not known".
    """)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __str__(self):
        return self.address or ""

    @property
    def preferred(self):
        return self.preference == 1


@six.python_2_unicode_compatible
class MailingAddress(Base):
    """
    Represents a physical / mailing address associated with a contactable entity.
    """
    __tablename__ = 'address'
    __table_args__ = (
        sa.Index('address_ix_parent', 'parent_type', 'parent_uuid'),
    )
    __versioned__= {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    type = sa.Column(sa.String(length=15), nullable=True)

    street = sa.Column(sa.String(length=100), nullable=True)
    street2 = sa.Column(sa.String(length=100), nullable=True)
    city = sa.Column(sa.String(length=60), nullable=True)
    state = sa.Column(sa.String(length=2), nullable=True)
    zipcode = sa.Column(sa.String(length=10), nullable=True)
    invalid = sa.Column(sa.Boolean(), nullable=True)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __str__(self):

        if self.street and self.street2:
            street = '{}, {}'.format(self.street, self.street2)
        else:
            street = self.street or ''

        if self.city and self.state:
            city = '{}, {}'.format(self.city, self.state)
        else:
            city = self.city or self.state or ''

        if street and city and self.zipcode:
            text = '{}, {}  {}'.format(street, city, self.zipcode)
        elif street and city:
            text = '{}, {}'.format(street, city)
        elif street and self.zipcode:
            text = '{}  {}'.format(street, self.zipcode)
        elif city and self.zipcode:
            text = '{}  {}'.format(city, self.zipcode)
        else:
            text = city or self.zipcode or ''

        return text

    @property
    def preferred(self):
        return self.preference == 1


class ContactMixin(object):
    """
    Mixin which provides some useful methods for "contact" models, i.e. those
    which can play "parent" to email, phone and address records.
    """
    # TODO: subclass must set these
    _contact_email_model = None
    _contact_phone_model = None
    _contact_address_model = None

    def first_email(self, invalid=False, **kwargs):
        """
        Return the first available email record for the contact.

        :param invalid: If true, then this may return an email marked
           invalid; if false then only valid email will be returned.
        """
        if invalid:
            emails = self.emails
        else:
            emails = [email for email in self.emails
                      if not email.invalid]
        if emails:
            return emails[0]

    def first_email_address(self, invalid=False, **kwargs):
        """
        Return the first available email address for the contact.
        """
        email = self.first_email(invalid=invalid)
        if email:
            return email.address

    def make_email(self, **kwargs):
        """
        Make a new "email" record for the contact.
        """
        email = self._contact_email_model(**kwargs)
        return email

    def add_email(self, **kwargs):
        """
        Add a new "email" record to the contact.
        """
        flush = kwargs.pop('flush', True)
        email = self.make_email(**kwargs)
        self.emails.append(email)
        if flush:
            session = orm.object_session(self)
            session.flush()
        return email

    def set_primary_email(self, email, flush=True):
        """
        Will re-arrange the contact's email records as needed to ensure that
        the given ``email`` record is "primary" - i.e. first in the list.
        """
        if email.preference != 1:
            session = orm.object_session(self)
            contact = email.parent
            if not contact:
                contact = session.query(email.Parent).get(email.parent_uuid)
                if not contact:
                    raise ValueError("cannot locate parent {} contact for email: {}".format(
                        email.Parent.__name__, email))
            emails = contact.emails
            if email in emails:
                emails.remove(email)
            emails.insert(0, email)
            emails.reorder()
            if flush:
                session.flush()

    def remove_email(self, email, **kwargs):
        """
        Remove the given email record from the contact.
        """
        flush = kwargs.pop('flush', True)
        self.emails.remove(email)
        if flush:
            session = orm.object_session(self)
            session.flush()

    def first_phone(self, **kwargs):
        """
        Return the first available phone record for the contact.
        """
        if self.phones:
            return self.phones[0]

    def first_phone_number(self, **kwargs):
        """
        Return the first available phone number for the contact.
        """
        phone = self.first_phone()
        if phone:
            return phone.number

    def make_phone(self, **kwargs):
        """
        Make a new "phone" record for the contact.
        """
        # set some safe defaults in case session is flushed early
        kwargs.setdefault('number', '')
        phone = self._contact_phone_model(**kwargs)
        return phone

    def add_phone(self, **kwargs):
        """
        Add a new "phone" record to the contact.
        """
        flush = kwargs.pop('flush', True)
        phone = self.make_phone(**kwargs)
        self.phones.append(phone)
        if flush:
            session = orm.object_session(self)
            session.flush()
        return phone

    def remove_phone(self, phone, **kwargs):
        """
        Remove the given phone record from the contact.
        """
        flush = kwargs.pop('flush', True)
        self.phones.remove(phone)
        if flush:
            session = orm.object_session(self)
            session.flush()

    def set_primary_phone(self, phone, flush=True):
        """
        Will re-arrange the contact's phone records as needed to ensure that
        the given ``phone`` record is "primary" - i.e. first in the list.
        """
        if phone.preference != 1:
            session = orm.object_session(self)
            contact = phone.parent
            if not contact:
                contact = session.query(phone.Parent).get(phone.parent_uuid)
                if not contact:
                    raise ValueError("cannot locate parent {} contact for phone: {}".format(
                        phone.Parent.__name__, phone))
            phones = contact.phones
            if phone in phones:
                phones.remove(phone)
            phones.insert(0, phone)
            phones.reorder()
            if flush:
                session.flush()

    def first_address(self, **kwargs):
        """
        Return the first available address record for the contact.
        """
        if self.addresses:
            return self.addresses[0]

    def make_address(self, **kwargs):
        """
        Make a new "address" record for the contact.
        """
        address = self._contact_address_model(**kwargs)
        return address

    def add_address(self, **kwargs):
        """
        Add a new "address" record to the contact.
        """
        flush = kwargs.pop('flush', True)
        address = self.make_address(**kwargs)
        self.addresses.append(address)
        if flush:
            session = orm.object_session(self)
            session.flush()
        return address

    def set_primary_address(self, address, flush=True):
        """
        Will re-arrange the contact's address records as needed to ensure that
        the given ``address`` record is "primary" - i.e. first in the list.
        """
        if address.preference != 1:
            session = orm.object_session(self)
            contact = address.parent
            if not contact:
                contact = session.query(address.Parent).get(address.parent_uuid)
                if not contact:
                    raise ValueError("cannot locate parent {} contact for address: {}".format(
                        address.Parent.__name__, address))
            addresses = contact.addresses
            if address in addresses:
                addresses.remove(address)
            addresses.insert(0, address)
            addresses.reorder()
            if flush:
                session.flush()

    def remove_address(self, address, **kwargs):
        """
        Remove the given address record from the contact.
        """
        flush = kwargs.pop('flush', True)
        self.addresses.remove(address)
        if flush:
            session = orm.object_session(self)
            session.flush()
