from dataclasses import dataclass
from typing import List, Optional

import infima_client.core.api.prediction_v1.prediction_v1_get as _get
import infima_client.core.api.prediction_v1.prediction_v1_get_available_as_ofs as _get_available_as_ofs
import infima_client.core.api.prediction_v1.prediction_v1_get_latest_as_of as _get_latest_as_of
import infima_client.core.api.prediction_v1.prediction_v1_get_n_months_ahead as _get_n_months_ahead
import infima_client.core.api.prediction_v1.prediction_v1_get_one_month_ahead as _get_one_month_ahead
import infima_client.core.api.prediction_v1.prediction_v1_get_service_info as _get_service_info
from infima_client.api.utils import unwrap_or_unset
from infima_client.core.client import Client
from infima_client.core.models import (
    CoreBinaryInfo,
    CoreDate,
    CoreFactorDateRange,
    GoogleRpcStatus,
    PredictionV1GetAvailableAsOfsRequest,
    PredictionV1GetAvailableAsOfsResponse,
    PredictionV1GetLatestAsOfRequest,
    PredictionV1GetLatestAsOfResponse,
    PredictionV1GetNMonthsAheadRequest,
    PredictionV1GetNMonthsAheadResponse,
    PredictionV1GetOneMonthAheadRequest,
    PredictionV1GetOneMonthAheadResponse,
    PredictionV1GetRequest,
    PredictionV1GetResponse,
)
from infima_client.core.types import UNSET


@dataclass
class PredictionV1:
    client: Client

    def get(
        self, *, symbols: List[str], as_of: Optional[CoreDate] = None
    ) -> PredictionV1GetResponse:
        _symbols = symbols
        _as_of = unwrap_or_unset(as_of)
        json_body = PredictionV1GetRequest(symbols=_symbols, as_of=_as_of)
        response = _get.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_available_as_ofs(
        self, *, symbol: str
    ) -> PredictionV1GetAvailableAsOfsResponse:
        _symbol = symbol
        json_body = PredictionV1GetAvailableAsOfsRequest(symbol=_symbol)
        response = _get_available_as_ofs.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_latest_as_of(
        self, *, date: Optional[CoreDate] = None
    ) -> PredictionV1GetLatestAsOfResponse:
        _date = unwrap_or_unset(date)
        json_body = PredictionV1GetLatestAsOfRequest(date=_date)
        response = _get_latest_as_of.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_n_months_ahead(
        self,
        *,
        num_months: int,
        symbols: List[str],
        factor_date_range: Optional[CoreFactorDateRange] = None,
        return_all_as_ofs: Optional[bool] = None,
    ) -> PredictionV1GetNMonthsAheadResponse:
        _num_months = num_months
        _symbols = symbols
        _factor_date_range = unwrap_or_unset(factor_date_range)
        _return_all_as_ofs = unwrap_or_unset(return_all_as_ofs)
        json_body = PredictionV1GetNMonthsAheadRequest(
            num_months=_num_months,
            symbols=_symbols,
            factor_date_range=_factor_date_range,
            return_all_as_ofs=_return_all_as_ofs,
        )
        response = _get_n_months_ahead.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_one_month_ahead(
        self,
        *,
        symbols: List[str],
        factor_date_range: Optional[CoreFactorDateRange] = None,
        return_all_as_ofs: Optional[bool] = None,
    ) -> PredictionV1GetOneMonthAheadResponse:
        _symbols = symbols
        _factor_date_range = unwrap_or_unset(factor_date_range)
        _return_all_as_ofs = unwrap_or_unset(return_all_as_ofs)
        json_body = PredictionV1GetOneMonthAheadRequest(
            symbols=_symbols,
            factor_date_range=_factor_date_range,
            return_all_as_ofs=_return_all_as_ofs,
        )
        response = _get_one_month_ahead.sync(client=self.client, json_body=json_body)
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
