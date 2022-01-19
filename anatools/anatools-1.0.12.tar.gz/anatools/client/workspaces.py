"""
Workspace Functions
"""
    
def get_workspace(self):
    """Get Workspace ID of current workspace. 
    
    Returns
    -------
    str
        Workspace ID of current workspace.
    """
    if self.check_logout(): return
    return self.workspace


def set_workspace(self, workspaceId):
    """Set the workspace to the one you wish to work in.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID for the workspace you wish to work in.
    """
    if self.check_logout(): return
    if workspaceId is None: raise Exception('WorkspaceId must be specified.')
    workspaceSet = False
    self.workspaces = self.ana_api.getWorkspaces()
    for workspace in self.workspaces:
        if workspaceId == workspace['workspaceId']:
            self.workspace = workspace['workspaceId']
            self.organization = workspace['organizationId']
            workspaceSet = True
            break
    if not workspaceSet: raise Exception('Could not find workspace specified.')
    print(f'Organization set to {self.organization}.')
    print(f'Workspace set to {self.workspace}.')
    return


def get_workspaces(self, organizationId=None, workspaceId=None):
    """Shows list of workspaces with id, name, and owner data.
    
    Parameters
    ----------
    organizationId : str
        Organization ID to filter on. Optional
    workspaceId : str
        Workspace ID to filter on. Optional

    Returns
    -------
    list[dict]
        Workspace data for all workspaces for a user.
    """  
    if self.check_logout(): return
    try:
        workspaces = self.ana_api.getWorkspaces(organizationId, workspaceId)
        return workspaces
    except:
        return 


def create_workspace(self, name, channelIds=[]):
    """Create a new workspace with specific channels.
    
    Parameters
    ----------
    name : str    
        New workspace name.
    channels : list[str]
        List of channel names to add to workspace. 
    
    Returns
    -------
    str
        Workspace ID if creation was successful. Otherwise returns message.
    """    
    if self.check_logout(): return
    if name is None: raise ValueError("Name must be provided")
    return self.ana_api.createWorkspace(organizationId=self.organization, name=name, channelIds = channelIds)


def delete_workspace(self, workspaceId=None, prompt=True):
    """Delete an existing workspace. 
    
    Parameters
    ----------
    workspaceId : str    
        Workspace ID for workspace to get deleted. Deletes current workspace if not specified. 
    prompt: bool
        Set to True if avoiding prompts for deleting workspace.
    
    Returns
    -------
    str
        Success or failure message if workspace was sucessfully removed.
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace 
    if prompt:
        response = input('This will remove any configurations, graphs and datasets associated with this workspace.\nAre you certain you want to delete this workspace? (y/n)  ')
        if response not in ['Y', 'y', 'Yes', 'yes']: return
    return self.ana_api.deleteWorkspace(workspaceId=workspaceId)


def edit_workspace(self, name=None, channels=None, workspaceId=None):
    """Edit workspace information. Provided channels list will result in the workspace having those channels. If channels is not provided, then no change will occur. 
    
    Parameters
    ----------
    name : str    
        New name to replace old one.
    channels: list[str]
        Names of channels that the workspace will have access to.
    workspaceId : str    
        Workspace ID for workspace to update.
    
    Returns
    -------
    str
        Success or failure message if workspace was sucessfully updated.
    """  
    if self.check_logout(): return
    if name is None and channels is None: return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editWorkspace(workspaceId=workspaceId, name=name, channelIds=channels)


def get_workspace_guests(self, workspaceId=None):
    """Get guests of a workspace. Uses default workspace if not specified.
    
    Parameters
    ----------
    workspaceId : str
        Workspace Id. Optional.
    
    Returns
    -------
    list[dict]
        Information about guests of an workspace.
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getMembers(workspaceId=workspaceId)


def add_workspace_guest(self, email, workspaceId=None):
    """Add a guest to an existing workspace.
    
    Parameters
    ----------
    email: str
        Email of guest to add.
    workspaceId : str    
        Workspace ID to add a guest to. Uses current if not specified.
    
    Returns
    -------
    str
        Response status if guest got added to workspace succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.addMember(email=email, role=None, organizationId=None, workspaceId=workspaceId)


def remove_workspace_guest(self, email, workspaceId=None):
    """Remove a guest from an existing workspace.
    
    Parameters
    ----------
    email : str
        Guest email to remove.
    workspaceId : str    
        Workspace ID to remove guest from. Removes from current workspace if not specified. 
    
    Returns
    -------
    str
        Response status if guest got removed from workspace succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.removeMember(email=email, organizationId=None, workspaceId=workspaceId)


def get_workspace_limits(self, setting=None, workspaceId=None):
    """Get information about Workspace limits and settings.

    Parameters
    ----------
    setting : str
        Setting name.
    workspaceId : str
        Workspace ID. Defaults to current if not specified.
    
    Returns
    -------
    list[dict]
        Workspace limit information.
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getWorkspaceLimits(workspaceId=workspaceId, setting=setting)


def set_workspace_limit(self, setting, limit, workspaceId=None):
    """Set a limit for a workspace.

    Parameters
    ----------
    setting : str
        Setting name.
    limit : int
        Limit to set at.
    workspaceId : str
        Workspace ID. Defaults to current if not specified.
    
    Returns
    -------
    list[dict]
        Workspace limit information.
    """
    if self.check_logout(): return
    if setting is None: raise("Setting must be provided.")
    if limit is None: raise("Limit must be provided.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.setWorkspaceLimit(workspaceId=workspaceId, setting=setting, limit=limit)

