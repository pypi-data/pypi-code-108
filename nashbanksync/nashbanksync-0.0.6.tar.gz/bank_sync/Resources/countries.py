from bank_sync.Resources.resource import Resource

class Countries(Resource):

    urls = {}

    def _set_urls(self):

        self.urls = {
            "read" : f"/countries"
        }

        super().set_urls(self.urls)

        return self
        
    def read(self,country_code = None, payload = None, method='GET',endpoint=None):
        
        self._set_urls()

        if country_code is not None:
            self.urls["read"] = f'{self.urls["read"]}/{country_code}'
            super().set_urls(self.urls)
        
        return super().read(payload, method, endpoint)