# -*- coding: utf-8 -*-

from zope.interface import alsoProvides
from collective.dms.scanbehavior.behaviors.behaviors import IScanFields
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives as form


class IScanFieldsHiddenToSignAndSigned(IScanFields):

    form.omitted('to_sign')
    form.omitted('signed')

alsoProvides(IScanFieldsHiddenToSignAndSigned, IFormFieldProvider)
