from bank_sync.Resources.resource import Resource
from bank_sync.Resources.countries import Countries
from bank_sync.Resources.accounts import Accounts
from bank_sync.Resources.payments import Payments


class Bank(Resource):

    _resources = {
        "Countries": Countries(),
        "Accounts": Accounts(),
        "Payments": Payments(),
    }

    # use the nash object to confirm if the user accessing the banks is logged in
    _nash = None

    urls = {}

    def __init__(self, nash, bank_id=None):
        self._nash = nash
        super().__init__("BankAPI", self._nash.get_headers(), self._nash.get_params())
        super().set_bank_id(bank_id)
        self._set_urls()

    def resource(self, resource_name):
        resource = self._resources[resource_name].set_bank_id(super().get_bank_id()).set_headers(self._nash.get_headers())

        return resource

    def get_resources(self):
        return list(self._resources.keys())

    def _set_urls(self):

        self.urls = {
            "read": f"/banks",
        }

        super().set_urls(self.urls)

        return self
        
    def read(self,bank_id = None, payload = None, method='GET',endpoint=None):
        
        self._set_urls()

        if bank_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{bank_id}'
            super().set_urls(self.urls)

        elif super().get_bank_id() is not None:
            self.urls["read"] = f'{self.urls["read"]}/{super().get_bank_id()}'
            super().set_urls(self.urls)
        
        return super().read(payload, method, endpoint)

    def sample_payload(self, bank_id=None, payload=None, method='GET', endpoint='/sample_payload'):

        if bank_id is not None:
            endpoint = f'{endpoint}/{bank_id}'

        return super().read(payload, method, endpoint)

    def callback(self, bank_name=None, payload=None, method='POST', endpoint='/callback'):

        if bank_name is not None:
            endpoint = f'{endpoint}/{bank_name}'

        return super().read(payload, method, endpoint)
    
    def bank_types(self):
        
        self._set_urls()

        return super().read(method='GET')
