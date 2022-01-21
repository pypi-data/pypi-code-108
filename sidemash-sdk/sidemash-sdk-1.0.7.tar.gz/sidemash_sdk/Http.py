import base64
import hashlib
import hmac
import json
import requests
from typing import Optional
from sidemash_sdk.Sdk import Sdk
from sidemash_sdk.Auth import Auth
from sidemash_sdk.HttpCallError import HttpCallError
from sidemash_sdk.SdmRequest import SdmRequest
from sidemash_sdk.RestCollection import RestCollection


class Http:

    @staticmethod
    def post(path: str, body: Optional[dict], query_string: Optional[dict], headers: Optional[dict], converter, auth: Auth):
        return Http.__call(path, "POST", body, auth, query_string, converter, headers)

    @staticmethod
    def list_all(path: str, query_string: Optional[dict], headers: Optional[dict], converter, auth: Auth):
        return Http.get(path, auth, query_string, lambda json: RestCollection.from_json(json, converter), headers)

    @staticmethod
    def get(path: str, query_string: Optional[dict], headers: Optional[dict], converter, auth: Auth):
        return Http.__call(path, "GET", None, auth, query_string, converter, headers)

    @staticmethod
    def patch(path: str, body: Optional[dict], query_string: Optional[dict], headers: Optional[dict], converter, auth: Auth):
        return Http.__call(path, "PATCH", body, auth, query_string, converter, headers)

    @staticmethod
    def put(path: str, body: Optional[dict], query_string: Optional[dict], headers: Optional[dict], converter, auth: Auth):
        return Http.__call(path, "PUT", body, auth, query_string, converter, headers)

    @staticmethod
    def delete(path: str, body: Optional[dict], query_string: Optional[dict], headers: Optional[dict], converter, auth: Auth):
        return Http.__call(path, "DELETE", body, auth, query_string, converter, headers)

    @staticmethod
    def __sign(message: str, private_key: str):
        signature = hmac.new(bytes(private_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha512).digest()
        return base64.b64encode(signature).decode()

    @staticmethod
    def __sha256(message: str):
        h = hashlib.sha256(bytes(message,  "utf-8")).digest()
        return base64.b64encode(h).decode()

    @staticmethod
    def __compute_signed_headers(body: Optional[str], headers: dict, auth: Auth) -> dict:
        signed_headers = dict(
            {"Accept": "application/json", "User-Agent": "Sdk Python " + Sdk.version(), "Authorization": "Bearer " + auth.token},
            **headers,
            **{"Content-Type": "application/json"} if body is not None else {}
        )
        return signed_headers

    @staticmethod
    def __make_request(method: str, url: str, body: Optional[str], headers: dict):
        r = None
        if method == "POST":
            r = requests.post(url, data=body, headers=headers)
        elif method == "GET":
            r = requests.get(url, headers=headers)
        elif method == "PATCH":
            r = requests.patch(url, data=body, headers=headers)
        elif method == "PUT":
            r = requests.put(url, data=body, headers=headers)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers)
        return r


    @staticmethod
    def __call(path: str, method: str, body: Optional[dict], auth: Auth, query_string: Optional[str], converter, headers: dict):
        body_str = json.dumps(body) if body is not None else None
        url = Sdk.base_url() + path + (query_string if query_string is not None else "")
        signed_headers = Http.__compute_signed_headers(body, headers if headers is not None else {}, auth)
        sdm_request = SdmRequest(signed_headers,
                                 method,
                                 path,
                                 query_string,
                                 body_hash=Http.__sha256(body_str) if body_str is not None else None)
        h = signed_headers
        h["X-Sdm-Nonce"] = str(sdm_request.nonce)
        h["X-Sdm-SignedHeaders"] = ",".join([header_name for header_name in list(signed_headers.keys())])
        h["X-Sdm-Signature"] = "SHA512 " + Http.__sign(sdm_request.to_message(), auth.private_key)
        response = Http.__make_request(method, url, body_str, h)
        if response.status_code >= 300:
            raise HttpCallError(response.status_code, response.reason, response.json())
        elif response.status_code == 204:
            return None
        else:
            return converter(response.json())
