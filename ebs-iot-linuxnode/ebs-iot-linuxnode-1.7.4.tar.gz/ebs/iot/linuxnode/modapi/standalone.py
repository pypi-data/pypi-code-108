

from twisted.internet.defer import inlineCallbacks
import treq


class StandaloneActual(object):
    @inlineCallbacks
    def http_get(self, url, **kwargs):
        d = yield treq.request('get', url, **kwargs)
        return d

    @inlineCallbacks
    def http_post(self, url, **kwargs):
        response = yield treq.post(url, **kwargs)
        data = yield response.json()
        return data


class StandaloneConfig(object):
    def __init__(self, *args, **kwargs):
        pass
