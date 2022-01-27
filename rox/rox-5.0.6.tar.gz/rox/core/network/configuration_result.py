import json

class ConfigurationFetchResult(object):
    def __init__(self, data, source):
        self.source = source
        self.json_data = json.loads(data)

class ConfigurationSource:
    CDN = 'CDN'
    API = 'API'
    ROXY = 'Roxy'
