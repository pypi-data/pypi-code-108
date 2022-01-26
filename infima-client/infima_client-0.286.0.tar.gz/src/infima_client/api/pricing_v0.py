from dataclasses import dataclass
from typing import List, Optional

import infima_client.core.api.pricing_v0.pricing_v0_get as _get
import infima_client.core.api.pricing_v0.pricing_v0_get_available_as_ofs as _get_available_as_ofs
import infima_client.core.api.pricing_v0.pricing_v0_get_service_info as _get_service_info
from infima_client.api.utils import unwrap_or_unset
from infima_client.core.client import Client
from infima_client.core.models import (
    CoreBinaryInfo,
    CoreDate,
    GoogleRpcStatus,
    PricingV0GetAvailableAsOfsRequest,
    PricingV0GetAvailableAsOfsResponse,
    PricingV0GetRequest,
    PricingV0GetResponse,
)
from infima_client.core.types import UNSET


@dataclass
class PricingV0:
    client: Client

    def get(
        self, *, as_of: Optional[CoreDate] = None, symbols: Optional[List[str]] = None
    ) -> PricingV0GetResponse:
        _as_of = unwrap_or_unset(as_of)
        _symbols = unwrap_or_unset(symbols)
        json_body = PricingV0GetRequest(as_of=_as_of, symbols=_symbols)
        response = _get.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_available_as_ofs(
        self, *, symbol: Optional[str] = None
    ) -> PricingV0GetAvailableAsOfsResponse:
        _symbol = unwrap_or_unset(symbol)
        json_body = PricingV0GetAvailableAsOfsRequest(symbol=_symbol)
        response = _get_available_as_ofs.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_service_info(self) -> CoreBinaryInfo:
        response = _get_service_info.sync(client=self.client)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response
