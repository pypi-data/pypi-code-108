"""
Graphs API calls.
"""

def getGraphs(self, workspaceId, graphId=None, name=None, email=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getGraphs",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId,
                "name": name,
                "email": email
            },
            "query": """query 
                getGraphs($workspaceId: String!, $graphId: String, $name: String, $email: String) {
                    getGraphs(workspaceId: $workspaceId, graphId: $graphId, name: $name, member: $email) {
                        graphid
                        name
                        channel
                        user
                        deleted
                        description
                    }
                }"""})
    return self.errorhandler(response, "getGraphs")


def createGraph(self, workspaceId, channelId, graph, name, description):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createGraph",
            "variables": {
                "workspaceId": workspaceId,
                "channelId": channelId,
                "graph": graph,
                "name": name,
                "description": description
            },
            "query": """mutation 
                createGraph($workspaceId: String!, $channelId: String!, $graph: String!, $name: String!, $description: String) {
                    createGraph(workspaceId: $workspaceId, channelId: $channelId, graph: $graph, name: $name, description: $description)
                }"""})
    return self.errorhandler(response, "createGraph")


def deleteGraph(self, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId
            },
            "query": """mutation 
                deleteGraph($workspaceId: String!, $graphId: String!) {
                    deleteGraph(workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "deleteGraph")


def editGraph(self, workspaceId, graphId, name=None, description=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId,
                "name": name,
                "description": description
            },
            "query": """mutation 
                editGraph($workspaceId: String!, $graphId: String!, $name: String, $description: String) {
                    editGraph(workspaceId: $workspaceId, graphId: $graphId, name: $name, description: $description)
                }"""})
    return self.errorhandler(response, "editGraph")


def downloadGraph(self, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId
            },
            "query": """mutation 
                downloadGraph($workspaceId: String!, $graphId: String!) {
                    downloadGraph(workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "downloadGraph")


def getDefaultGraph(self, channelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDefaultGraph",
            "variables": {
                "channelId": channelId,
            },
            "query": """query 
                getDefaultGraph($channelId: String!) {
                    getDefaultGraph(channelId: $channelId)
                }"""})
    return self.errorhandler(response, "getDefaultGraph")
    