import datetime
import hashlib
import hmac
import json
import urllib
import uuid
from base64 import b64decode, b64encode
from urllib.parse import urljoin

import zerohash
from zerohash import error, error_classes, http_client
from zerohash.zerohash_response import ZerohashResponse


class APIRequestor:
    def __init__(
        self,
        credentials=None,
        api_base=None,
        client=None,
    ):
        self.api_base = api_base or zerohash.api_base
        self.credentials = credentials or zerohash.credentials

        if client:
            self._client = client
        elif zerohash.default_http_client:
            self._client = zerohash.default_http_client
        else:
            """If no default http client is set, set one to avoid creating one for every request"""
            zerohash.default_http_client = http_client.new_default_http_client()
            self._client = zerohash.default_http_client

    def handle_error_response(self, rbody, rcode, resp, rheaders):
        try:
            err = self.specific_api_error(rbody, rcode, resp, rheaders)
        except (KeyError, TypeError):
            raise error.APIError(
                f"Invalid response from Zero Hash API: {rbody}. HTTP response code {rcode}",
                rbody,
                rcode,
                resp,
            )
        raise err

    def specific_api_error(self, rbody, rcode, resp, rheaders):

        # api_error_code = resp["code"]
        if 400 <= rcode < 500:
            return zerohash.error.ClientError(
                body=resp,  # resp is serialized, rbody is a bytes string of the body b""
                headers=rheaders,
                status_code=rcode,
            )
        elif rcode > 500:
            return zerohash.error.APIError(headers=rheaders, status_code=rcode)
        else:
            return zerohash.error.UnknownError(body=resp, status_code=rcode)
        # try:
        #     return error_classes.ERROR_CLASSES[api_error_code](
        #         code=resp["code"],
        #         body=resp,
        #         status_code=rcode,
        #         headers=rheaders,
        #     )
        # except KeyError:
        #     return error.UnknownError(body=resp, status_code=rcode)

    def interpret_response(self, rbody, rcode, rheaders):
        try:

            resp = ZerohashResponse(rbody, rcode, rheaders)
        except Exception:
            raise Exception(
                f"Invalid response from API: {rbody} (HTTP response code: {rcode})",
                rbody,
                rcode,
                rheaders,
            )
        if not 200 <= rcode < 300:
            self.handle_error_response(rbody, rcode, resp.data, rheaders)
        return resp

    def _sign(
        self, private_key: str, method: str, route: str, json_body: str, timestamp: str
    ) -> bytes:
        """Given a key and data, create and sign a payload.

        :param api_key: Key to sign the message with
        :param method: HTTP method
        :param route: Relative route. EX. /fills
        :param json_body: JSON as a string. Usually created via json.dumps(dict)
        :param timestamp: Unix Epoch time as a string
        :return: Base64 encoded digest
        """
        msg = bytes(timestamp + method.upper() + route + json_body, encoding="utf-8")
        hm = hmac.new(key=b64decode(private_key), msg=msg, digestmod=hashlib.sha256)
        return b64encode(hm.digest())

    def request_headers(self, credentials, method, route, json_body):
        referrer = "https://api.getlinus.io"
        user_agent = "Zerohash Python Library"
        timestamp = str(int(datetime.datetime.now().timestamp()))
        headers = {
            "X-SCX-API-KEY": credentials.public_key,
            "X-SCX-SIGNED": self._sign(
                private_key=credentials.private_key,
                method=method,
                route=route,
                json_body=json_body,
                timestamp=timestamp,
            ),
            "X-SCX-TIMESTAMP": timestamp,  # Unix Epoch
            "X-SCX-PASSPHRASE": credentials.passphrase,
            "Content-Type": "application/json",
        }

        return headers

    def request(self, method, url, params={}, headers=None):
        rbody, rcode, rheaders = self.request_raw(method, url, params)
        resp = self.interpret_response(rbody, rcode, rheaders)
        return resp

    def request_raw(self, method, url, params={}, supplied_headers=None):
        if self.credentials:
            credentials = self.credentials
        else:
            from zerohash import credentials

            credentials = credentials

        if credentials is None:
            raise error.MalformedAuthorizationError("Missing credentials")

        abs_url = "%s%s" % (self.api_base, url)
        if method.lower() in (
            "post",
            "put",
            "patch",
        ):
            post_data = json.dumps(params, separators=(",", ":"))
        elif method.lower() in (
            "get",
            "delete",
        ):
            post_data = json.dumps({}, separators=(",", ":"))
            if params:
                new_path = "?" + urllib.parse.urlencode(params)
                abs_url = abs_url + new_path
                url = url + new_path
                # abs_url = abs_url + "?" + urllib.parse.urlencode(params)

        headers = self.request_headers(
            credentials, method, route=url, json_body=post_data
        )

        rbody, rcode, rheaders = self._client.request_with_retries(
            method, abs_url, headers, post_data
        )

        return rbody, rcode, rheaders
