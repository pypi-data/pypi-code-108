from loguru import logger
import requests
import os
from gql import gql, Client#, AIOHTTPTransport, RequestsHTTPTransport # This is gql version 3
from gql.transport.requests import RequestsHTTPTransport
import json

class FileImportService():
    
    def __init__(self) -> None:
        endpoint = 'http://172.16.2.206:7200/graphql/'
    
        transport =  RequestsHTTPTransport(url=endpoint, verify=True)
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

    def importFile(self, path):
        file = open(path, 'rb')
        fileName = os.path.split(path)[-1]

        graphQlString = 'mutation ($input: [UploadFileInput!]!) { uploadFiles(input: $input) { ... on FileFailed { fileName message } ... on ProfileFailed { fileName importProfileId message } ... on ObjectFailed { fileName importProfileId messages } } }'

        files = {
            '0': (fileName, file),
            'operations': (None, f'{{ "query": "{graphQlString}", "variables": {{"input": [{{ "file": null }}]}}}}'),
            'map': (None, '{ "0": ["variables.input.0.file"] }'),
        }

        response = requests.post(self.endpoint, files=files)

        response = json.loads(response.text)
        for file in response['data']['uploadFiles']:
            logger.error(f"Filename: {file['fileName']}, ImportProfileId: {file['importProfileId']}, Message: {file['message']} ")

        return

if __name__ == '__main__':
    a = FileImportService()
    resp = a.importFile(r'C:\temp\techstack_test\items_appartments_comma.csv')