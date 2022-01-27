from types import SimpleNamespace

import requests
import json
from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.domain.Search import Search
from ikologikapi.services.AbstractIkologikCustomerService import AbstractIkologikCustomerService


class InstallationService(AbstractIkologikCustomerService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer: str):
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation'

    def search(self, customer: str, search) -> list:
        try:
            data = json.dumps(search, default=lambda o: o.__dict__)
            response = requests.post(
                f'{self.get_url(customer)}/search',
                data=data,
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.HTTPError as error:
            print(error)