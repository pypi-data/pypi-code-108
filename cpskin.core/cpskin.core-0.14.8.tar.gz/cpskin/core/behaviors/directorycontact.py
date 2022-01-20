# -*- coding: utf-8 -*-
from collective.contact.core import _ as CCMF
from collective.contact.core.behaviors import IContactDetails
from cpskin.core.browser.widget import multiline_field_widget
from cpskin.locales import CPSkinMessageFactory as _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider

import re


_PHONE_RE = re.compile(r'[+]?[0-9 \(\)\/\.]*$')


class InvalidPhone(schema.ValidationError):
    """Exception for invalid address"""
    __doc__ = _(u'Invalid phone')


def validatePhone(value):
    """Simple email validator"""
    if not _PHONE_RE.match(value):
        raise InvalidPhone(value)
    return True


def validate_phones(values):
    for value in values:
        validatePhone(value)
    return True


@provider(IFormFieldProvider)
class IDirectoryContactDetails(IContactDetails):

    form.widget(phone=multiline_field_widget)
    phone = schema.List(
        title=_(u'Phones'),
        required=False,
        constraint=validate_phones,
    )

    form.widget(cell_phone=multiline_field_widget)
    cell_phone = schema.List(
        title=CCMF(u'Cell phone'),
        required=False,
        constraint=validate_phones,
    )
