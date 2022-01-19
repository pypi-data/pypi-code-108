"""API Module
"""
class AnaAPI:
    """
    API Module
    """
    
    def __init__(self, url, headers, verbose=False):
        import requests
        self.url = url
        self.headers = headers
        self.verbose = verbose
        self.session = requests.Session()

    def close(self):
        self.session.close()

    from .handlers      import errorhandler
    from .organizations import getOrganizations, editOrganization
    from .channels      import getChannels, getManagedChannels, getChannelDeployment, createManagedChannel, deleteManagedChannel, editManagedChannel, addChannelOrganization, removeChannelOrganization, deployManagedChannel, setChannelGraph
    from .volumes       import getVolumes, getManagedVolumes, createManagedVolume, deleteManagedVolume, editManagedVolume, addVolumeOrganization, removeVolumeOrganization, getVolumeData, putVolumeData, deleteVolumeData
    from .members       import getMembers, addMember, removeMember, editMember
    from .workspaces    import getWorkspaces, createWorkspace, deleteWorkspace, editWorkspace
    from .graphs        import getGraphs, createGraph, deleteGraph, editGraph, downloadGraph, getDefaultGraph
    from .datasets      import getDatasets, createDataset, deleteDataset, editDataset, downloadDataset, cancelDataset
    from .limits        import getPlatformLimits, setPlatformLimit, getOrganizationLimits, setOrganizationLimit, getWorkspaceLimits, setWorkspaceLimit, getOrganizationUsage
    from .analytics     import getAnalytics, getAnalyticsTypes, createAnalytics, deleteAnalytics
    from .annotations   import getAnnotations, getAnnotationFormats, getAnnotationMaps, createAnnotation, downloadAnnotation
    from .gan           import getGANModels, getGANDataset, createGANDataset, deleteGANDataset