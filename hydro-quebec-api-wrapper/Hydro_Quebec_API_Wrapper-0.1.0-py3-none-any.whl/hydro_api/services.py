"""Wrappers to API calls and associated post processing."""

import logging
import json

import datetime

from hydroqc.config.config import Config
from .auth import Hydro

log = logging.getLogger(__name__)


GET_WINTER_CREDIT_API_URL = (
    "https://cl-services.idp.hydroquebec.com/cl/prive/api"
    "/v3_0/tarificationDynamique/creditPointeCritique")
HOURLY_CONSUMPTION_API_URL = (
    "https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele"
    "/portrait-de-consommation/resourceObtenirDonneesConsommationHoraires/")
DAILY_CONSUMPTION_API_URL = (
    "https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/"
    "portrait-de-consommation/resourceObtenirDonneesQuotidiennesConsommation")


class Services:
    """Hydro Quebec API services."""

    def __init__(self):
        """Hydroquebec Services constructor."""
        self.auth = Hydro()
        self.auth.login()
        self.api_headers = self.auth.get_api_headers()
        self.session = self.auth.session
        self.config = Config()

    def get_winter_credit(self):
        """Return information about the winter credit.

        :return: raw JSON from hydro QC API
        """
        params = {"noContrat": self.auth.contract_id}
        api_call_response = self.session.get(
            GET_WINTER_CREDIT_API_URL,
            headers=self.api_headers,
            params=params,
        )
        return json.loads(api_call_response.text)

    def get_today_hourly_consumption(self):
        """Return latest consumption info (about 2h delay it seems).

        :return: raw JSON from hydro QC API for current day (not officially supported, data delayed)
        """
        date = datetime.date
        today = date.today().strftime("%Y-%m-%d")
        yesterday = (date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        # We need to call a valid date first as theoretically today is invalid
        # and the api will not respond if called directly
        self.get_hourly_consumption(yesterday)
        return self.get_hourly_consumption(today)

    def get_hourly_consumption(self, date):
        """Return hourly consumption for a specific day.

        :param: date: YYYY-MM-DD string to pass to API

        :return: raw JSON from hydro QC API
        """
        api_call_response = self.session.get(
            HOURLY_CONSUMPTION_API_URL,
            params={"date": date},
        )

        return json.loads(api_call_response.text)

    def get_daily_consumption(self, start_date, end_date):
        """Return hourly consumption for a specific day.

        :param: start_date: YYYY-MM-DD string to pass to API
        :param: end_date: YYYY-MM-DD string to pass to API

        :return: raw JSON from hydro QC API
        """
        params = {"dateDebut": start_date, "dateFin": end_date}
        api_call_response = self.session.get(
            DAILY_CONSUMPTION_API_URL,
            params=params,
        )

        return json.loads(api_call_response.text)
