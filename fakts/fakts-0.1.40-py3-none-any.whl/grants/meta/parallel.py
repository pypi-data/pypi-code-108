from typing import List
from fakts.grants.base import FaktsGrant
from fakts.beacon import EndpointDiscovery, FaktsRetriever
import asyncio
from functools import reduce

from fakts.utils import update_nested


class ParallelGrant(FaktsGrant):

    def __init__(self, parellized_grants: List[FaktsGrant], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parellized_grants = parellized_grants


    async def aload(self, previous = {}, **kwargs):

        config_futures = [grant.aload(**kwargs) for grant in self.parellized_grants]
        configs = await asyncio.gather(config_futures)
        return reduce(lambda x, y : update_nested(x, y), configs,  previous)