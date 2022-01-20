# -*- coding: utf-8 -*-

from plone import api
import logging

from cpskin.theme.upgradehandlers import upgrade_to_less as base_less_upgrade

logger = logging.getLogger('cpskin.diazotheme.dream')


def upgrade_to_less(context):
    portal = api.portal.get()
    if not 'portal_less' in portal.objectIds():
        base_less_upgrade(context)
    context.runImportStepFromProfile(
        'profile-cpskin.diazotheme.dream:default',
        'lessregistry'
    )
    logger.info('LESS files installed and configurations done !')
