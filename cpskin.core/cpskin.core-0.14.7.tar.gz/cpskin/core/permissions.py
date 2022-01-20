# -*- coding: utf-8 -*-
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles


security = ModuleSecurityInfo('cpskin.core.permissions')

security.declarePublic('CPSkinSiteAdministrator')
CPSkinSiteAdministrator = 'CPSkin: Site administrator'
setDefaultRoles(CPSkinSiteAdministrator, ('Site Administrator',
                                          'Manager'))

security.declarePublic('CPSkinEditKeywords')
CPSkinEditKeywords = 'CPSkin: Edit keywords'
setDefaultRoles(CPSkinEditKeywords, ('Site Administrator',
                                     'Manager',
                                     'Portlets Manager'))
