"""
GAN Functions
"""

def get_gan_models(self, modelId=None):
    """Retrieve information about GAN models that exist on the platform.
    
    Parameters
    ----------
    modelId : str
        Model ID to retrieve information for. 
    
    Returns
    -------
    list[dict]
        GAN Model information.
    """
    if self.check_logout(): return
    return self.ana_api.getGANModels(modelId=modelId)
    

def get_gan_dataset(self, datasetId, workspaceId=None):
    """Retrieve information about GAN dataset jobs.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to retrieve information for. 
    workspaceId : str
        Workspace ID where the dataset exists.
    
    Returns
    -------
    list[dict]
        Information about the GAN Dataset.
    """
    if self.check_logout(): return
    if datasetId is None: raise ValueError("DatasetId must be provided.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getGANDataset(workspaceId=workspaceId, datasetId=datasetId)


def create_gan_dataset(self, modelId, datasetId, workspaceId=None):
    """Create a new GAN dataset based off an existing dataset. This will start a new job.
    
    Parameters
    ----------
    modelId : str
        Model ID to use for the GAN.
    datasetId : str
        Dataset ID to input into the GAN. 
    workspaceId : str
        Workspace ID where the dataset exists.
    
    Returns
    -------
    str
        The datsetId for the GAN Dataset job.
    """
    if self.check_logout(): return
    if modelId is None: raise ValueError("ModelId must be provided.")
    if datasetId is None: raise ValueError("DatasetId must be provided.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createGANDataset(workspaceId=workspaceId, datasetId=datasetId, modelId=modelId)


def delete_gan_dataset(self, datasetId, workspaceId=None):
    """Deletes a GAN dataset job.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID for the GAN dataset. 
    workspaceId : str
        Workspace ID where the dataset exists.
    
    Returns
    -------
    bool
        Returns true if the GAN dataset was successfully deleted.
    """
    if self.check_logout(): return
    if datasetId is None: raise ValueError("DatasetId must be provided.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteGANDataset(workspaceId=workspaceId, datasetId=datasetId)

