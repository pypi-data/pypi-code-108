"""
Annotations Functions
"""

def get_annotation_formats(self):
    """Retrieves the annotation formats supported by the Platform.
    
    Returns
    -------
    str
        The annotation formats supported by the Platform.
    """
    if self.check_logout(): return
    return self.ana_api.getAnnotationFormats()


def get_annotation_maps(self, channelId):
    """Retrieves the map files that are supported by the channel.
    
    Parameters
    ----------
    channelId : str
        Channel ID to retrieve maps for.
    
    Returns
    -------
    str
        The annotation maps supported by the channel.
    """
    if self.check_logout(): return
    if channelId is None: raise ValueError('ChannelId must be specified.')
    return self.ana_api.getAnnotationMaps(channelId)


def get_annotations(self, datasetId=None, annotationId=None, workspaceId=None):
    """Retrieve information about existing annotations generated for a dataset. Querying requires both datasetId and annotationId.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to generate annotations for.
    annotationId : str
        Annotation ID for a specific annotations job.
    workspaceId: str
        Workspace ID where the annotations exist. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    list[dict]
        Annotation information.
    """
    if self.check_logout(): return
    if annotationId is None and datasetId is None: raise ValueError('datasetId and annotationId must be specified.')
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getAnnotations(workspaceId=workspaceId, datasetId=datasetId, annotationId=annotationId)
    

def create_annotation(self, datasetId, format, map, workspaceId=None):
    """Generates annotations for an existing dataset. 
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to generate annotation for.
    format : str
        Annotation format. Call get_annotation_formats() to find supported formats.
    map: str
        The map file used for annotations. Call get_annotation_maps() to find supported maps.
    workspaceId: str
        Workspace ID of the dataset to generate annotation for. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        The annotationsId for the annotation job.
    """
    if self.check_logout(): return
    if datasetId is None: raise ValueError("DatasetId must be defined.")
    if format is None: raise ValueError("Format must be defined.")
    if map is None: raise ValueError("Map must be defined.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createAnnotation(workspaceId=workspaceId, datasetId=datasetId, format=format, map=map)
    

def download_annotation(self, datasetId, annotationId, workspaceId=None):
    """Downloads annotations archive.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to download image annotation for.
    annotationId : str
        Id of previously generated image annotation. 
    workspaceId: str
        Workspace ID of the dataset to generate annotation for. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        The name of the archive file that got downloaded.
    """
    import requests
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    url = self.ana_api.downloadAnnotation(workspaceId=workspaceId, datasetId=datasetId, annotationId=annotationId)
    fname = url.split('?')[0].split('/')[-1]
    with requests.get(url, stream=True) as downloadresponse:
        with open(fname, 'wb') as outfile:
            downloadresponse.raise_for_status()
            outfile.write(downloadresponse.content)
            with open(fname, 'wb') as f:
                for chunk in downloadresponse.iter_content(chunk_size=8192):
                    f.write(chunk)
    return fname


def delete_annotation(self, annotationId, workspaceId=None):
    """Delete a dataset annotation.
    
    Parameters
    ----------
    annotationId : str
        AnnoationId of the annotation job.
    workspaceId: str
        Workspace ID of the dataset to generate annotation for. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        If true, successfully deleted the annotation.
    """
    if self.check_logout(): return
    if annotationId is None: raise ValueError("AnnotationId must be defined.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteAnnotation(workspaceId=workspaceId, annotationId=annotationId)

