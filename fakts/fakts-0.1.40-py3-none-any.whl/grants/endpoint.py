


from fakts.beacon.beacon import FaktsEndpoint
from fakts.grants.base import FaktsGrant
from fakts.beacon import EndpointDiscovery, FaktsRetriever




class EndpointGrant(FaktsGrant):

    def __init__(self, endpoint: FaktsEndpoint, retrieve_protocol: FaktsRetriever = None) -> None:
        self._endpoint = endpoint
        self._retriev = retrieve_protocol  or FaktsRetriever()

        super().__init__()

    async def aload(self, previous={}, **kwargs):
        return await self._retriev.aretrieve(self._endpoint, previous=previous)