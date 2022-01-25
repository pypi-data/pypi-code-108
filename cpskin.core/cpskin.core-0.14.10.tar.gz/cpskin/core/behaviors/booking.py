# -*- coding: utf-8 -*-
from cpskin.locales import CPSkinMessageFactory as _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IBooking(model.Schema):

    directives.order_after(booking_type='IDublinCore.description')
    booking_type = schema.Choice(
        title=_(u'Booking type'),
        required=False,
        vocabulary=u'cpskin.core.vocabularies.booking_types',
    )

    directives.order_after(booking_price='.booking_type')
    booking_price = schema.Text(
        title=_(u'Price'),
        required=False,
    )

    directives.order_after(booking_url='.booking_price')
    booking_url = schema.URI(
        title=_(u'Booking URL'),
        required=False,
    )
