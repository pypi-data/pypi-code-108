import base64
import json
import requests
import urllib
import logging
import magic
from datetime import datetime, timedelta
from akeneo_cli.exceptions import *

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AkeneoClient:

    refresh_before = 300
    endpoint = None
    __headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    __client_id = None
    __client_secret = None
    __token = None
    __refresh_token = None
    __expiration_date = None

    def __init__(self, endpoint, client_id, client_secret):
        self.endpoint = endpoint
        self.__client_id = client_id
        self.__client_secret = client_secret

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__client_id = None
        self.__client_secret = None
        self.__token = None
        self.__refresh_token = None
        self.__expiration_date = None

    def __call(self, url, method="GET", data=None, additional_headers={}):
        files = None
        headers = {**self.__headers, **additional_headers}
        if headers["Content-Type"] == "application/json":
            response = getattr(requests, method.lower())(
                url, verify=False, headers=headers, data=json.dumps(data)
            )

        elif headers["Content-Type"] == "multipart/form-data":
            del headers["Content-Type"]
            files = data
            files["file"] = (
                data["file"],
                open(data["file"], "rb"),
                magic.from_file(data["file"]),
            )
            response = getattr(requests, method.lower())(
                url, verify=False, headers=headers, data=data, files=files
            )
        else:
            response = getattr(requests, method.lower())(
                url, verify=False, headers=headers, data=data
            )

        logging.debug(f"API Call: {response.status_code} {method} {url}")
        if response.status_code > 299:
            if response.status_code == 404:
                raise Akeneo_NotFound(response)
            else:
                raise Akeneo_RequestException(response)
        if (
            "Content-Type" in response.headers
            and response.headers["Content-Type"] == "application/json"
        ):
            if (
                "Content-Length" not in response.headers
                or int(response.headers["Content-Length"]) > 0
            ):
                try:
                    return response.json()
                except Exception as e:
                    logging.error(
                        f"Error get json from response: {e}:\n{response.text}"
                    )
            return dict()
        else:
            return response.text

    def __call_api(
        self,
        path,
        method="GET",
        data=None,
        additional_headers={},
        path_suffix="api/rest",
        version="v1",
        filters=None,
    ):
        url = "/".join([self.endpoint, path_suffix, version, path])
        if filters is not None:
            if not url.endswith("?"):
                url += "?"
            for param in filters.keys():
                if not url.endswith("&"):
                    url += "&"
                url += (
                    urllib.parse.quote(str(param))
                    + "="
                    + urllib.parse.quote(str(filters[param]))
                )
        return self.__call(
            url, method=method, data=data, additional_headers=additional_headers
        )

    def __get_token(self, data):
        result = self.__call_api(
            "token",
            method="POST",
            data=data,
            additional_headers=self.get_basic_auth_header(),
            path_suffix="api/oauth",
        )
        self.__check_response_struct(
            ["access_token", "refresh_token", "expires_in"], result
        )
        self.__expiration_date = datetime.now() + timedelta(
            seconds=result["expires_in"]
        )
        self.__token = result["access_token"]
        self.__refresh_token = result["refresh_token"]

    def __call_authenticated_api(
        self,
        path,
        method="GET",
        data=None,
        additional_headers={},
        path_suffix="api/rest",
        version="v1",
        filters=None,
    ):
        if datetime.now() > (
            self.__expiration_date + timedelta(seconds=self.refresh_before)
        ):
            logging.info(
                f"The token will expire in less than {self.refresh_before}s. Refreshing it..."
            )
            self.refresh_token()
        additional_headers["Authorization"] = f"Bearer {self.__token}"
        return self.__call_api(
            path, method, data, additional_headers, path_suffix, version, filters
        )

    def __call_authenticated_url(
        self,
        url,
        method="GET",
        data=None,
        additional_headers={},
    ):
        if datetime.now() > (
            self.__expiration_date + timedelta(seconds=self.refresh_before)
        ):
            logging.info(
                f"The token will expire in less than {self.refresh_before}s. Refreshing it..."
            )
            self.refresh_token()
        additional_headers["Authorization"] = f"Bearer {self.__token}"
        return self.__call(url, method, data, additional_headers)

    def __check_response_struct(self, expects, response_struct):
        for expect in expects:
            if expect not in response_struct:
                raise Akeneo_UnexpectedResponse(expect, response_struct)

    def login(self, username, password):
        data = dict(username=username, password=password, grant_type="password")
        self.__get_token(data)
        logging.info(
            f"Login successful ! Token will expire at {self.__expiration_date}"
        )
        return self

    def refresh_token(self):
        data = dict(refresh_token=self.__refresh_token, grant_type="refresh_token")
        self.__get_token(data)
        logging.info(
            f"Token refresh successful ! New token will expire at {self.__expiration_date}"
        )
        return self

    def get_basic_auth_header(self):
        return {
            "Authorization": "Basic %s"
            % (
                base64.b64encode(
                    bytes(f"{self.__client_id}:{self.__client_secret}", "utf-8")
                ).decode("ascii")
            ),
        }

    def get(
        self,
        type,
        code=None,
        sub_type=None,
        sub_type_code=None,
        sub_sub_type=None,
        sub_sub_type_code=None,
        filters=dict(),
        all=False,
    ):
        path = type
        if code is not None:
            path += f"/{code}"

        if sub_type is not None:
            path += f"/{sub_type}"

        if sub_type_code is not None:
            path += f"/{sub_type_code}"

        if sub_sub_type is not None:
            path += f"/{sub_sub_type}"

        if sub_sub_type_code is not None:
            path += f"/{sub_sub_type_code}"

        if all:
            result = self.__call_authenticated_api(path, filters=filters)
            if "_links" in result and "next" in result["_links"]:
                next_page = result["_links"]["next"]["href"]
            while next_page:
                next_result = self.__call_authenticated_url(next_page)
                result["_embedded"]["items"] = (
                    result["_embedded"]["items"] + next_result["_embedded"]["items"]
                )
                if "_links" in next_result and "next" in next_result["_links"]:
                    next_page = next_result["_links"]["next"]["href"]
                else:
                    next_page = False
            del result["_links"]
            del result["current_page"]
        else:
            result = self.__call_authenticated_api(path, filters=filters)
        return result

    def get_next_page(self, result):
        next_result = None
        if "_links" in result and "next" in result["_links"]:
            next_page = result["_links"]["next"]["href"]
            next_result = self.__call_authenticated_url(next_page)
        return next_result

    def delete(
        self,
        type,
        code,
        sub_type=None,
        sub_type_code=None,
        sub_sub_type=None,
        sub_sub_type_code=None,
    ):
        path = f"{type}/{code}"

        if sub_type is not None:
            path += f"/{sub_type}/{sub_type_code}"

        if sub_sub_type is not None:
            path += f"/{sub_sub_type}/{sub_sub_type_code}"

        return self.__call_authenticated_api(path, method="DELETE")

    def post(
        self,
        type,
        code,
        sub_type=None,
        sub_type_code=None,
        sub_sub_type=None,
        sub_sub_type_code=None,
        data=dict(),
    ):
        path = f"{type}/{code}"

        if sub_type is not None:
            path += f"/{sub_type}/{sub_type_code}"

        if sub_sub_type is not None:
            path += f"/{sub_sub_type}/{sub_sub_type_code}"

        return self.__call_authenticated_api(path, method="POST", data=data)

    def patch(
        self,
        type,
        code,
        sub_type=None,
        sub_type_code=None,
        sub_sub_type=None,
        sub_sub_type_code=None,
        data=dict(),
    ):
        path = f"{type}/{code}"

        if sub_type is not None:
            path += f"/{sub_type}/{sub_type_code}"

        if sub_sub_type is not None:
            path += f"/{sub_sub_type}/{sub_sub_type_code}"

        return self.__call_authenticated_api(path, method="PATCH", data=data)

    def bulk(self, type, code=None, sub_type=None, data=[]):
        path = type
        if code is not None:
            path += f"/{code}/{sub_type}"

        post_data = ""
        for row in data:
            post_data += f"{json.dumps(row)}\n"

        return self.__call_authenticated_api(
            path,
            method="PATCH",
            additional_headers={
                "Content-Type": "application/vnd.akeneo.collection+json"
            },
            data=post_data,
        )

    def put_file(self, type, filepath, data=[]):
        post_data = dict()
        for key in data.keys():
            post_data[key] = f"{json.dumps(data[key])}\n"

        post_data["file"] = filepath

        return self.__call_authenticated_api(
            type,
            method="POST",
            additional_headers={"Content-Type": "multipart/form-data"},
            data=post_data,
        )
