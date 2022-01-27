


from fakts.beacon.beacon import FaktsEndpoint
from fakts.grants.base import FaktsGrant
from fakts.beacon import EndpointDiscovery, FaktsRetriever



async def discover_endpoint(name_filter= None):
    discov = EndpointDiscovery()
    return await discov.ascan_first(name_filter=name_filter)




class BeaconGrant(FaktsGrant):

    def __init__(self, *args, dicovery_protocol: EndpointDiscovery = None, retriever_protocol: FaktsRetriever = None, **kwargs) -> None:

        self._discov = dicovery_protocol or EndpointDiscovery()
        self._retriev = retriever_protocol  or FaktsRetriever()

        super().__init__(*args, **kwargs)

    async def aload(self, previous={}, **kwargs):
        endpoint = await self._discov.ascan_first(**previous)
        return await self._retriev.aretrieve(endpoint, previous=previous)