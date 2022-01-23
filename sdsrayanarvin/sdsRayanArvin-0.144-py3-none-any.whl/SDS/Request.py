import json

import requests

from sdsRayanArvin.Cache import Cache
from sdsRayanArvin.Token import Token


class Request(Token, Cache):

    def __init__(self, URL):
        super().__init__()
        Cache.__init__(self)
        Token.__init__(self)
        self.Url = URL

    def sendWithToken(self, method, url, body={}):
        res = requests.request(method, self.Url + url, data=body, headers={"Authorization": "bearer " + self.getToken()})
        return json.loads(res.text)

    def sendWithOutToken(self, method, url, body={}):
        res = requests.request(method, self.Url + url, data=body)
        return json.loads(res.text)
