"""Provide BambooAPIClient mock."""

from unittest.mock import Mock

from bambooapi_client.client.bambooapi_client import BambooAPIClient
from bambooapi_client.client.sites_api import SitesApi
from bambooapi_client.client.weather_api import WeatherApi


def api_client_mock():
    """Mock Api client.

    Use this mock to test safely your implementations.
    """
    api_client = Mock(spec_set=BambooAPIClient)
    api_client.sites_api.return_value = Mock(spec_set=SitesApi)
    api_client.weather_api.return_value = Mock(spec_set=WeatherApi)
    return api_client
