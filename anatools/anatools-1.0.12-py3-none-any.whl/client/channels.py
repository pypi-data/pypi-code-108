"""
Channels Functions
"""

def get_channels(self, organizationId=None, workspaceId=None, channelId=None):
    """Shows all channels available to the user. Can filter by organizationId, workspaceId, or channelId.
    
    Parameters
    ----------
    organizationId : str
        Filter channel list on what's available to the organization.
    workspaceId : str    
        Filter channel list on what's available to the workspace.
    channelId: str
        Filter channel list on the specific channelId.
    
    Returns
    -------
    list[dict]
        List of channels associated with user, workspace, organization or channelId.
    """
    if self.check_logout(): return
    channels = self.ana_api.getChannels(organizationId=organizationId, workspaceId=workspaceId, channelId=channelId)
    if channels:
        for channel in channels:
            self.channels[channel['channelId']] = channel['name']
        return channels
    else: return None       
                

def get_managed_channels(self, channelId=None, organizationId=None):
    """Get information for all managed channels that you own within your organization.
    
    Parameters
    ----------
    channelId : str
        Channel Id to filter.
    organizationId : str
        Organization ID. Defaults to current if not specified.
   
    Returns
    -------
    list[dict]
        channel data
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    return self.ana_api.getManagedChannels(organizationId=organizationId, channelId=channelId)


def create_managed_channel(self, name, organizationId=None, volumes=[], instance='p2.xlarge', timeout=120):
    """Create a managed channel for your organization.
    
    Parameters
    ----------
    name : str
        Channel name.
    organizationId : str
        Organization ID. Defaults to current if not specified.
    volumes : list[str]
        List of the data volume names to associate with this channel.
    instance: str
        AWS Instance type.
    timeout: int
        Timeout
   
    Returns
    -------
    list[dict]
        channel data
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    result = self.ana_api.createManagedChannel(organizationId=organizationId, name=name, volumes=volumes, instance=instance, timeout=timeout)
    self.get_channels()
    return result


def edit_managed_channel(self, channelId, name=None, volumes=None, instance=None, timeout=None, status=None):
    """Edit a managed channel for your organization.
    
    Parameters
    ----------
    channelId : str
        ChannelId ID of the channel to edit.
    name : name
        The new name to give the channel.
    volumes : list[str]
        Data volumes for the channel.
    instance: str
        Instance type to run the channel on.
    timeout: int
        Timeout for the channel.
    status: str
        The status of the channel.
    
    Returns
    -------
    bool
        If true, the channel was successfully edited.
    """
    if self.check_logout(): return
    if channelId is None: raise Exception('ChannelId must be specified.')
    result = self.ana_api.editManagedChannel(channelId=channelId, name=name, volumes=volumes, instance=instance, timeout=timeout, status=status)
    self.get_channels()
    return result


def add_channel_access(self, channelId, organizationId):
    """Add access to a channel for an organization.
    
    Parameters
    ----------
    channelId : str
        Id of channel to add access for.
    organizationId : str
        Organization ID. Defaults to current if not specified.
    
    Returns
    -------
    str
        Access status. 
    """
    if self.check_logout(): return
    if organizationId is None: raise Exception('OrganizationId must be specified.')
    return self.ana_api.addChannelOrganization(channelId=channelId, organizationId=organizationId)


def remove_channel_access(self, channelId, organizationId):
    """Remove access to a channel for an organization.
    
    Parameters
    ----------
    channelId : str
        Id of channel to remove access to.
    organizationId : str
        Organization ID. Defaults to current if not specified.
    
    Returns
    -------
    str
        Access status. 
    """
    if self.check_logout(): return
    if organizationId is None: raise Exception('OrganizationId must be specified.')
    return self.ana_api.removeChannelOrganization(channelId=channelId, organizationId=organizationId)


def deploy_managed_channel(self, channelId=None, image=None):
    """Deploy the Docker image of a channel.
    
    Parameters
    ----------
    channelId : str
        Channel ID that you are pushing the image to. If the channelId isn't specified, it will use the image name to lookup the channelId.
    image: str
        The Docker image name. This should match the channel name when running ana. If image is not specified, it will use the channel name for the channelId.

    Returns
    -------
    str
        deploymentId for current round of deployment or an error message if something went wrong
    """
    import docker, base64
    if self.check_logout(): return
    if channelId is None and image is None: print('The channelId or local image must be specified.'); return
    self.get_channels()
    
    # check if channel image is in Docker
    dockerclient = docker.from_env()
    if image and channelId:
        channel = image
        if channelId not in self.channels: 
            print(f'User does not have permissions to deploy to a channel with ID \"{channelId}\" on the Rendered.ai Platform.'); return
    elif image:   
        channel = image
        channels = self.get_managed_channels()
        filteredchannels = [channel for channel in channels if channel['name'] == image]
        if len(filteredchannels) == 1: channelId = filteredchannels[0]['channelId']
        elif len(filteredchannels) == 0: print(f'User does not have permissions to deploy to a channel named \"{image}\" on the Rendered.ai Platform.'); return
        else: print('User has access to multiple channels with name \"{image}\" on the Rendered.ai Platform, please specify channelId.'); return
    else:
        if channelId in self.channels: channel = self.channels[channelId]
        else: print(f'User does not have permissions to deploy to a channel with ID \"{channelId}\" on the Rendered.ai Platform.'); return
    try: channelimage = dockerclient.images.get(channel)
    except docker.errors.ImageNotFound: print(f'Could not find Docker image with name \"{channel}\".'); return
    except: raise Exception('Error connecting to Docker.')
    
    # get repository info
    print(f'Docker image \"{channel}\" will be deployed to the \"{self.channels[channelId]}\" channel.')
    print(f"Pushing Docker Image. This could take awhile...", end='', flush=True)
    dockerinfo = self.ana_api.deployManagedChannel(channelId, image)
    deploymentId = dockerinfo['deploymentId']
    reponame = dockerinfo['ecrEndpoint']
    encodedpass = dockerinfo['ecrPassword']
    if encodedpass:
        encodedbytes = encodedpass.encode('ascii')
        decodedbytes = base64.b64decode(encodedbytes)
        decodedpass = decodedbytes.decode('ascii').split(':')[-1]
    else: print('Failed to retrieve Docker credentials from Rendered.ai platform.'); return

    # tag and push image
    resp = channelimage.tag(reponame)
    if self.verbose:
        for line in dockerclient.images.push(reponame, auth_config={'username':'AWS', 'password':decodedpass}, stream=True, decode=True):
            if 'status' and 'progress' in line:
                    print(f"\x1b[1K\r {line['status']} \"{channel}\" to \"{self.channels[channelId]}\" {line['progress']}",end='')
    else:
        for line in dockerclient.images.push(reponame, auth_config={'username':'AWS', 'password':decodedpass}, stream=True, decode=True):
            if 'status' and 'progressDetail' in line:
                if 'current' and 'total' in line['progressDetail']:
                    progressDetail = line['progressDetail']
                    print(f"\x1b[1K\r[{round((progressDetail['current']/progressDetail['total']) * 100)}%] {line['status']} \"{channel}\" to \"{self.channels[channelId]}\" ",end='')
    print("\nComplete!", flush=True)
    
    # cleanup docker and update channels
    resp = dockerclient.images.remove(reponame)
    del dockerclient
    if self.check_logout(): return
    self.get_channels()
    return deploymentId


def get_deployment_status(self, deploymentId, stream=False):
    """Retrieves status for a channel's deployment.
    
    Parameters
    ----------
    deploymentId: str
        The deploymentId to retrieve status for
    stream: bool
        Flag to print information to the terminal so the user can avoid constant polling to retrieve status.

    Returns
    -------
    list[dict]
        Deployment status. 
    """
    import time
    if self.check_logout(): return
    if deploymentId is None: raise Exception('DeploymentId must be specified.')
    if stream:
        data = self.ana_api.getChannelDeployment(deploymentId=deploymentId)
        print(f"Step: {data['status']['step']}\nState: {data['status']['state']}\nMessage: {data['status']['message']}", end="\033[F"*2, flush=True)
        while (data['status']['state'] not in ['Channel Deployment Complete','Channel Deployment Failed']):
            time.sleep(10)
            print(f"Step: {data['status']['step']}\nState: {data['status']['state']}\nMessage: {data['status']['message']}", end="\033[F"*2, flush=True)
            data = self.ana_api.getChannelDeployment(deploymentId=deploymentId)
        print(f"Step: {data['status']['step']}\nState: {data['status']['state']}\nMessage: {data['status']['message']}", flush=True)
    else: return self.ana_api.getChannelDeployment(deploymentId=deploymentId)
