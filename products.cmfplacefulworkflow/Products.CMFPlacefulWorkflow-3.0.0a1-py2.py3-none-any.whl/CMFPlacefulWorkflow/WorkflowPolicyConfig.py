# -*- coding: utf-8 -*-
# CMFPlacefulWorkflow
# Copyright (C)2005 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see th e file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Workflow Policy config
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from os.path import join as path_join
from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow.global_symbols import Log
from Products.CMFPlacefulWorkflow.permissions import ManageWorkflowPolicies
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id  # noqa: E501
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import six


manage_addWorkflowPolicyConfigForm = PageTemplateFile(
    path_join('www', 'add_workflow_policy_config_form'), globals())


def manage_addWorkflowPolicyConfig(self, REQUEST=None):
    ' add a Workflow Policy Configuratio into the system '
    workflow_policy_in = ''
    workflow_policy_below = ''
    if REQUEST:
        workflow_policy_in = REQUEST.get('workflow_policy_in', '')
        workflow_policy_below = REQUEST.get('workflow_policy_below', '')

    # create new workflow policy config
    i = WorkflowPolicyConfig(workflow_policy_in, workflow_policy_below)
    self._setObject(WorkflowPolicyConfig_id, i)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url() + '/manage_main')


class WorkflowPolicyConfig(SimpleItem):
    """Workflow policy configuration"""
    meta_type = 'Workflow Policy Configuration'
    index_html = None
    security = ClassSecurityInfo()

    manage_main = PageTemplateFile(path_join('www', 'manage_workflow_policy_config'),
                                   globals(),
                                   __name__='manage_main')

    manage_options = ((
        {'icon': '', 'label': 'Edit', 'action': 'manage_main', },
    ) + SimpleItem.manage_options
    )

    def __init__(self, workflow_policy_in='', workflow_policy_below=''):
        """Initialize a new MailHost instance """
        self.id = WorkflowPolicyConfig_id
        self.title = "Workflow policy configuration"
        self.setPolicyIn(workflow_policy_in)
        self.setPolicyBelow(workflow_policy_below)

    security.declareProtected(ManageWorkflowPolicies, 'manage_makeChanges')

    def manage_makeChanges(self, workflow_policy_in, workflow_policy_below):
        """ Store the policies """
        self.setPolicyIn(workflow_policy_in)
        self.setPolicyBelow(workflow_policy_below)

    security.declareProtected(ManageWorkflowPolicies, 'getPolicyInId')

    def getPolicyInId(self):
        return self.workflow_policy_in

    security.declareProtected(ManageWorkflowPolicies, 'getPolicyBelowId')

    def getPolicyBelowId(self):
        return self.workflow_policy_below

    security.declareProtected(ManageWorkflowPolicies, 'getPolicyIn')

    def getPolicyIn(self):
        pwtool = getToolByName(self, 'portal_placeful_workflow')
        return pwtool.getWorkflowPolicyById(self.getPolicyInId())

    security.declareProtected(ManageWorkflowPolicies, 'getPolicyBelow')

    def getPolicyBelow(self):
        pwtool = getToolByName(self, 'portal_placeful_workflow')
        return pwtool.getWorkflowPolicyById(self.getPolicyBelowId())

    security.declareProtected(ManageWorkflowPolicies, 'setPolicyIn')

    def setPolicyIn(self, policy, update_security=False):
        if not isinstance(policy, six.string_types):
            raise ValueError("Policy must be a six.string_types")
        self.workflow_policy_in = policy
        if update_security:
            wtool = getToolByName(self, 'portal_workflow')
            # wtool.updateRoleMappings(context)    # passing context is not possible :(
            #
            # Since WorkflowTool.updateRoleMappings()  from the line above supports
            # only sitewide updates code from updateRoleMappings() was copied below
            # to enable context passing to
            # wftool._recursiveUpdateRoleMappings()
            wfs = {}
            for id in wtool.objectIds():
                wf = wtool.getWorkflowById(id)
                if hasattr(aq_base(wf), 'updateRoleMappingsFor'):
                    wfs[id] = wf
            context = aq_parent(aq_inner(self))
            wtool._recursiveUpdateRoleMappings(context, wfs)

    security.declareProtected(ManageWorkflowPolicies, 'setPolicyBelow')

    def setPolicyBelow(self, policy, update_security=False):
        if not isinstance(policy, six.string_types):
            raise ValueError("Policy must be a string")
        self.workflow_policy_below = policy
        if update_security:
            wtool = getToolByName(self, 'portal_workflow')
            wfs = {}
            for id in wtool.objectIds():
                wf = wtool.getWorkflowById(id)
                if hasattr(aq_base(wf), 'updateRoleMappingsFor'):
                    wfs[id] = wf
            context = aq_parent(aq_inner(self))
            wtool._recursiveUpdateRoleMappings(context, wfs)

    security.declareProtected(ManageWorkflowPolicies, 'getPlacefulChainFor')

    def getPlacefulChainFor(self, portal_type, start_here=False):
        """Get the chain for the given portal_type.

        Returns None if no placeful chain is found.
        Does _not_ acquire from parent configurations.

        Usecases:
        If the policy config is in the object that request the chain we cannot
        take the 'below' policy.
        In other case we test the 'below' policy first and, if there's no chain
        found, the 'in' policy.
        """
        workflow_tool = getToolByName(self, 'portal_placeful_workflow')
        Log.debug('below policy id %s', self.getPolicyBelowId())
        Log.debug('in policy id %s', self.getPolicyInId())

        chain = None
        policy = None
        if not start_here:
            policy = workflow_tool.getWorkflowPolicyById(
                self.getPolicyBelowId())
            if policy is not None:
                chain = policy.getChainFor(portal_type)

        policy = workflow_tool.getWorkflowPolicyById(self.getPolicyInId())

        if policy is not None:
            Log.debug("policy %s %s", repr(policy), policy is not None)
        if chain is None and policy is not None:
            chain = policy.getChainFor(portal_type)
            Log.debug("portal_type and chain %s %s", portal_type, chain)

        return chain


InitializeClass(WorkflowPolicyConfig)
