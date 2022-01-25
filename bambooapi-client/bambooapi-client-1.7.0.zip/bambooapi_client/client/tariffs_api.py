"""Electricity tariffs."""
import typing as tp
from datetime import datetime

from bambooapi_client.api.tariffs_api import TariffsApi as _TariffsApi
from bambooapi_client.exceptions import NotFoundException
from bambooapi_client.model.monthly_tariff_create import MonthlyTariffCreate
from bambooapi_client.model.monthly_tariff_update import MonthlyTariffUpdate
from bambooapi_client.model.seasonal_tariff_create import SeasonalTariffCreate
from bambooapi_client.model.seasonal_tariff_update import SeasonalTariffUpdate
from bambooapi_client.model.tariff_list_item import TariffListItem

import pandas as pd


class TariffsApi:
    """Implementation for '/v1/tariff' endpoints."""

    def __init__(self, bambooapi_client):
        """Initialize defaults."""
        self._bambooapi_client = bambooapi_client
        self._api_instance = _TariffsApi(bambooapi_client.api_client)

    def list_tariffs(self) -> tp.List[TariffListItem]:
        """List tariffs."""
        return self._api_instance.list_tariffs()

    def get_tariff(self, tariff_id: int) -> tp.Optional[dict]:
        """Get tariff by id."""
        try:
            return self._api_instance.get_tariff(tariff_id)
        except NotFoundException:
            return None

    def create_tariff(
        self,
        tariff: tp.Union[MonthlyTariffUpdate, SeasonalTariffUpdate],
    ) -> dict:
        """Create a new tariff."""
        return self._api_instance.create_tariff(tariff.to_dict())

    def update_tariff(
        self,
        tariff_id: int,
        tariff: tp.Union[MonthlyTariffUpdate, SeasonalTariffUpdate],
    ) -> dict:
        """Update tariff."""
        return self._api_instance.update_tariff(
            tariff_id,
            tariff.to_dict(),
        )

    def delete_tariff(self, tariff_id: int) -> dict:
        """Delete tariff."""
        return self._api_instance.delete_tariff(tariff_id)

    def get_tariff_schedule(
        self,
        tariff_id: int,
        period_start: datetime,
        period_stop: datetime,
    ) -> pd.DataFrame:
        """Return a pd.Dataframe with the tariff schedule between two dates."""
        schedule = self._api_instance.get_tariff_schedule(
            tariff_id,
            period_start=period_start,
            period_stop=period_stop,
        )
        schedule_dicts = [
            tariff_period_item.to_dict() for tariff_period_item in schedule
        ]
        if schedule:
            return pd.json_normalize(
                data=schedule_dicts
            ).set_index(['time'])
        else:
            return pd.DataFrame()
