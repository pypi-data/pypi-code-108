from infima_client.api.cohort_v1 import CohortV1
from infima_client.api.market_v0 import MarketV0
from infima_client.api.pool_v1 import PoolV1
from infima_client.api.prediction_v1 import PredictionV1
from infima_client.api.pricing_v0 import PricingV0
from infima_client.api.search_v0 import SearchV0
from infima_client.core.client import Client


class ServiceAPI:
    cohort_v1: CohortV1
    market_v0: MarketV0
    pool_v1: PoolV1
    prediction_v1: PredictionV1
    pricing_v0: PricingV0
    search_v0: SearchV0

    def __init__(self, client: Client) -> None:
        self.cohort_v1 = CohortV1(client)
        self.market_v0 = MarketV0(client)
        self.pool_v1 = PoolV1(client)
        self.prediction_v1 = PredictionV1(client)
        self.pricing_v0 = PricingV0(client)
        self.search_v0 = SearchV0(client)
