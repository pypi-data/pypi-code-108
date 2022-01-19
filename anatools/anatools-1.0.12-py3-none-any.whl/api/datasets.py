"""
Datasets API calls.
"""

def getDatasets(self, workspaceId, datasetId=None, name=None, email=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDatasets",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "name": name,
                "email": email
            },
            "query": """query 
                getDatasets($workspaceId: String!, $datasetId: String, $name: String, $email: String) {
                    getDatasets(workspaceId: $workspaceId, datasetId: $datasetId, name: $name, member: $email) {
                        datasetId: datasetid
                        name
                        channel
                        graphId: source
                        interpretations: scenarios
                        user
                        type
                        status
                        priority
                        seed
                        count
                        files
                        size
                        description
                    }
                }"""})
    return self.errorhandler(response, "getDatasets")


def createDataset(self, workspaceId, graphId, name, runs, seed, priority, description=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createDataset",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId,
                "name": name,
                "description": description,
                "interpretations": runs,
                "seed": seed,
                "priority": priority
            },
            "query": """mutation 
                createDataset($workspaceId: String!, $graphId: String!, $name: String!, $description: String, $interpretations: Int!, $seed: Int!, $priority: Int!) {
                    createDataset(workspaceId: $workspaceId, graphId: $graphId, name: $name, description: $description, interpretations: $interpretations, seed: $seed, priority: $priority)
                }"""})
    return self.errorhandler(response, "createDataset")


def deleteDataset(self, workspaceId, datasetId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """mutation 
                deleteDataset($workspaceId: String!, $datasetId: String!) {
                    deleteDataset(workspaceId: $workspaceId, datasetId: $datasetId)
                }"""})
    return self.errorhandler(response, "deleteDataset")


def editDataset(self, workspaceId, datasetId, name=None, description=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "name": name,
                "description": description
            },
            "query": """mutation 
                editDataset($workspaceId: String!, $datasetId: String!, $name: String, $description: String) {
                    editDataset(workspaceId: $workspaceId, datasetId: $datasetId, name: $name, description: $description)
                }"""})
    return self.errorhandler(response, "editDataset")


def downloadDataset(self, workspaceId, datasetId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """mutation 
                downloadDataset($workspaceId: String!, $datasetId: String!) {
                    downloadDataset(workspaceId: $workspaceId, datasetId: $datasetId)
                }"""})
    return self.errorhandler(response, "downloadDataset")


def cancelDataset(self, workspaceId, datasetId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "cancelDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """mutation 
                cancelDataset($workspaceId: String!, $datasetId: String!) {
                    cancelDataset(workspaceId: $workspaceId, datasetId: $datasetId)
                }"""})
    return self.errorhandler(response, "cancelDataset")