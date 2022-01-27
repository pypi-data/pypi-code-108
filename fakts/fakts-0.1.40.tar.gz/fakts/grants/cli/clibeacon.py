


from fakts.beacon.beacon import FaktsEndpoint
from fakts.grants.base import FaktsGrant, GrantException
from fakts.beacon import EndpointDiscovery, FaktsRetriever
from rich.prompt import Prompt
from rich.console import Console


class PrompingBeaconGrantException(GrantException):
    pass

class NoBeaconsFound(PrompingBeaconGrantException):
    pass


class CLIBeaconGrant(FaktsGrant):

    def __init__(self, *args, dicovery_protocol: EndpointDiscovery = None, retriever_protocol: FaktsRetriever = None, timeout=4, console = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._discov = dicovery_protocol or EndpointDiscovery()
        self._retriev = retriever_protocol or FaktsRetriever()
        self._console = console or Console()
        self._timeout = timeout

    async def aload(self, previous = {}, **kwargs):

        with self._console.status(f"Waiting {self._timeout} seconds for Beacon Answers"):
            endpoints = await self._discov.ascan_list(timeout=self._timeout)
        
        if len(endpoints.keys()) == 0: raise NoBeaconsFound("We couldn't find any beacon in your local network")

        choices_name = [key for key, value in endpoints.items()]
        endpoint_name = Prompt.ask("Which Endpoint do you want", choices=choices_name, default=choices_name[0])

        with self._console.status(f"Please check your broswer window to finish the setup"):
            return await self._retriev.aretrieve(endpoints[endpoint_name], previous)