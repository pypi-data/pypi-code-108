import json
import ipfsApi

import requests

from DecenTT.IPFS.IPFSExceptions import *
from DecenTT.IPFS.locales import getIPFSHost
from DecenTT.IPFS.config import ENDPOINTS
from requests import post
from urllib.parse import urlencode
from DecenTT.IPFS.threader import ThreadDecorator, ProcessDecorator
from DecenTT.IPFS.standard import IPFSResponse

from DecenTT.env.config import DEFAULT_HOST


class Client:
    """
    >>> c = Client()
    >>> c.publish("abc", "Hello Worlds!!!")
    <Response [200]>
    """

    # Subscription Class:
    class Subscription:
        def __init__(self, topic: str, callback, client, host: str = DEFAULT_HOST, **kwargs):
            self.host = host
            self.topic = topic
            self.client = client
            if (not 'function' in str(type(callback))) or callback is None:
                raise InvalidCallback(callback=callback)
            else:
                self.__callback = callback
                self.thread = self.__run(topic=self.topic, callback=self.__callback)

        #@ThreadDecorator.thread
        @ProcessDecorator.thread
        def __callback_thread(self, resp: requests.Response, callback) -> None:
            for line in resp.iter_lines(decode_unicode=True):
                payload = json.loads(line)

                """
                    Match the standards of MQTT here
                        arg1: client : ipfsApi.Client
                        arg2: userdata : from JSON response of IPFS HTTP API
                        arg3: msg : from JSON 
                """
                ipfs_resp = IPFSResponse(in_dict=payload)
                __client = self.client
                __usrdata = ipfs_resp.userdata
                __msg = ipfs_resp.msg

                callback(__client, __usrdata, __msg)

        def __run(self, topic: str, callback):
            """
                Refer to IPFS HTTP API Docs: https://docs.ipfs.io/reference/http/api/#api-v0-pubsub-sub
            """

            ep = ENDPOINTS["pubsub"]["sub"]
            args = [
                ("arg", topic),
                # ("discover", None)                # Deprecated
            ]
            url = f"http://{self.host}{ep}?{urlencode(args)}"

            # Create Request to: IPFS HTTP API
            resp = post(url=url, stream=True)
            # Check for Encoding
            if resp.encoding is None:
                resp.encoding = 'utf-8'

            return self.__callback_thread(resp, callback)

        def close(self):
            del self

    def __init__(self) -> None:
        self.host = getIPFSHost()
        self.host_address = self.host.split(":")[0]
        self.host_port = int(self.host.split(":")[1])
        self.ipfs_client = ipfsApi.Client(self.host_address, self.host_port)

    def subscribe(self, topic: any, callback, **kwargs):
        if not (isinstance(topic, list) or isinstance(topic, str)):
            raise TopicIncompatibleType
        if isinstance(topic, list):
            return [self.Subscription(topic=t_i, callback=callback, client=self) for t_i in list(topic)]
        return self.Subscription(topic=topic, callback=callback, client=self)

    def publish(self, topic: str, payload: str, **kwargs) -> None:
        """
            Refer to IPFS HTTP API Docs: https://docs.ipfs.io/reference/http/api/#api-v0-pubsub-pub
        """
        ep = ENDPOINTS["pubsub"]["pub"]

        args = [
            ("arg", topic),
            ("arg", payload)
        ]

        url = f"http://{self.host}{ep}?{urlencode(args)}"

        resp = post(url=url)

        if resp.status_code == 200 and resp.reason == "OK":
            return resp

        resp.raise_for_status()
