# -*- coding: utf-8 -*-

from plone import api
from zope.component import getUtility

from collective.sendinblue.interfaces import ISendinblueAPI


def install_recaptcha(context):
    profile_id = 'profile-plone.formwidget.recaptcha:default'
    setup = api.portal.get_tool('portal_setup')
    setup.runAllImportStepsFromProfile(profile_id)


def update_cache(context):
    sendinblue = getUtility(ISendinblueAPI)
    sendinblue.updateCache()
