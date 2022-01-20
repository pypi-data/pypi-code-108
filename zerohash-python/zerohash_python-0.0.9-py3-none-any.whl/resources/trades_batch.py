from zerohash import api_requestor, util
from zerohash.resources.abstract import CreateableAPIResource


class TradesBatch(CreateableAPIResource):
    OBJECT_NAME = "trades.batch"

    @classmethod
    def create(cls, credentials=None, idempotency_key=None, trades=None):
        if trades is None:
            trades = []
        requestor = api_requestor.APIRequestor(credentials)
        url = cls.class_url()
        response = requestor.request("POST", url, params=trades)
        return util.convert_to_zerohash_object(
            response,
            credentials,  # klass_name=cls.OBJECT_NAME
        )
