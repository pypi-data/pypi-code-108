"""
Analytics Functions
"""

def get_analytics_types(self):
    """Retrieve the analytics types available on the Platform.
    
    Returns
    -------
    list[str]
        The analytics types available on the Platform.
    """
    if self.check_logout(): return
    return self.ana_api.getAnalyticsTypes()


def get_analytics(self, datasetId, analyticsId, workspaceId=None):
    """Retrieve information about analytics jobs.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID that the analytics job is associated with.
    analyticsId : str
        Job ID for an analytics job. 
    workspaceId: str
        Workspace ID where the analytics exist. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    list[dict]
        Analytics job information.
    """
    import os, json, requests
    if self.check_logout(): return
    if datasetId is None: raise ValueError("DatasetId must be provided.")
    if analyticsId is None: raise ValueError("AnalyticsId must be provided.")
    if workspaceId is None: workspaceId = self.workspace
    result = self.ana_api.getAnalytics(workspaceId=workspaceId, datasetId=datasetId, analyticsId=analyticsId)
    analytics_result = json.dumps(result)
    presigned_urls = [str for str in analytics_result.split("\\\"") if str.startswith("https")]

    for i in range(len(presigned_urls)):
        filename = presigned_urls[i].split("/")[-1].split("?")[0]
        print(f"\r[{i+1} / {len(presigned_urls)}]  Downloading {filename}...", end="", flush=True)
        
        with requests.get(presigned_urls[i], allow_redirects=True) as response:
            with open(filename, "wb") as outfile:
                outfile.write(response.content)
        analytics_result = analytics_result.replace(presigned_urls[i], os.path.join(os.getcwd(), filename), 1)
    print("\r", end="")

    return json.loads(analytics_result)


def create_analytics(self, datasetId, type, range=[], images=True, workspaceId=None):
    """Generate analytics for a dataset.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to download image annotation for.
    type : str
        The type of analytics to generate. Choose one from the list that `get_analytics_types` method returns.  
    range : list[int]
        The range of runs to generate analytics for.
    workspaceId: str
        Workspace ID of the dataset to generate the analytics for. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        The analyticsId for the analytics job.
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createAnalytics(workspaceId=workspaceId, datasetId=datasetId, typeInput=type, rangeInput=range, returnImages=images)


def delete_analytics(self, analyticsId, workspaceId=None):
    """Deletes a dataset's analytics.
    
    Parameters
    ----------
    analyticsId : str
        Analytics ID for the analytics to delete. 
    workspaceId: str
        Workspace ID where the analytics exist. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        If true, successfully deleted the analytics.
    """
    if self.check_logout(): return
    if analyticsId is None: raise ValueError("AnalyticsId must be defined.")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteAnalytics(workspaceId=workspaceId, analyticsId=analyticsId)

