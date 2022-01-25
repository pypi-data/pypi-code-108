# -*- coding: utf-8 -*-
""" Zope 2 permissions
"""

from AccessControl.Permission import addPermission


ManageWorkflowPolicies = 'CMFPlacefulWorkflow: Manage workflow policies'
addPermission(ManageWorkflowPolicies, ('Manager', 'Site Administrator'))
