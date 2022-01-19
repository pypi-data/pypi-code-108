"""
Organization Functions
"""

def get_organization(self):
    """Get organization id of current organization. 
    
    Returns
    -------
    str
        Organization ID of current workspace.
    """
    if self.check_logout(): return
    return self.organization


def set_organization(self, organizationId, workspaceId=None):
    """Set the organization (and optionally a workspace) to the one you wish to work in.
    
    Parameters
    ----------
    organizationId : str
        Organization ID for the organization you wish to work in.
    workspaceId : str
        Workspace ID for the workspace you wish to work in. Uses default workspace if this is not set.
    """
    if self.check_logout(): return
    if organizationId is None: raise Exception('WorkspaceId must be specified.')
    workspaceSet = False
    self.workspaces = self.ana_api.getWorkspaces()
    for workspace in self.workspaces:
        if organizationId == workspace['organizationId']:
            if workspaceId is None or workspaceId == workspace['workspaceId']:
                self.workspace = workspace['workspaceId']
                self.organization = workspace['organizationId']
                workspaceSet = True
                break
    if not workspaceSet: raise Exception('Could not find organization or workspace specified.')
    print(f'Organization set to {self.organization}.')
    print(f'Workspace set to {self.workspace}.')
    return


def get_organizations(self):
    """Shows the organizations the user belongs to and the user's role in that organization.
    
    Returns
    -------
    list[dict]
        Information about the organizations you belong to. 
    """  
    if self.check_logout(): return
    try:
        orgs = self.ana_api.getOrganizations()
        return orgs
    except:
        return 


def edit_organization(self, name, organizationId=None):
    """Update the organization name. Uses current organization if no organizationId provided.
    
    Parameters
    ----------
    name : str
        Name to update organization to.
    organizationId : str
        Organization Id to update.
    
    Returns
    -------
    bool
        True if organization was edited successfully, False otherwise.
    """  
    if self.check_logout(): return
    if name is None: return
    if organizationId is None: organizationId = self.organization
    return self.ana_api.editOrganization(organizationId, name)


def get_organization_members(self, organizationId=None):
    """Get users of an organization optionally filtered on workspace.
    
    Parameters
    ----------
    organizationId : str
        Organization ID. Defaults to current if not specified.
    
    Returns
    -------
    list[dict]
        Information about users of an organization.
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    return self.ana_api.getMembers(organizationId=organizationId, workspaceId=None)


def add_organization_member(self, email, role, organizationId=None):
    """Add a user to an existing organization.
    
    Parameters
    ----------
    email: str
        Email of user to add.
    role : str
        Role for user. 
    organizationId : str
        Organization ID to add members too. Uses current if not specified.
    
    Returns
    -------
    str
        Response status if user got added to workspace succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if role is None: raise ValueError("Role must be provided.")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.addMember(email=email, role=role, organizationId=organizationId, workspaceId=None)


def remove_organization_member(self, email, organizationId=None):
    """Remove a member from an existing organization.
    
    Parameters
    ----------
    email : str
        Member email to remove.
    organizationId: str
        Organization ID to remove member from. Removes from current organization if not specified.
    
    Returns
    -------
    str
        Response status if member got removed from organization succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.removeMember(email=email, organizationId=organizationId, workspaceId=None)


def edit_organization_member(self, email, role, organizationId=None):
    """Edit a member's role. 
    
    Parameters
    ----------
    email : str
        Member email to edit.
    role: str
        Role to assign. 
    organizationId: str
        Organization ID to remove member from. Edits member in current organization if not specified.
    
    Returns
    -------
    str
        Response if member got edited succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if role is None: raise ValueError("Role must be provided.")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.editMember(email=email, role=role, organizationId=organizationId)


def get_organization_limits(self, organizationId=None, setting=None):
    """Get information about Organization limits and setting.
    
    Parameters
    ----------
    organizationId : str
        Organization ID. Defaults to current if not specified.
    setting : str
        Setting name.
    
    Returns
    -------
    list[dict]
        Organization limit information.
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    return self.ana_api.getOrganizationLimits(organizationId=organizationId, setting=setting)


def set_organization_limit(self, setting, limit, organizationId=None):
    """Set Organization limit for a setting.
    
    Parameters
    ----------
    setting : str
        Setting name.
    limit: int
        Limit for the setting.
    organizationId : str
        Organization ID. Defaults to current if not specified.
    
    Returns
    -------
    list[dict]
        Organization limit information.
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    return self.ana_api.setOrganizationLimit(organizationId=organizationId, setting=setting, limit=limit)


def get_organization_usage(self, organizationId=None, year=None, month=None, workspaceId=None, member=None):
    """Get organization usage optionally filtered on workspace or a user. 
    
    Parameters
    ----------
    organizationId : str
        Organization ID. Defaults to current if not specified.
    year: str
        Usage year to filter on.
    month: str
        Usage month to filter on.
    workspaceId : str
        Workspace Id. Optional.
    member: str
        User email. Optional.
    
    Returns
    -------
    list[dict]
        Organization usage by channels, instanceType, and time as integer.
    """
    from datetime import datetime
    if self.check_logout(): return
    if year is None: year = str(datetime.now().year)
    if month is None: month = str(datetime.now().month)
    if organizationId is None: organizationId = self.organization
    return self.ana_api.getOrganizationUsage(organizationId=organizationId, year=year, month=month, workspaceId=workspaceId, member=member)

