from dataclasses import dataclass
from typing import Optional

import infima_client.core.api.market_v0.market_v0_get_service_info as _get_service_info
import infima_client.core.api.market_v0.market_v0_get_story_view as _get_story_view
import infima_client.core.api.market_v0.market_v0_get_view as _get_view
from infima_client.api.utils import unwrap_or_unset
from infima_client.core.client import Client
from infima_client.core.models import (
    CoreBinaryInfo,
    GoogleRpcStatus,
    MarketV0GetStoryViewRequest,
    MarketV0GetStoryViewResponse,
    MarketV0GetViewRequest,
    MarketV0GetViewResponse,
    MbsAgencyTicker,
)
from infima_client.core.types import UNSET


@dataclass
class MarketV0:
    client: Client

    def get_service_info(self) -> CoreBinaryInfo:
        response = _get_service_info.sync(client=self.client)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_story_view(
        self, *, ticker: Optional[MbsAgencyTicker] = None
    ) -> MarketV0GetStoryViewResponse:
        _ticker = unwrap_or_unset(ticker)
        json_body = MarketV0GetStoryViewRequest(ticker=_ticker)
        response = _get_story_view.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_view(
        self, *, ticker: Optional[MbsAgencyTicker] = None
    ) -> MarketV0GetViewResponse:
        _ticker = unwrap_or_unset(ticker)
        json_body = MarketV0GetViewRequest(ticker=_ticker)
        response = _get_view.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response
