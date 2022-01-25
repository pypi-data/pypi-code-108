# -*- coding: utf-8 -*-
# Copyright (C) 2008 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow.global_symbols import \
    placeful_prefs_configlet
from Products.CMFPlacefulWorkflow.interfaces import IPlacefulMarker
from Products.CMFPlacefulWorkflow.interfaces import IPlacefulWorkflowTool
from zope.component import getSiteManager
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import logging


logger = logging.getLogger('Products.CMFPlacefulWorkflow')


def installMarker(context):
    """
    Apply a marker interface to the workflow tool to indicate that the
    product is installed.
    """
    wf = getToolByName(context, 'portal_workflow', None)
    if wf is not None:
        alsoProvides(wf, IPlacefulMarker)
        logger.info('Added placeful marker to portal_workflow.')


def uninstall(context):
    # Note: this function is registered as a pre_handler instead of a
    # post_handler, because otherwise toolset.xml has already been applied,
    # which removes the portal_placeful_workflow tool.
    portal = getToolByName(context, 'portal_url').getPortalObject()
    tool = getattr(portal, 'portal_placeful_workflow', None)
    if tool is not None:
        getSiteManager(portal).unregisterUtility(
            tool,
            IPlacefulWorkflowTool)
        logger.info('Unregistered portal_placeful_workflow')
    # uninstall configlets
    try:
        cptool = getToolByName(portal, 'portal_controlpanel')
        cptool.unregisterConfiglet(placeful_prefs_configlet['id'])
        logger.info('Removing CMFPlacefulWorkflow Configlet')
    except:
        logger.info('Failed to remove CMFPlacefulWorkflow Configlet')

    wf_tool = getToolByName(portal, 'portal_workflow')
    if IPlacefulMarker.providedBy(wf_tool):
        noLongerProvides(wf_tool, IPlacefulMarker)
        logger.info('Removed placeful marker from portal_workflow.')
    # Mark our base profile as uninstalled, because:
    # 1. It is good practice.
    # 2. Otherwise when the user installs CMFPlacefulWorkflow again,
    #    portal_setup will not apply our base profile.
    portal_setup = getToolByName(portal, 'portal_setup')
    portal_setup.unsetLastVersionForProfile(
        'Products.CMFPlacefulWorkflow:base')
