""" Base class for interacting with Sermos Cloud API.
"""
import json
import logging
import requests
from sermos.utils.config_utils import get_access_key, get_deployment_id
from sermos.constants import DEFAULT_BASE_URL, DEPLOYMENTS_DEPLOY_URL,\
    DEPLOYMENTS_SERVICES_URL

logger = logging.getLogger(__name__)


class SermosCloud():
    """ Primary Sermos Cloud class for interacting with API.
    """
    def __init__(self,
                 access_key: str = None,
                 base_url: str = None,
                 deployment_id: str = None):
        """ Arguments:
                access_key (optional): Access key, issued by Sermos, which is
                    tied to a `Deployment`. Defaults to checking the environment
                    for `SERMOS_ACCESS_KEY`. If not found, will exit.
                base_url (optional): Defaults to primary Sermos Cloud API
                    endpoint (https://cloud.sermos.ai/api/v1/).
                    Only modify this if there is a specific, known reason to do so.
                deployment_id: UUID for Deployment. Find in your Sermos
                    Cloud Console.
        """
        super(SermosCloud, self).__init__()
        self.access_key = get_access_key(access_key)
        self.base_url = base_url if base_url\
            else DEFAULT_BASE_URL
        try:
            self.deployment_id = get_deployment_id(deployment_id)
        except KeyError:
            self.deployment_id = None  # Not always required, so allow None ...

        self.deploy_url = DEPLOYMENTS_DEPLOY_URL.format(
            self.base_url, self.deployment_id)
        self.services_url = DEPLOYMENTS_SERVICES_URL.format(
            self.base_url, self.deployment_id)

        # Note: Sermos Cloud's API expects `apikey`
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.access_key
        }

    def get(self, url: str, as_dict: bool = False):
        """ Send a GET request to Sermos Cloud
        """
        r = requests.get(url, headers=self.headers)
        if as_dict:
            return r.json()
        return r

    def get_all(self, url: str, page: int = 0, page_size: int = 15):
        """ Loop through all paginated results from a GET endpoint
        """
        new_results = True
        results = []
        while new_results:
            this_url = f"{url}?page={page}&sort_order=DESC&page_size={page_size}"
            r = requests.get(this_url, headers=self.headers).json()
            new_results = r.get("data", {}).get("results", [])
            results.extend(new_results)
            page += 1

        return {'data': {'results': results}, 'message': 'All Results'}

    def post(self, url: str, payload: dict = None, as_dict: bool = False):
        """ Send a POST request to Sermos Cloud
        """
        if payload is None:
            payload = {}
        r = requests.post(url, headers=self.headers, data=json.dumps(payload))
        if as_dict:
            return r.json()
        return r
