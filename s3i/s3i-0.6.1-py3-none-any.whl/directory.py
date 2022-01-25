import requests
import json
import os
import pgpy
from s3i.ditto_manager import DittoManager
from s3i.exception import S3IDirectoryError, raise_error_from_response


class Directory(DittoManager):
    """Class Directory contains functions to query things in S3I Directory """

    def __init__(self, s3i_dir_url, token):
        """
        Constructor

        :param s3i_dir_url: url of S3I Directory, https://dir.s3i.vswf.dev/api/2/
        :type s3i_dir_url: str
        :param token: id token obtained from S3I IdP
        :type token: str
        """
        super().__init__(s3i_dir_url, token)
    
    def queryEndpointService(self, thingID, serviceType):
        """
        Query a endpoint of service

        :param thingID: thingId
        :type thingID: str
        :param serviceType: service type
        :type serviceType: str
        """
        thing = self.queryThingIDBased(thingID=thingID)
        thing = raise_error_from_response(thing, S3IDirectoryError, 200)
        thing_links = thing["attributes"]["thingStructure"]["links"]
        endpoints = list()
        for link in thing_links:
            [endpoints.append(service["endpoints"]) for service in link["target"]
             ["services"] if service["serviceType"] == serviceType]
        return endpoints


    def getPublicKey(self, thingID):  # TODO thingIDs is list
        """
        Query public key of a thing

        :param thingID: thingId
        :type thingID: str
        """
        if isinstance(thingID, str):
            response = requests.get(url=self.ditto_url+"things/"+thingID +
                                    "/attributes/publicKey", headers=self.ditto_headers)
            raise_error_from_response(response, S3IDirectoryError, 200)
            return response.text
        if isinstance(thingID, list):
            keys = list()
            for id in thingID:
                response = requests.get(url=self.ditto_url+"things/"+id +
                                        "/attributes/publicKey", headers=self.ditto_headers)
                raise_error_from_response(response, S3IDirectoryError, 200)
                keys.append(response.text)
            return keys
        else:
            print(
                "[S3I]: Try to get public keys from thing ids but thing ids are neither strings nor lists.")
            return

    def putPublicKey(self, thingID, file):
        """
        Upload/Update public key of a thing

        :param thingID: thingId
        :type thingID: str
        :param file: file which stores a public key
        :type file: str
        """
        path = os.path.join(os.getcwd(), file)
        key, _ = pgpy.PGPKey.from_file(path)
        keystr = key.__str__()
        url_str = self.ditto_url+"things/" + thingID + "/attributes/publicKey"
        response = requests.put(
            url=url_str,  headers=self.ditto_headers, data=json.dumps(keystr))
        raise_error_from_response(response, S3IDirectoryError, 204)
        return response
