import logging
import re
import requests
import urllib3

from json import JSONEncoder, JSONDecoder
from requests import Response
from typing import Dict, Any, cast, Optional, List, Tuple, BinaryIO, Sequence
from vectice.api.json_object import JsonObject

DEFAULT_API_ENDPOINT = "http://localhost:4000"

logger = logging.getLogger("vectice.http")


class HttpError(Exception):
    def __init__(self, code: int, reason: str, path: str, method: str, json: Optional[str]):
        super().__init__()
        self.code: int = code
        self.reason: str = reason
        self.path = path
        self.method = method
        self.json = json

    def __str__(self):
        return f"""HTTP Error Code {self.code} : {self.reason}
        {self.method} {self.path}

        {self.json}
        """


def format_url(url: str) -> str:
    """Add https protocol if missing and remove trailing slash."""
    url = url.rstrip("/")
    if not re.match("(?:http|https|ftp)://", url):
        return "https://{}".format(url)
    return url


class VecticeEncoder(JSONEncoder):
    """
    Json Encoder with 2 specific behaviors:
    - handle datetime types so be serialized as a string following ISO8601 format
    - remove any null property from the serialized json.
    """

    def default(self, obj: Any) -> Any:
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        internal_copy = obj.__dict__.copy()
        return {k: v for (k, v) in internal_copy.items() if v is not None}


# DecodedType = TypeVar('DecodedType')


class Connection:
    def __init__(self, api_endpoint: Optional[str] = None, allow_self_certificate=True):
        self._API_BASE_URL = format_url(api_endpoint or DEFAULT_API_ENDPOINT)
        self._request_headers: Dict[str, str] = {}
        self.verify_certificate = not allow_self_certificate
        if allow_self_certificate:
            urllib3.disable_warnings()

    @property
    def api_base_url(self) -> str:
        return self._API_BASE_URL

    def _get(self, path: str) -> Dict[str, Any]:
        self._request_headers["Content-Type"] = "application/json"
        response = requests.get(
            url=self.api_base_url + path, headers=self._request_headers, verify=self.verify_certificate
        )
        return self._response(self.api_base_url + path, response, "GET")

    def _post(self, path: str, payload: Dict[str, Any] = None, decoder=JSONDecoder, files=None) -> JsonObject:
        self._request_headers["Content-Type"] = "application/json"
        data = VecticeEncoder(indent=1).encode(payload)
        response = requests.post(
            url=self.api_base_url + path, headers=self._request_headers, data=data, verify=self.verify_certificate
        )
        return self._response(self.api_base_url + path, response, "POST", payload)

    def _put(self, path: str, payload: Any = None, decoder=JSONDecoder, cls=dict) -> Dict[str, Any]:
        self._request_headers["Content-Type"] = "application/json"
        data = VecticeEncoder().encode(payload)
        response = requests.put(
            url=self.api_base_url + path, headers=self._request_headers, data=data, verify=self.verify_certificate
        )
        return self._response(self.api_base_url + path, response, "POST", payload)

    def _response(
        self, path: str, response: Response, method: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.raise_status(path, response, method, payload)
        logger.debug(f"{method} {path} {response.status_code}")
        logger.debug("\n".join(f"{item[0]}: {item[1]}" for item in self._request_headers.items()))
        logger.debug(VecticeEncoder(indent=4, sort_keys=True).encode(payload))
        if len(response.content) > 0:
            return cast(Dict[str, Any], response.json())
        return {response.reason: response.status_code}

    @classmethod
    def raise_status(cls, path: str, response: Response, method: str, payload: Optional[Dict[str, Any]]) -> None:
        if not (200 <= response.status_code < 300):
            reason = response.text
            json = VecticeEncoder(indent=4, sort_keys=True).encode(payload) if payload is not None else None
            raise HttpError(response.status_code, reason, path, method, json)

    @classmethod
    def raise_attachment_status(cls, path: str, response: Response, method: str) -> None:
        if not (200 <= response.status_code < 300):
            reason = response.text
            raise ConnectionError(reason)

    def _post_attachments(
        self, path: str, files: Optional[List[Tuple[str, Tuple[Any, BinaryIO]]]] = None
    ) -> Optional[Response]:
        if self._request_headers.get("Content-Type"):
            self._request_headers.pop("Content-Type")
        response = requests.post(
            url=self.api_base_url + path,
            headers=self._request_headers,
            files=files,
            verify=self.verify_certificate,
        )
        return self._attachment_response(self.api_base_url + path, response, "POST")

    def _update_attachments(
        self, path: str, files: Optional[List[Tuple[str, Tuple[Any, BinaryIO]]]] = None
    ) -> Optional[Response]:
        if self._request_headers.get("Content-Type"):
            self._request_headers.pop("Content-Type")
        response = requests.put(
            url=self.api_base_url + path,
            headers=self._request_headers,
            files=files,
            verify=self.verify_certificate,
        )
        return self._attachment_response(self.api_base_url + path, response, "PUT")

    def _get_attachment(self, path: str) -> Optional[Any]:
        if self._request_headers.get("Content-Type"):
            self._request_headers.pop("Content-Type")
        response = requests.get(
            url=self.api_base_url + path, headers=self._request_headers, verify=self.verify_certificate
        )
        self._attachment_response(path=self.api_base_url + path, response=response, method="GET")
        return response

    def _delete_attachment(self, path: str) -> Optional[Response]:
        response = requests.delete(url=self.api_base_url + path, headers=self._request_headers)
        return self._attachment_response(self.api_base_url + path, response, "DELETE")

    def _list_attachments(self, path: str) -> Sequence[dict]:
        response = requests.get(
            url=self.api_base_url + path, headers=self._request_headers, verify=self.verify_certificate
        )
        self._attachment_response(self.api_base_url + path, response, "GET")
        return cast(Sequence[Dict], response.json())

    def _attachment_response(self, path: str, response: Response, method: str) -> Optional[Response]:
        self.raise_attachment_status(path, response, method)
        logger.debug(f"{method} {path} {response.status_code}")
        logger.debug("\n".join(f"{item[0]}: {item[1]}" for item in self._request_headers.items()))
        return response
