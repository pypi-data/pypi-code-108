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

    def sendWithToken(self, method, url, body={}, typeBody='form'):
        if typeBody == 'form':
            res = requests.request(method, self.Url + url, data=body, headers={"Authorization": "bearer " + self.getToken()})
        else:
            res = requests.request(method, self.Url + url, json=body, headers={"Authorization": "bearer " + self.getToken()})
        try:
            return json.loads(res.text)
        except:
            return str(res.status_code)

    def sendWithOutToken(self, method, url, body={}, typeBody='form'):
        if typeBody == 'form':
            res = requests.request(method, self.Url + url, data=body)
        else:
            res = requests.request(method, self.Url + url, json=body)

        try:
            return json.loads(res.text)
        except:
            return str(res.status_code)
