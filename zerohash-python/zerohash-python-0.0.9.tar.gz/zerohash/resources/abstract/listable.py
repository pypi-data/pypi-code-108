from zerohash import util
from zerohash.api_requestor import APIRequestor
from zerohash.resources.abstract.api_resource import APIResource


class ListableAPIResource(APIResource):
    @classmethod
    def list(cls, **params):
        requestor = APIRequestor()
        url = cls.class_url()
        response = requestor.request("GET", url, params)
        zerohash_object = util.convert_to_zerohash_object(response)
        return zerohash_object
