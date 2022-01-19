"""
Analytics API calls.
"""

def getAnalytics(self, analyticsId, datasetId, workspaceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnalytics",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "analyticsId": analyticsId
            },
            "query": """query 
                getAnalytics($workspaceId: String!, $datasetId: String!, $analyticsId: String!) {
                    getAnalytics(workspaceId: $workspaceId, datasetId: $datasetId, analyticsId: $analyticsId){
                        analyticsId
                        workspaceId
                        datasetId
                        status
                        result
                        member
                        type
                        range
                        returnImages
                    }
                }"""})
    return self.errorhandler(response, "getAnalytics")


def getAnalyticsTypes(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnalyticsTypes",
            "variables": {},
            "query": """query 
                getAnalyticsTypes{
                    getAnalyticsTypes
                }"""})
    return self.errorhandler(response, "getAnalyticsTypes")


def createAnalytics(self, workspaceId, datasetId, rangeInput, typeInput, returnImages):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createAnalytics",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "range": rangeInput,
                "type": typeInput,
                "returnImages": returnImages
            },
            "query": """mutation 
                createAnalytics($workspaceId: String!, $datasetId: String!, $range: [Int], $type: String!, $returnImages: Boolean) {
                    createAnalytics(workspaceId: $workspaceId, datasetId: $datasetId, range: $range, type: $type, returnImages: $returnImages)
                }"""})
    return self.errorhandler(response, "createAnalytics")


def deleteAnalytics(self, workspaceId, analyticsId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteAnalytics",
            "variables": {
                "workspaceId": workspaceId,
                "analyticsId": analyticsId
            },
            "query": """mutation 
                deleteAnalytics($workspaceId: String!, $datasetId: String! $analyticsId: String!) {
                    deleteAnalytics(workspaceId: $workspaceId, datasetId: $datasetId, analyticsId: $analyticsId)
                }"""})
    return self.errorhandler(response, "deleteAnalytics")
