"""
GAN API calls.
"""

def getGANModels(self, modelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getGANModels",
            "variables": {
                "modelId": modelId
            },
            "query": """query 
                getGANModels($modelId: String) {
                    getGANModels(modelId: $modelId){
                        modelId
                        name
                        description
                        images
                    }
                }"""})
    return self.errorhandler(response, "getGANModels")


def getGANDataset(self, datasetId, workspaceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getGANDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """query 
                getGANDataset($workspaceId: String!, $datasetId: String!) {
                    getGANDataset(workspaceId: $workspaceId, datasetId: $datasetId) {
                        datasetId: datasetid
                        channelId
                        graphId: source
                        parentDataset: ganparent
                        modelId: ganmodelId
                        interpretations: scenarios
                        user
                        status
                        files
                        size
                        name
                        description
                    }
                }"""})
    return self.errorhandler(response, "getGANDataset")


def createGANDataset(self, modelId, datasetId, workspaceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createGANDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "modelId": modelId,
            },
            "query": """mutation 
                createGANDataset($workspaceId: String!, $datasetId: String!, $modelId: String!) {
                    createGANDataset(workspaceId: $workspaceId, datasetId: $datasetId, modelId: $modelId)
                }"""})
    return self.errorhandler(response, "createGANDataset")


def deleteGANDataset(self, datasetId, workspaceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteGANDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """mutation 
                deleteGANDataset($workspaceId: String!, $datasetId: String!) {
                    deleteGANDataset(workspaceId: $workspaceId, datasetId: $datasetId)
                }"""})
    return self.errorhandler(response, "deleteGANDataset")

