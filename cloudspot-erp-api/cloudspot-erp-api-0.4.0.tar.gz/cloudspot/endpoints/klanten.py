from .base import APIEndpoint

from cloudspot.models.klanten import Klanten

class KlantenMethods(APIEndpoint):

    def __init__(self, api):
        super().__init__(api, 'klanten')
        
    def list(self, fields=None):
        data = None
        status, headers, respJson = self.api.get(self.endpoint, data)
        
        if status != 200: return Klanten().parseError(respJson)
        artikels = Klanten().parse(respJson['data'])
        
        return artikels