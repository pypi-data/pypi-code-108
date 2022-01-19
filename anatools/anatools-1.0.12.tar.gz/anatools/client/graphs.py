"""
Staged Graphs Functions
"""

def get_staged_graphs(self, graphId=None, name=None, email=None, workspaceId=None):
    """Queries the workspace staged graphs based off provided parameters. Checks on graphId, name, or owner in this respective order within the specified workspace.
    If only workspace ID is provided, this will return all the staged graphs in a workspace. 
    
    Parameters
    ----------
    graphid : str
        Staged GraphID to filter on. Optional.
    name : str
        Name of the staged graph to filter on. Optional.
    email: str
        Owner of staged graphs to filter on. Optional.
    workspaceId : str    
        Workspace ID to filter on. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    list[dict]
        A list of staged graphs based off provided query parameters if any parameters match.
    """
    if self.check_logout(): return
    if graphId is None: graphid = ''
    if name is None: name = ''
    if email is None: email = ''
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getGraphs(workspaceId=workspaceId, graphId=graphId, name=name, email=email)


def create_staged_graph(self, name, channelId, graph, description=None, workspaceId=None):
    """Generates a new staged graph based off provided parameters. Must provide valid json string to create a new staged graph.
    
    Parameters
    ----------
    name : str
        Name for the  that will get generated.
    channelId: str
        Id of channel to generate the staged graph with.
    graph: str
        The graph as a dictionary or `JSON` string. While `YAML` files are used in channel development, the Platform SDK and API only support `JSON`. 
        Ensure that the `YAML` file is valid in order for the `yaml.safe_load` to convert `YAML` to a dictionary for you. Otherwise,  provide a graph in `JSON` format.
    description: str
        Description of staged graph. Optional.
    workspaceId : str    
        Workspace ID create the staged graph in. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    str
        The staged graph id if it was created sucessfully or an error message.
    """
    if self.check_logout(): return
    if name is None: raise ValueError('Name input must be defined.')
    if graph is None: raise ValueError('Graph input must be defined.')
    if channelId is None: raise ValueError('ChannelId input must be defined.')
    if workspaceId is None: workspaceId = self.workspace
    if type(graph) is dict:
        import json
        graph = json.dumps(graph)
    return self.ana_api.createGraph(workspaceId=workspaceId, channelId=channelId, graph=graph, name=name, description=description)


def edit_staged_graph(self, graphId, description=None, name=None, workspaceId=None):
    """Update staged graph description and name. 
    
    Parameters
    ----------
    graphId : str
        Staged Graph id to update.
    description: str
        New description to update.
    name: str
        New name to update.
    workspaceId : str    
        Workspace ID of the staged graph's workspace. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        A success or error message based on staged graph's update.
    """
    if self.check_logout(): return
    if graphId is None: return
    if name is None and description is None: return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editGraph(workspaceId=workspaceId, graphId=graphId, name=name, description=description)


def delete_staged_graph(self, graphId, workspaceId=None):
    """Delete a staged graph in a workspace.
    
    Parameters
    ----------
    graphId : str
        Staged Graph id to delete.
    workspaceId : str    
        Workspace ID of the staged graph's workspace. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        A success or error message based on staged graph's delete.
    """
    if self.check_logout(): return
    if graphId is None: return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteGraph(workspaceId=workspaceId, graphId=graphId)
    

def download_staged_graph(self, graphId, workspaceId=None):
    """Download a staged graph.
    
    Parameters
    ----------
    graphId : str
        Graph ID of the staged graph to download.
    workspaceId : str    
        Workspace ID of the staged graph's workspace. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    str
        A download URL that can be used in the browser or a failure message.
    """
    if self.check_logout(): return
    if graphId is None: return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.downloadGraph(workspaceId=workspaceId, graphId=graphId)


def get_default_graph(self, channelId):
    """Gets the default graph for a channel.
    
    Parameters
    ----------
    channelId:
        Id of channel to get the default graph for.
   
    Returns
    -------
    json
        json data representing the graph.
    """
    if self.check_logout(): return
    return self.ana_api.getDefaultGraph(channelId=channelId)


def set_default_graph(self, channelId, workspaceId, graphId):
    """Sets the default graph for a channel. User must be in the organization that manages the channel.
    
    Parameters
    ----------
    channel : str
        The name of the channel to update the default graph.
    workspaceId : str
        The ID of the Workspace that the graph is in.
    graphId: str
        The ID of the graph that you want to be the default for the channel.
    
    Returns
    -------
    str
        Status
    """
    if self.check_logout(): return
    if graphId is None: raise Exception('GraphID must be specified.')
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.setChannelGraph(channelId=channelId, workspaceId=workspaceId, graphId=graphId)

