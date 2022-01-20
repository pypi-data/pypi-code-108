from zerohash.resources.abstract import CreateableAPIResource, ListableAPIResource


class Withdrawals(ListableAPIResource, CreateableAPIResource):
    OBJECT_NAME = "withdrawals.requests"
