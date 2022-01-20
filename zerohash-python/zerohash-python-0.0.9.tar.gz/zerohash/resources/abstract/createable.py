from zerohash import api_requestor, util
from zerohash.resources.abstract.api_resource import APIResource


class CreateableAPIResource(APIResource):
    @classmethod
    def create(cls, credentials=None, idempotency_key=None, **params):

        requestor = api_requestor.APIRequestor(credentials)
        url = cls.class_url()
        response = requestor.request("POST", url, params)
        return util.convert_to_zerohash_object(
            response,
            credentials,  # klass_name=cls.OBJECT_NAME
        )
