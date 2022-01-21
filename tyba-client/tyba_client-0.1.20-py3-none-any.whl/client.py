from tyba_client.models import PVModel, PVStorageModel, StandaloneStorageModel
import json
import requests


class Ancillary(object):
    def __init__(self, prices):
        self.prices = prices

    def get(self, route, params=None):
        return self.prices.get(f"ancillary/{route}", params=params)

    def get_pricing_regions(self, *, iso, service, market):
        return self.get("regions", {"iso": iso,
                                    "service": service,
                                    "market": market})

    def get_prices(self, *, iso, service, market, region, start_year, end_year):
        return self.get("prices", {"iso": iso,
                                   "service": service,
                                   "market": market,
                                   "region": region,
                                   "start_year": start_year,
                                   "end_year": end_year})


class LMP(object):
    def __init__(self, prices):
        self.prices = prices

    def get(self, route, params=None):
        return self.prices.get(f"lmp/{route}", params=params)

    def get_all_nodes(self, *, iso):
        return self.get("nodes", {"iso": iso})

    def get_prices(self, *, node_ids, market, start_year, end_year):
        return self.get("prices", {"node_ids": json.dumps(node_ids),
                                   "market": market,
                                   "start_year": start_year,
                                   "end_year": end_year})


class Services(object):
    def __init__(self, client):
        self.client = client
        self.ancillary = Ancillary(self)
        self.lmp = LMP(self)

    def get(self, route, params=None):
        return self.client.get(f"services/{route}", params=params)

    def get_all_isos(self):
        return self.get("isos")


class Client(object):
    """Tyba client class"""

    DEFAULT_OPTIONS = {
        'version': '0.1'
    }

    def __init__(self, personal_access_token, host="https://dev.tybaenergy.com", request_args=None):
        """A :class:`Client` object for interacting with Tyba's API.
        """
        self.personal_access_token = personal_access_token
        self.host = host
        self.services = Services(self)
        self.request_args = {} if request_args is None else request_args

    def _auth_header(self):
        return self.personal_access_token

    def _base_url(self):
        return self.host + "/public/" + self.DEFAULT_OPTIONS["version"] + "/"

    def get(self, route, params=None):
        return requests.get(self._base_url() + route,
                            params=params,
                            headers={"Authorization": self._auth_header()},
                            **self.request_args)

    def post(self, route, json):
        return requests.post(self._base_url() + route,
                             json=json,
                             headers={"Authorization": self._auth_header()},
                             **self.request_args
                             )

    def schedule_pv(self, pv_model: PVModel):
        model_json_dict = pv_model.to_dict()
        return self.post("schedule-pv", json=model_json_dict)

    def schedule_storage(self, storage_model: StandaloneStorageModel):
        model_json_dict = storage_model.to_dict()
        return self.post("schedule-storage", json=model_json_dict)

    def schedule_pv_storage(self, pv_storage_model: PVStorageModel):
        model_json_dict = pv_storage_model.to_dict()
        return self.post("schedule-pv-storage", json=model_json_dict)

    def get_status(self, run_id: str):
        url = "get-status/" + run_id
        return self.get(url)
