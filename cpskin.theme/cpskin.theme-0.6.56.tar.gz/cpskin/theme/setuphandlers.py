# -*- coding: utf-8 -*-

from plone.resource.interfaces import IResourceDirectory
from six import StringIO
from zope.component import getUtility
import logging

logger = logging.getLogger('cpskin.theme')

CUSTOM_FOLDER_NAME = 'cpskin'


def installTheme(context):
    if context.readDataFile('cpskin.theme-default.txt') is None:
        return
    addCustomLessFiles()


def addCustomLessFiles():
    added = False
    portal_resources = getUtility(IResourceDirectory, name='persistent')
    if CUSTOM_FOLDER_NAME not in portal_resources:
        portal_resources.makeDirectory(CUSTOM_FOLDER_NAME)
    folder = portal_resources[CUSTOM_FOLDER_NAME]
    if not 'variables.less' in folder:
        folder.writeFile(
            'variables.less',
            StringIO('/*\nPut your custom LESS variables here.\n*/\n\n'),
        )
        logger.info('Custom variables LESS files added to portal_resources')
    if not 'styles.less' in folder:
        folder.writeFile(
            'styles.less',
            StringIO('/*\nPut your custom LESS styles here.\n*/\n\n'),
        )
        logger.info('Custom styles LESS files added to portal_resources')
        added = True
    return added


def uninstallTheme(context):
    if context.readDataFile('cpskin.theme-uninstall.txt') is None:
        return
    removeCustomLessFiles()


def removeCustomLessFiles():
    portal_resources = getUtility(IResourceDirectory, name='persistent')
    if CUSTOM_FOLDER_NAME in portal_resources:
        del portal_resources[CUSTOM_FOLDER_NAME]
        logger.info('Custom LESS files removed from portal_resources')
