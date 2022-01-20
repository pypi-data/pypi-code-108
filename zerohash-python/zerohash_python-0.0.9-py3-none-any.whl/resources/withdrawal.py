from zerohash.resources.abstract.api_resource import APIResource


class Withdrawal(APIResource):
    OBJECT_NAME = "withdrawals.requests"

    # We have to override refresh because the API returns a list instead of a single object
    # This causing a hashing issue with the standard refresh_from method. Thus, we extract the first (only)
    # object and process that accordingly.
    def refresh(self):
        self.refresh_from(self.request("get", self.instance_url())[0])
        return self
