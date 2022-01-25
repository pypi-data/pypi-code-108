# -*- coding: utf-8 -*-

from imio.gdpr import _
from imio.gdpr import get_default_text
from imio.gdpr import get_default_cookies_text
from imio.gdpr.interfaces import IGDPRSettings
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile
from plone.registry import field
from plone.registry import Record
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def udpate_default_template(context):
    text = get_default_text(api.portal.get())
    api.portal.set_registry_record('text', text, interface=IGDPRSettings)


def reload_gs_profile(context):
    loadMigrationProfile(
        context,
        'profile-imio.gdpr:default',
    )


def add_cookie_policy(context):
    registry = getUtility(IRegistry)
    records = registry.records
    if 'imio.gdpr.interfaces.IGDPRSettings.cookies_text' in records:
        return
    record = Record(
        field.Text(
            title=_(u'title_cookies_text', default=u'Cookies text'),
            description=_(
                u'help_cookies_text',
                default=u'The text of the Cookies Policy page.'),
            required=True,
        ),
        value=get_default_cookies_text(context)
    )
    records['imio.gdpr.interfaces.IGDPRSettings.cookies_text'] = record
