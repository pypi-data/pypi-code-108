"""
Volumes Functions
"""

def get_volumes(self, organizationId=None, volumeId=None):
    """Retrieves the managed volumes for an organization.
    
    Parameters
    ----------
    organizationId : str
        The ID of the organization that the managed volume belongs to.
    volumeId : str
        The ID of a specific Volume.
    
    Returns
    -------
    list[dict]
        Volume Info
    """
    if self.check_logout(): return
    return self.ana_api.getVolumes(organizationId=organizationId, volumeId=volumeId)


def get_managed_volumes(self, organizationId=None, volumeId=None):
    """Retrieves the managed volumes for an organization.
    
    Parameters
    ----------
    organizationId : str
        The ID of the organization that the managed volume belongs to.
    volumeId : str
        The ID of a specific Volume.
    
    Returns
    -------
    list[dict]
        Volume Info
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    return self.ana_api.getManagedVolumes(organizationId=organizationId, volumeId=volumeId)


def create_managed_volume(self, name, organizationId=None):
    """Creates a new volume with the specified name in the organization.
    
    Parameters
    ----------
    name : str
        The name of the new volume. Note: this name needs to be unique per organization.
    organizationId : str
        The ID of the organization that the managed volume will belong to.
    
    Returns
    -------
    str
        volumeId
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    if name is None: raise Exception("Name must be specified.")
    return self.ana_api.createManagedVolume(organizationId=organizationId,name=name)

    
def delete_managed_volume(self, volumeId):
    """Removes the volumeId from the organization. Note that this will delete any remote data in the volume 
    and channels that rely on this volume will need to be updated.
    
    Parameters
    ----------
    volumeId : str
        The ID of a specific Volume.
    
    Returns
    -------
    str
        Status
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    return self.ana_api.deleteManagedVolume(volumeId=volumeId)


def edit_managed_volume(self, volumeId, name):
    """Edits the name of a volume.
    
    Parameters
    ----------
    volumeId: str
        The volumeId that will be updated.
    name : str
        The new name of the new volume. Note: this name needs to be unique per organization.
    
    Returns
    -------
    str
        Status
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    if name is None: raise Exception("Name must be specified.")
    return self.ana_api.editManagedVolume(volumeId=volumeId,name=name)


def add_volume_access(self, volumeId, organizationId):
    """Add access to a volume for an organization.
    
    Parameters
    ----------
    volumeId : str
        VolumeId to add access for.
    organizationId : str
        Organization ID to add access
    
    Returns
    -------
    str
        Status
    """
    if self.check_logout(): return
    if organizationId is None: raise Exception('OrganizationId must be specified.')
    if volumeId is None: raise Exception('VolumeId must be specified.')
    return self.ana_api.addVolumeOrganization(volumeId=volumeId, organizationId=organizationId)


def remove_volume_access(self, volumeId, organizationId):
    """Remove access to a volume for an organization.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to remove access to.
    organizationId : str
        Organization ID to remove access.
    
    Returns
    -------
    str
       Status
    """
    if self.check_logout(): return
    if organizationId is None: raise Exception('OrganizationId must be specified.')
    if volumeId is None: raise Exception('VolumeId must be specified.')
    return self.ana_api.removeVolumeOrganization(volumeId=volumeId, organizationId=organizationId)


def get_volume_data(self, volumeId, files=[]):
    """Retrieves information about data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to remove access to.
    files : str
        The specific files to retrieve information about from the volume, if you wish to retrieve all then leave the list empty.
   
    Returns
    -------
    str
       Status
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    response = self.ana_api.getVolumeData(volumeId=volumeId, keys=files)
    result = []
    for fileinfo in response:
        result.append({
            'key':          fileinfo['key'],
            'size':         fileinfo['size'],
            'lastUpdated':  fileinfo['updatedAt'],
            'hash':         fileinfo['hash']
        })
    return result


def download_volume_data(self, volumeId, files=[], localDir=None):
    """Download data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to remove access to.
    files : str
        The specific files to retrieve from the volume, if you wish to retrieve all then leave the list empty.
    localDir : str
        The location of the local directory to download the files to. If not specified, this will download the files to the current directory.
    
    Returns
    -------
    str
       Status
    """
    import requests, traceback, os
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    if localDir is None: localDir = os.getcwd()
    response = self.ana_api.getVolumeData(volumeId=volumeId, keys=files)
    for fileinfo in response:
        try:
            downloadresponse = requests.get(url=fileinfo['url'])
            filename = os.path.join(localDir, fileinfo['key'])
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            with open(filename, 'wb') as outfile:
                outfile.write(downloadresponse.content)
        except:
            traceback.print_exc()
            print(f'Failed to download {fileinfo["key"]}.')
    return


def upload_volume_data(self, volumeId, files=[], localDir=None):
    """Upload data to a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to remove access to.
    files : list[str]
        The specific files to push to the volume from the localDir. If you wish to push all then leave the list empty.
    localDir : str
        The location of the local directory to upload the files from. If not specified, this will try to upload the files from the current directory.
    
    Returns
    -------
    str
       Status
    """
    import requests, traceback, time, os
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    if localDir is None: localDir = os.getcwd()
    elif not localDir.endswith('/'): localDir+='/'
    elif not os.path.exists(localDir): raise Exception(f"Could not find directory {localDir}.")
    uploadfiles = []
    if len(files):
        for file in files:
            upfile = os.path.join(localDir, file)
            if os.path.exists(upfile):
                uploadfiles.append(file)
            else: print(f"Could not find {upfile}.")
    else:
        for root, dirs, files in os.walk(localDir):
            for upfile in files:
                uploadfiles.append(os.path.join(root,upfile).replace(localDir,''))
    faileduploads = []
    if not self.verbose: print(f"Uploading volume data. This could take awhile...", end='\x1b[1K\r', flush=True)
    for i in range(len(uploadfiles)):
        self.refresh_token()
        fileinfo = self.ana_api.putVolumeData(volumeId=volumeId, keys=[uploadfiles[i]])[0]
        try:
            filepath = os.path.join(localDir, uploadfiles[i])
            fileSize = os.path.getsize(filepath)
            
            if self.verbose: print(f"\x1b[1K\r[{i+1} / {len(uploadfiles)}]  Uploading {uploadfiles[i]}...  [fileSize: {round(fileSize/1024, 2)}KB]", end='', flush=True)
            else: 
                print(f"\x1b[1K\r[{(round((i + 1)/len(uploadfiles) * 100))}%] Uploading: {uploadfiles[i]}... ",end='')
            with open(filepath, 'rb') as filebytes:
                files = {'file': filebytes}
                data = {
                    "key":                  fileinfo['fields']['key'],
                    "bucket":               fileinfo['fields']['bucket'],
                    "X-Amz-Algorithm":      fileinfo['fields']['algorithm'],
                    "X-Amz-Credential":     fileinfo['fields']['credential'],
                    "X-Amz-Date":           fileinfo['fields']['date'],
                    "X-Amz-Security-Token": fileinfo['fields']['token'],
                    "Policy":               fileinfo['fields']['policy'],
                    "X-Amz-Signature":      fileinfo['fields']['signature'],
                }
                response = requests.post(fileinfo['url'], data=data, files=files)
                if response.status_code != 204:
                    faileduploads.append(uploadfiles[i])
                    if self.verbose: print(end=f"\x1b[1K\rFailure {uploadfiles[i]}", flush=True)
                else:
                    if self.verbose: print(end=f"\x1b[1K\r{uploadfiles[i]} completed", flush=True)
        except:
            traceback.print_exc() 
            print(f'Failed to upload {uploadfiles[i]}')
    if self.verbose: print("\x1b[1K\rUploading files completed.", end='\n')
    else: print('\x1b[1K\rCompleted.', end='\n')
    if len(faileduploads): print('The following files failed to upload:',faileduploads)
            

def delete_volume_data(self, volumeId, files=[]):
    """Delete data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to remove access to.
    files : str
        The specific files to delete from the volume, if you wish to delete all then leave the list empty.
    
    Returns
    -------
    str
       Status
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    return self.ana_api.deleteVolumeData(volumeId=volumeId, keys=files)
