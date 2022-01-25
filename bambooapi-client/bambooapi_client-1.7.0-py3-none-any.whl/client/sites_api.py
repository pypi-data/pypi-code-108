"""Sites are physical locations where flexibility devices are deployed."""
import typing as tp

from bambooapi_client.api.sites_api import SitesApi as _SitesApi
from bambooapi_client.exceptions import NotFoundException
from bambooapi_client.model.activation_state import ActivationState
from bambooapi_client.model.baseline_model import BaselineModel
from bambooapi_client.model.flexibility_model import FlexibilityModel
from bambooapi_client.model.site import Site
from bambooapi_client.model.site_data_point import SiteDataPoint
from bambooapi_client.model.site_list_item import SiteListItem
from bambooapi_client.model.thermal_zone import ThermalZone
from bambooapi_client.model.thermal_zone_setpoints import ThermalZoneSetpoints

import pandas as pd


class SitesApi(object):
    """Implementation for '/v1/sites' endpoints."""

    def __init__(self, bambooapi_client):
        """Initialize defaults."""
        self._bambooapi_client = bambooapi_client
        self._api_instance = _SitesApi(bambooapi_client.api_client)

    def list_sites(self) -> tp.List[SiteListItem]:
        """List sites."""
        return self._api_instance.list_sites()

    def get_site(self, site_id: int) -> tp.Optional[Site]:
        """Get site by id."""
        try:
            return self._api_instance.read_site(site_id)
        except NotFoundException:
            return None

    def get_site_id(self, site_name: str) -> tp.Optional[int]:
        """Get site id by name."""
        try:
            return self._api_instance.get_site_id_by_name(site_name)
        except NotFoundException:
            return None

    def list_devices(
        self,
        site_id: int,
        device_type: str = 'hvac',
    ) -> tp.List[tp.Any]:
        """List devices for a given site."""
        return self._api_instance.list_devices(
            site_id,
            device_type=device_type,
        )

    def get_device(self, site_id: int, device_name: str) -> tp.Optional[dict]:
        """Get single device by name for a given site."""
        try:
            return self._api_instance.read_device(site_id, device_name)
        except NotFoundException:
            return None

    def list_thermal_zones(self, site_id: int) -> tp.List[ThermalZone]:
        """List zones for a given site."""
        return self._api_instance.list_thermal_zones(site_id)

    def get_thermal_zone(
        self,
        site_id: int,
        zone_name: str,
    ) -> tp.Optional[ThermalZone]:
        """Get single zone by name for a given site."""
        try:
            return self._api_instance.read_thermal_zone(site_id, zone_name)
        except NotFoundException:
            return None

    def read_device_baseline_model(
        self,
        site_id: int,
        device_name: str,
        horizon: str = 'day-ahead',
    ) -> tp.Optional[BaselineModel]:
        """Read baseline model for a given site and device."""
        try:
            return self._api_instance.read_baseline_model(
                site_id,
                device_name,
                horizon=horizon,
            )
        except NotFoundException:
            return None

    def update_device_baseline_model(
        self,
        site_id: int,
        device_name: str,
        baseline_model: tp.Union[BaselineModel, dict],
        horizon: str = 'day-ahead',
    ) -> BaselineModel:
        """Update baseline model for a given site and device."""
        return self._api_instance.update_baseline_model(
            site_id,
            device_name,
            baseline_model,
            horizon=horizon,
        )

    def read_device_measurements(
        self,
        site_id: int,
        device_name: str,
        start: tp.Optional[str] = None,
        stop: tp.Optional[str] = None,
        frequency: tp.Optional[str] = None,
    ) -> tp.Optional[pd.DataFrame]:
        """Read site device measurements."""
        kwargs = {}
        if start and stop:
            kwargs.update(
                period='CustomRange',
                period_start=start,
                period_stop=stop,
            )
        if frequency:
            kwargs.update(frequency=frequency)
        _meas = self._api_instance.read_device_measurements(
            site_id,
            device_name,
            **kwargs,
        )
        # Convert SiteDataPoint objects to dict before converting to DF
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            # Convert to DF
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_device_measurements(
        self,
        site_id: int,
        device_name: str,
        data_frame: pd.DataFrame,
    ) -> tp.List[SiteDataPoint]:
        """Update site device measurements."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_device_measurements(
            site_id,
            device_name,
            _dps,
        )

    def read_device_baseline_forecasts(
        self,
        site_id: int,
        device_name: str,
        horizon: str = 'day-ahead',
        start: tp.Optional[str] = None,
        stop: tp.Optional[str] = None,
        frequency: tp.Optional[str] = None,
    ) -> pd.DataFrame:
        """Read site device forecasts."""
        kwargs = {}
        if start and stop:
            kwargs.update(
                horizon=horizon,
                period='CustomRange',
                period_start=start,
                period_stop=stop,
            )
        if frequency:
            kwargs.update(frequency=frequency)

        _meas = self._api_instance.read_device_baseline_forecasts(
            site_id,
            device_name,
            **kwargs,
        )
        # Convert DataPoint objects to dict before converting to DF
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            # Convert to DF
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_device_baseline_forecasts(
        self,
        site_id: int,
        device_name: str,
        data_frame: pd.DataFrame,
        horizon: str,
    ) -> tp.List[SiteDataPoint]:
        """Update site device baseline forecasts."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_device_baseline_forecasts(
            site_id,
            device_name,
            _dps,
            horizon=horizon,
        )

    def read_device_activations(
        self,
        site_id: int,
        device_name: str,
    ) -> tp.Optional[ActivationState]:
        """Read site device activations."""
        try:
            return self._api_instance.read_device_activations(
                site_id,
                device_name,
            )
        except NotFoundException:
            return None

    def read_thermal_zone_flexibility_model(
        self,
        site_id: int,
        zone_name: str,
        horizon: str = 'day-ahead',
    ) -> tp.Optional[FlexibilityModel]:
        """Read thermal flexibility model for a given site and zone."""
        try:
            return self._api_instance.read_flexibility_model(
                site_id,
                zone_name,
                horizon=horizon,
            )
        except NotFoundException:
            return None

    def update_thermal_zone_flexibility_model(
        self,
        site_id: int,
        zone_name: str,
        flexibility_model: tp.Union[FlexibilityModel, dict],
        horizon: str = 'day-ahead',
    ) -> FlexibilityModel:
        """Update thermal flexibility model for a given site and zone."""
        return self._api_instance.update_flexibility_model(
            site_id,
            zone_name,
            flexibility_model,
            horizon=horizon,
        )

    def update_device_flexibility_forecast(
        self,
        site_id: int,
        device_name: str,
        data_frame: pd.DataFrame,
        ramping: str,
        horizon: str = 'day-ahead',
    ) -> tp.List[SiteDataPoint]:
        """Update device flexibility forecast."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_device_flexibility_forecasts(
            site_id=site_id,
            device_name=device_name,
            site_data_point=_dps,
            horizon=horizon,
            ramping=ramping,
        )

    def read_device_flexibility_forecast(
        self,
        site_id: int,
        device_name: str,
        ramping: str,
        horizon: str = 'day-ahead',
        start: tp.Optional[str] = None,
        stop: tp.Optional[str] = None,
        frequency: tp.Optional[str] = None,
    ) -> pd.DataFrame:
        """Read site device flexibility."""
        kwargs = {}
        if start and stop:
            kwargs.update(
                period='CustomRange',
                period_start=start,
                period_stop=stop,
            )
        if frequency:
            kwargs.update(frequency=frequency)

        _meas = self._api_instance.read_device_flexibility_forecasts(
            site_id=site_id,
            device_name=device_name,
            ramping=ramping,
            horizon=horizon,
            **kwargs,
        )
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def update_thermal_zone_flexibility_forecast(
        self,
        site_id: int,
        zone_name: str,
        data_frame: pd.DataFrame,
        ramping: str,
        horizon: str = 'day-ahead',
    ) -> tp.List[SiteDataPoint]:
        """Update site thermal zone flexibility forecast."""
        _dps = data_frame.reset_index().to_dict(orient='records')
        return self._api_instance.insert_thermal_zone_flexibility_forecasts(
            site_id=site_id,
            zone_name=zone_name,
            site_data_point=_dps,
            ramping=ramping,
            horizon=horizon,
        )

    def read_thermal_zone_flexibility_forecast(
        self,
        site_id: int,
        zone_name: str,
        ramping: str,
        horizon: str = 'day-ahead',
        start: tp.Optional[str] = None,
        stop: tp.Optional[str] = None,
        frequency: tp.Optional[str] = None,
    ) -> pd.DataFrame:
        """Read site thermal zone flexibility forecast."""
        kwargs = {}
        if start and stop:
            kwargs.update(
                period='CustomRange',
                period_start=start,
                period_stop=stop,
            )
        if frequency:
            kwargs.update(frequency=frequency)

        _meas = self._api_instance.read_thermal_zone_flexibility_forecasts(
            site_id=site_id,
            zone_name=zone_name,
            ramping=ramping,
            horizon=horizon,
            **kwargs,
        )
        if _meas:
            _meas = [m.to_dict() for m in _meas]
            return pd.DataFrame.from_records(_meas, index='time')
        else:
            return pd.DataFrame()

    def read_thermal_zone_setpoints(
        self,
        site_id: int,
        zone_name: str,
    ) -> ThermalZoneSetpoints:
        """Read site thermal zone setpoint."""
        return self._api_instance.read_thermal_zone_setpoints(
            site_id=site_id,
            zone_name=zone_name,
        )

    def update_thermal_zone_setpoints(
        self,
        site_id: int,
        zone_name: str,
        thermal_zone_setpoints: ThermalZoneSetpoints,
    ) -> ThermalZoneSetpoints:
        """Update site thermal zone setpoint."""
        return self._api_instance.update_thermal_zone_setpoints(
            site_id=site_id,
            zone_name=zone_name,
            thermal_zone_setpoints=thermal_zone_setpoints,
        )
