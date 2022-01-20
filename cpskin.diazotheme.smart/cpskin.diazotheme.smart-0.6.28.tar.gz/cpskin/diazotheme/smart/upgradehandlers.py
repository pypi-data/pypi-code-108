# -*- coding: utf-8 -*-

from plone import api
import logging

from cpskin.theme.upgradehandlers import upgrade_to_less as base_less_upgrade

logger = logging.getLogger('cpskin.theme')


def upgrade_to_less(context):
    portal = api.portal.get()
    if not 'portal_less' in portal.objectIds():
        base_less_upgrade(context)
    context.runImportStepFromProfile(
        'profile-cpskin.diazotheme.smart:default',
        'lessregistry'
    )
    logger.info('LESS files installed and configurations done !')


def upgrade_portal_less(context):
    context.runImportStepFromProfile(
        'profile-cpskin.diazotheme.smart:default',
        'lessregistry'
    )
    logger.info('LESS registry refreshed !')
