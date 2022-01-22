import json
import math
import os

import requests

from glapi import configuration

CERT_IS_PRESENT = "REQUESTS_CLIENT_CERT" in os.environ and os.environ["REQUESTS_CLIENT_CERT"] and os.environ["REQUESTS_CLIENT_CERT"] != ""
KEY_IS_PRESENT = "REQUESTS_CLIENT_KEY" in os.environ and os.environ["REQUESTS_CLIENT_KEY"] and os.environ["REQUESTS_CLIENT_KEY"] != ""

class GitlabConnection:
    """
    GitlabConnection is a connection instance to a Gitlab API.
    """

    def __init__(self, version: str = configuration.GITLAB_API_VERSION, token: str = configuration.GITLAB_TOKEN):
        """
        Args:
            token (string): GitLab token (personal or deploy)
            version (string): GitLab API url specific to api version
        """
        self.token = token
        self.version = version

    def query(self, endpoint: str, params: dict = dict()) -> dict:
        """
        Attempt HTTP request to GitLab API.

        Args:
            endpoint (string): GitLab API resource
            params (dictionary): key/value pair of optional params to use with endpoint

        Returns:
            A dictionary with data, status, headers keys and corresponding values from GitLab API.
        """

        # process params into string
        params = "".join(["&%s=%s" % (key, params[key]) for key in list(params.keys())]) if not isinstance(params, str) else None

        # construct request url
        url = "%s/%s?private_token=%s&per_page=%s%s" % (
            self.version,
            endpoint,
            self.token,
            configuration.GITLAB_PAGINATION_PER_PAGE,
            "%s" % params if params else str()
        )
        
        # attempt request to service
        try:
            result = requests.get(url, cert=(os.environ["REQUESTS_CLIENT_CERT"], os.environ["REQUESTS_CLIENT_KEY"])) if (CERT_IS_PRESENT and KEY_IS_PRESENT) else requests.get(url)
        except Exception as e:
            raise e

        # read in as dictionary and expose some request info
        return {
            "data": json.loads(result.text) if (result.status_code == 200 and result.text and "raw" not in endpoint and "ref" not in params) else (result.text if "raw" in endpoint and "ref" in params else list()),
            "headers": result.headers,
            "status": result.status_code
        }

    def paginate(self, endpoint, params=dict(), data=list()):
        """
        Paginate through GitLab API headers to ensure all results captured.

        Args:
            data (list): existing data from previous request
            endpoint (string): Gitlab API resource
            params (dictionary): key/value pair of optional params to use with endpoint

        Returns:
            A list of dictionaries where each represents a GitLab object.
        """

        # make initial request
        data = self.query(endpoint, params)

        # get total number in gitlab instance
        # b/c it forces us to paginate/can't get all the results at once
        total_count = int(data["headers"]["X-Total"]) if "X-Total" in data["headers"] else None

        # how many are left to pull
        remaining_count = math.ceil(total_count / configuration.GITLAB_PAGINATION_PER_PAGE) - 1 if total_count else 0

        # set results as initial API request
        result = data["data"]

        # check difference between total and requested
        # make additional calls based on remaining issues
        for i in range(remaining_count):

            # update params
            params["page"] = str(i + 2)

            # add to results
            result += self.query(endpoint, params)["data"]

        return result
