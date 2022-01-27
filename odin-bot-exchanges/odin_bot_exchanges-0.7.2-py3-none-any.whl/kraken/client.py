import aiohttp
import logging
import time
import base64
import hashlib
import hmac
import urllib

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AbstractClient(ABC):

    api_key: str
    secret_key: str
    api_url: str
    exchange: str

    def __post_init__(self):
        logging.info(
            f"EXCHANGE CLIENT: Credentials for {self.exchange} are ready.")

    async def request(
        self, method: str, path: str, session: aiohttp.ClientSession, payload: dict
    ):
        try:
            timestamp = time.time()
            data = self.get_payload(payload, timestamp)
            signature = self.get_signature(
                payload=payload, endpoint=path, timestamp=timestamp
            )
            headers = self.get_headers(signature, timestamp)
            url = self.api_url + path

            async with session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
            ) as resp:
                resp.raise_for_status()
                response = await resp.json()
                return self.parse_response(response)
        except Exception as err:
            logging.debug(err)
            raise err

    async def get_public(self, path: str, session: aiohttp.ClientSession, params: dict):
        try:
            url = self.api_url + path
            async with session.get(url=url, params=params) as resp:
                url = resp.url
                response = await resp.json()
                return response
        except Exception as err:
            logging.debug(err)
            raise err

    @abstractmethod
    def get_headers(self, signature):
        pass

    @abstractmethod
    def get_signature(self, payload, endpoint):
        pass

    @abstractmethod
    def get_payload(self, payload):
        pass

    @abstractmethod
    def parse_response(self, response):
        pass


@dataclass
class KrakenClient(AbstractClient):
    exchange: str = "kraken"

    def get_headers(self, signature, *args):
        header = {
            "API-Key": self.api_key,
            "API-Sign": signature,
            "User-Agent": "Kraken REST API",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        return header

    def get_signature(self, payload, endpoint, *args, **kwarg):
        postdata = urllib.parse.urlencode(payload)
        encoded = (str(payload["nonce"]) + postdata).encode()
        message = endpoint.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(
            base64.b64decode(
                self.secret_key), message, hashlib.sha512
        )
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def get_payload(self, payload, *args, **kwargs):
        return urllib.parse.urlencode(payload)

    def parse_response(self, response):
        return response
