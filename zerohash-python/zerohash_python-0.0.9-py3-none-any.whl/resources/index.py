from zerohash import util
from zerohash.api_requestor import APIRequestor
from zerohash.resources.abstract.api_resource import APIResource


class Index(APIResource):
    OBJECT_NAME = "index"

    @classmethod
    def retrieve(cls, **kwargs):
        """
        Override the retrieve method to look like the list method as there is no ID to query by in this case.
        """

        requestor = APIRequestor()

        url = cls.class_url()
        response = requestor.request("GET", url, kwargs)

        return util.convert_to_zerohash_object(response)
