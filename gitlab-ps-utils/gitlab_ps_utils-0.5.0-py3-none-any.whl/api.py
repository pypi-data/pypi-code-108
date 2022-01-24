from math import ceil as math_ceil
from time import sleep
from re import findall
import requests

from gitlab_ps_utils.logger import myLogger
from gitlab_ps_utils.audit_logger import audit_logger
from gitlab_ps_utils.decorators import stable_retry
from gitlab_ps_utils.misc_utils import generate_audit_log_message, safe_json_response


class GitLabApi(object):
    def __init__(self, app_path=None, log_name=None, ssl_verify=True):
        self.log = myLogger(__name__, app_path=app_path, log_name=log_name)
        self.audit = audit_logger(__name__, app_path=app_path)
        self.ssl_verify = ssl_verify

    def generate_v4_request_url(self, host, api):
        return f"{host}/api/v4/{api}"

    def generate_graphql_request_url(self, host):
        return f"{host}/api/graphql"

    def generate_v4_request_header(self, token):
        return {
            'Private-Token': token,
            'Content-Type': 'application/json'
        }

    @stable_retry
    def generate_get_request(self, host, token, api, url=None, params=None):
        """
        Generates GET request to GitLab API.
        You will need to provide the GL host, access token, and specific api url.

            :param host: (str) GitLab host URL
            :param token: (str) Access token to GitLab instance
            :param api: (str) Specific GitLab API endpoint (ex: projects)
            :param url: (str) A URL to a location not part of the GitLab API. Defaults to None
            :param params:
            :return: The response object *not* the json() or text()

        """

        if url is None:
            url = self.generate_v4_request_url(host, api)

        headers = self.generate_v4_request_header(token)

        if params is None:
            params = {}

        return requests.get(url, params=params, headers=headers, verify=self.ssl_verify)

    @stable_retry
    def generate_post_request(self, host, token, api, data, url=None, graphql_query=False, headers=None, files=None, description=None):
        """
            Generates POST request to GitLab API.

            :param host: (str) GitLab host URL
            :param token: (str) Access token to GitLab instance
            :param api: (str) Specific GitLab API endpoint (ex: projects)
            :param data: (dict) Any data required for the API request

            :kwarg graphql_query: (bool) Sets the URL to use the GraphQL endpoint. Default False
            :kwarg headers: (dict) Any headers to be passed into the request. Default None
            :kwarg files: (dict) Any file content to be passed into the request. Default None
            :kwarg description: (str) A custom description message for the audit self.log. Default None

            :return: request object containing response
        """
        if graphql_query and not url:
            url = self.generate_graphql_request_url(host)
        elif not url:
            url = self.generate_v4_request_url(host, api)
        self.audit.info(generate_audit_log_message("POST", description, url))
        if headers is None:
            headers = self.generate_v4_request_header(token)
        return requests.post(url, data=data, headers=headers, files=files, verify=self.ssl_verify)

    @stable_retry
    def generate_put_request(self, host, token, api, data, headers=None, files=None, description=None):
        """
            Generates PUT request to GitLab API.

            :param host: (str) GitLab host URL
            :param token: (str) Access token to GitLab instance
            :param api: (str) Specific GitLab API endpoint (ex: projects)
            :param data: (dict) Any data required for the API request

            :return: request object containing response
        """
        url = self.generate_v4_request_url(host, api)
        self.audit.info(generate_audit_log_message("PUT", description, url))
        if headers is None:
            headers = self.generate_v4_request_header(token)

        return requests.put(url, headers=headers, data=data, files=files, verify=self.ssl_verify)

    @stable_retry
    def generate_delete_request(self, host, token, api, description=None):
        """
            Generates DELETE request to GitLab API.

            :param host: (str) GitLab host URL
            :param token: (str) Access token to GitLab instance
            :param api: (str) Specific GitLab API endpoint (ex: user/1234)

            :return: request object containing response
        """
        url = self.generate_v4_request_url(host, api)
        self.audit.info(generate_audit_log_message("DELETE", description, url))
        headers = self.generate_v4_request_header(token)

        return requests.delete(url, headers=headers, verify=self.ssl_verify)

    @stable_retry
    def get_count(self, host, token, api):
        """
            Retrieves total count of projects, users, and groups

            :param host: (str) GitLab host URL
            :param token: (str) Access token to GitLab instance
            :param api: (str) Specific GitLab API endpoint (ex: users)

            :return: long containing the data from the 'X-Total' header in the response OR None if the header doesn't exist in the response
        """
        url = self.generate_v4_request_url(host, api)

        response = requests.head(
            url, headers=self.generate_v4_request_header(token), verify=self.ssl_verify)

        if response.headers.get('X-Total', None) is not None:
            return int(response.headers['X-Total'])

    @stable_retry
    def get_total_pages(self, host, token, api):
        """
            Get total number of pages in API result

            :param host: (str) GitLab host URL
            :param token: (str) Access token to GitLab instance
            :param api: (str) Specific GitLab API endpoint (ex: users)

            :return: long containing the data from the 'X-Total-Pages' header in the response OR None if the header doesn't exist in the response
        """
        url = self.generate_v4_request_url(host, api)

        response = requests.head(
            url, headers=self.generate_v4_request_header(token), verify=self.ssl_verify)
        if response.headers.get('X-Total-Pages', None) is not None:
            return int(response.headers['X-Total-Pages'])

        return None

    @stable_retry
    def get_total_count(self, host, token, api, params=None, per_page=100, keyset=False, bypass_x_total_count=False):
        count = self.get_count(host, token, api)
        # Can't use a walrus operator if count is 0
        if (count or count == 0) and bypass_x_total_count is False:
            self.log.info(f"Total count for endpoint {api}: {count}")
            return count

        PER_PAGE = per_page
        start_at = 1
        last_id = 0

        start_page = (start_at / PER_PAGE) + 1  # pages are 1-indexed
        current_page = int(start_page)
        count = 0
        while True:
            url = self.generate_v4_request_url(host, api)
            response = requests.get(url, headers=self.generate_v4_request_header(token), verify=self.ssl_verify, params=self.get_params(
                params, PER_PAGE, current_page, keyset, last_id))
            headers = response.headers
            if headers.get('x-per-page', None):
                if data := safe_json_response(response):
                    # The system key denotes anything autogenerated by GitLab.
                    # If we include this key in our counts, it will lead to inaccurate note counts
                    if 'system' not in data[0].keys():
                        x_per_page = int(headers.get('x-per-page'))
                        self.log.info(
                            f"Retrieved {PER_PAGE * (current_page - 1) + x_per_page} {api}")
                        if keyset:
                            last_id = self.get_last_id(
                                headers.get("Link", None))
                            if last_id is None:
                                break
                        if not headers.get("x-next-page"):
                            count += len(data)
                            break
                        count += x_per_page
                    else:
                        adata = [actual_data for actual_data in data if actual_data.get(
                            "system") is False]
                        if not headers.get("x-next-page"):
                            count += len(adata)
                            break
                        count += len(adata)
            else:
                if data := safe_json_response(self.generate_get_request(host, token, api, params=self.get_params(
                        params, PER_PAGE, current_page, keyset, last_id))):
                    count += len(data)
                break
            current_page += 1
        self.log.info(f"Total count for endpoint {api}: {count}")
        return count

    @stable_retry
    def get_nested_total_count(self, host, token, apis, bypass_x_total_count=False):
        count = 0
        for top_level_data in self.list_all(host, token, apis[0]):
            if nested_id := top_level_data.get("iid", None):
                count += self.get_total_count(
                    host, token, f"{apis[0]}/{nested_id}/{apis[1]}", bypass_x_total_count=bypass_x_total_count)
        return count

    @stable_retry
    def list_all(self, host, token, api, params=None, per_page=100, keyset=False):
        """
            Generates a list of all projects, groups, users, etc.

            :param host: (str) GitLab host URL
            :param token: (str) Access token to GitLab instance
            :param api: (str) Specific GitLab API endpoint (ex: users)
            :param api: (str) Specific GitLab API endpoint (ex: users)
            :param per_page: (int) Total results per request. Defaults to 100

            :yields: Individual objects from the presumed array of data
        """

        count = self.get_count(host, token, api)
        self.log.info(f"Total count for {host} endpoint {api}: {count}")

        PER_PAGE = per_page
        start_at = 0
        end_at = count
        last_id = 0

        if count is not None:
            # total_work = end_at - start_at
            # total_pages = total_work / PER_PAGE
            start_page = (start_at / PER_PAGE) + 1  # pages are 1-indexed
            end_page = int(math_ceil(float(end_at) / float(PER_PAGE)))
            current_page = int(start_page)
            retried = False
            while current_page <= end_page:
                data = self.generate_get_request(host, token, api, params=self.get_params(
                    params, PER_PAGE, current_page, keyset, last_id))
                try:
                    self.log.info(
                        f"Retrieved {PER_PAGE * (current_page - 1) + len(data.json())} {api}")
                    if keyset:
                        last_id = self.get_last_id(
                            data.headers.get("Link", None))
                        if last_id is None:
                            break
                    data = data.json()
                    for project in data:
                        yield project
                    if len(data) < PER_PAGE:
                        break
                    current_page += 1
                    retried = False
                except ValueError as e:
                    self.log.error(e)
                    self.log.error("API request didn't return JSON")
                    self.log.info("Attempting to retry after 10 seconds")
                    sleep(10)
                    # Failure will only be retried once
                    retried = True
                if retried:
                    break
        else:
            start_page = (start_at / PER_PAGE) + 1  # pages are 1-indexed
            current_page = int(start_page)
            while True:
                data = self.generate_get_request(
                    host, token, api, params=self.get_params(
                        params, PER_PAGE, current_page, keyset, last_id))
                try:
                    self.log.info(
                        f"Retrieved {PER_PAGE * (current_page - 1) + len(data.json())} {api}")
                    if keyset:
                        last_id = self.get_last_id(
                            data.headers.get("Link", None))
                        if last_id is None:
                            break
                    data = data.json()
                    for project in data:
                        yield project
                    if len(data) < PER_PAGE:
                        break
                    current_page += 1
                except ValueError as e:
                    self.log.error(e)
                    self.log.error("API Request didn't return JSON")
                    # Retry interval is smaller here because it will just retry
                    # until it succeeds
                    self.log.info("Attempting to retry after 3 seconds")
                    sleep(3)

    @stable_retry
    def search(self, host, token, api, search_query):
        """
            Get total number of pages in API result

            :param host: (str) GitLab host URL
            :param token: (str) Access token to GitLab instance
            :param api: (str) Specific GitLab API endpoint (ex: users)
            :search_query: (str) Specific query to search

            :return: JSON object containing the request response
        """
        return self.generate_get_request(host, token, api, params={
            'search': search_query}).json()

    def get_params(self, params, per_page, current_page, keyset, last_id):
        if params:
            params["page"] = current_page
            params["per_page"] = per_page
        else:
            params = {
                "pagination": "keyset",
                "per_page": per_page,
                "order_by": "id",
                "sort": "asc",
                "id_after": last_id
            } if keyset else {
                "page": current_page,
                "per_page": per_page
            }
        return params

    # Project only keyset-based pagination - https://docs.gitlab.com/ee/api/#keyset-based-pagination

    def get_last_id(self, link):
        # Get id_after value. If the Link key is missing it's done, with an empty list response
        return findall(r"id_after=(.+?)&", link)[0] if link else None
