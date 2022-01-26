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
Data Models for People
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

from .core import Base, uuid_column, Note
from .contact import PhoneNumber, EmailAddress, MailingAddress, ContactMixin
from rattail.db.util import normalize_full_name


# TODO: deprecate/remove this
def get_person_display_name(first_name, last_name):
    return normalize_full_name(first_name, last_name)

# TODO: rename this?
def get_person_display_name_from_context(context):
    first_name = context.current_parameters.get('first_name')
    last_name = context.current_parameters.get('last_name')
    return normalize_full_name(first_name, last_name)


class Person(ContactMixin, Base):
    """
    Represents a real, living and breathing person.

    (Or, at least was previously living and breathing, in the case of the
    deceased.)
    """
    __tablename__ = 'person'
    __versioned__ = {
        'exclude': ['modified'],
    }

    uuid = uuid_column()
    first_name = sa.Column(sa.String(length=50), nullable=True)
    middle_name = sa.Column(sa.String(length=50), nullable=True)
    last_name = sa.Column(sa.String(length=50), nullable=True)
    # TODO: rename this to 'full_name' at some point...?
    display_name = sa.Column(sa.String(length=100), nullable=True)

    local_only = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the person is somehow specific to the "local" app node
    etc. and should not be synced elsewhere.
    """)

    invalid_address = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the person's mailing address(es) on file are invalid.
    """)

    modified = sa.Column(sa.DateTime(), nullable=True, onupdate=datetime.datetime.utcnow)

    users = orm.relationship(
        'User', doc="""
        List of user accounts associated with this person.
        """)

    def __str__(self):
        if six.PY2:
            return unicode(self).encode('utf8')
        return self.display_name or ""

    if six.PY2:
        def __unicode__(self):
            return self.display_name or ""

    # TODO: deprecate / remove this
    def add_email_address(self, address, type='Home', flush=False):
        email = self.add_email(type=type, address=address, flush=flush)
        return email

    # TODO: deprecate / remove this
    def add_phone_number(self, number, type='Home', flush=False):
        phone = self.add_phone(type=type, number=number, flush=flush)
        return phone

    # TODO: deprecate / remove this
    def first_valid_email(self):
        """
        Returns the first :class:`Email` which has not been marked invalid, or ``None``.
        """
        for email in self.emails:
            if not email.invalid:
                return email

    # TODO: deprecate / remove this
    def first_valid_email_address(self):
        """
        Returns the first email address which has not been marked invalid, or ``None``.
        """
        email = self.first_valid_email()
        if email:
            return email.address

    def only_customer(self, require=True):
        """
        Convenience method to retrieve the one and only ``Customer`` record
        which is associated with this person.  An error will be raised if there
        is not exactly one customer associated.
        """
        if len(self.customers) > 1 or (require and not self.customers):
            raise ValueError("person {} should have 1 customer but instead has {}: {}".format(
                self.uuid, len(self.customers), self))
        return self.customers[0] if self.customers else None


class PersonContactInfoMixin(object):
    """
    Base mixin class for person contact info models.
    """
    Parent = Person

    @declared_attr
    def parent(cls):
        return orm.synonym('person')


class PersonPhoneNumber(PersonContactInfoMixin, PhoneNumber):
    """
    Represents a phone (or fax) number associated with a person.
    """
    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person._contact_phone_model = PersonPhoneNumber

Person.phones = orm.relationship(
    PersonPhoneNumber,
    primaryjoin=PersonPhoneNumber.parent_uuid == Person.uuid,
    foreign_keys=[PersonPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan',
    doc="""
    Sequence of :class:`PersonPhoneNUmber` instances which belong to the
    person.
    """,
    backref=orm.backref(
        'person',
        doc="""
        Reference to the :class:`Person` instance to which the phone number
        belongs.
        """),
)

Person.phone = orm.relationship(
    PersonPhoneNumber,
    primaryjoin=sa.and_(
        PersonPhoneNumber.parent_uuid == Person.uuid,
        PersonPhoneNumber.preference == 1,
        ),
    foreign_keys=[PersonPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class PersonEmailAddress(PersonContactInfoMixin, EmailAddress):
    """
    Represents an email address associated with a person.
    """
    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person._contact_email_model = PersonEmailAddress

Person.emails = orm.relationship(
    PersonEmailAddress,
    primaryjoin=PersonEmailAddress.parent_uuid == Person.uuid,
    foreign_keys=[PersonEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan',
    doc="""
    Sequence of :class:`PersonEmailAddress` instances which belong to the
    person.
    """,
    backref=orm.backref(
        'person',
        doc="""
        Reference to the :class:`Person` instance to which the email address
        belongs.
        """),
)

Person.email = orm.relationship(
    PersonEmailAddress,
    primaryjoin=sa.and_(
        PersonEmailAddress.parent_uuid == Person.uuid,
        PersonEmailAddress.preference == 1,
        ),
    foreign_keys=[PersonEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class PersonMailingAddress(PersonContactInfoMixin, MailingAddress):
    """
    Represents a physical / mailing address associated with a person.
    """
    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person._contact_address_model = PersonMailingAddress

Person.addresses = orm.relationship(
    PersonMailingAddress,
    backref='person',
    primaryjoin=PersonMailingAddress.parent_uuid == Person.uuid,
    foreign_keys=[PersonMailingAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonMailingAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Person.address = orm.relationship(
    PersonMailingAddress,
    primaryjoin=sa.and_(
        PersonMailingAddress.parent_uuid == Person.uuid,
        PersonMailingAddress.preference == 1,
        ),
    foreign_keys=[PersonMailingAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class PersonNote(Note):
    """
    Represents a note attached to a person.
    """
    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person.notes = orm.relationship(
    PersonNote,
    primaryjoin=PersonNote.parent_uuid == Person.uuid,
    foreign_keys=[PersonNote.parent_uuid],
    order_by=PersonNote.created,
    cascade='all, delete-orphan',
    doc="""
    Sequence of notes which belong to the person.
    """,
    backref=orm.backref(
        'person',
        doc="""
        Reference to the person to which the note is attached.
        """))


@six.python_2_unicode_compatible
class MergePeopleRequest(Base):
    """
    Represents a *request* to merge 2 people.  If the request is no
    longer wanted then it should be deleted.  Otherwise it should be
    updated to reflect who satisfies the request, by performing the
    merge.
    """
    __tablename__ = 'merge_request_people'
    __table_args__ = (
        sa.ForeignKeyConstraint(['requested_by_uuid'], ['user.uuid'],
                                name='merge_request_people_fk_requested_by'),
        sa.ForeignKeyConstraint(['merged_by_uuid'], ['user.uuid'],
                                name='merge_request_people_fk_merged_by'),
    )

    uuid = uuid_column()

    removing_uuid = sa.Column(sa.String(length=32), nullable=False, doc="""
    UUID of the "unwanted" person, which is to be merged into the
    "preserved" person.
    """)

    keeping_uuid = sa.Column(sa.String(length=32), nullable=False, doc="""
    UUID of the person to be "preserved", into which the "unwanted"
    person is to be merged.
    """)

    requested = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the request was made.
    """)

    requested_by_uuid = sa.Column(sa.String(length=32), nullable=False)
    requested_by = orm.relationship(
        'User',
        foreign_keys=[requested_by_uuid],
        doc="""
        Reference to the User who created the request.
        """)

    merged = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the merge was performed.
    """)

    merged_by_uuid = sa.Column(sa.String(length=32), nullable=True)
    merged_by = orm.relationship(
        'User',
        foreign_keys=[merged_by_uuid],
        doc="""
        Reference to the User who performed the merge.
        """)

    def __str__(self):
        return "Person Merge Request: {} -> {}".format(
            self.removing_uuid, self.keeping_uuid)
