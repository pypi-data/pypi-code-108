"""
Annotations API calls.
"""

def getAnnotations(self, workspaceId, datasetId, annotationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnnotations",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "annotationId": annotationId,
            },
            "query": """query 
                getAnnotations($workspaceId: String!, $datasetId: String! $annotationId: String!) {
                    getAnnotations(workspaceId: $workspaceId, datasetId: $datasetId, annotationId: $annotationId){
                        workspaceId
                        datasetId
                        annotationId
                        map
                        format
                        status
                    }
                }"""})
    return self.errorhandler(response, "getAnnotations")


def getAnnotationFormats(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnnotationFormats",
            "variables": {},
            "query": """query 
                getAnnotationFormats{
                    getAnnotationFormats
                }"""})
    return self.errorhandler(response, "getAnnotationFormats")


def getAnnotationMaps(self, channelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnnotationMaps",
            "variables": {
                "channelId": channelId,
            },
            "query": """query 
                getAnnotationMaps($channelId: String!) {
                    getAnnotationMaps(channelId: $channelId)
                }"""})
    return self.errorhandler(response, "getAnnotationMaps")


def createAnnotation(self, workspaceId, datasetId, format, map):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "format": format,
                "map": map
            },
            "query": """mutation 
                createAnnotation($workspaceId: String!, $datasetId: String!, $format: String!, $map: String!) {
                    createAnnotation(workspaceId: $workspaceId, datasetId: $datasetId, format: $format, map: $map)
                }"""})
    return self.errorhandler(response, "createAnnotation")


def downloadAnnotation(self, workspaceId, datasetId, annotationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "annotationId": annotationId
            },
            "query": """mutation 
                downloadAnnotation($workspaceId: String!, $datasetId: String!, $annotationId: String!) {
                    downloadAnnotation(workspaceId: $workspaceId, datasetId: $datasetId, annotationId: $annotationId)
                }"""})
    return self.errorhandler(response, "downloadAnnotation")


def deleteAnnotation(self, workspaceId, annotationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "annotationId": annotationId
            },
            "query": """mutation 
                deleteAnnotation($workspaceId: String!, $annotationId: String!) {
                    deleteAnnotation(workspaceId: $workspaceId, annotationId: $annotationId)
                }"""})
    return self.errorhandler(response, "deleteAnnotation")
