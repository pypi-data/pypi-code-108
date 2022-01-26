import json
from types import SimpleNamespace

import requests

from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.domain.Search import Search
from ikologikapi.services.AbstractIkologikService import AbstractIkologikService


class AbstractIkologikCustomerService(AbstractIkologikService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer: str):
        pass

    def get_by_id(self, customer: str, id: str) -> object:
        try:
            response = requests.get(
                self.get_url(customer) + f'/{id}',
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.HTTPError as error:
            print(error)

    def list(self, customer: str) -> list:
        try:
            response = requests.get(
                self.get_url(customer),
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.HTTPError as error:
            print(error)

    def search(self, customer: str, search: Search) -> list:
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

    def create(self, customer: str, o: object) -> object:
        try:
            data = json.dumps(o, default=lambda o: o.__dict__)
            response = requests.post(
                self.get_url(customer),
                data=data,
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.HTTPError as error:
            print(error)

    def update(self, customer: str, id: str, o: object) -> object:
        try:
            data = json.dumps(o, default=lambda o: o.__dict__)
            response = requests.put(
                f'{self.get_url(customer)}/{id}',
                data=data,
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.HTTPError as error:
            print(error)

    def delete(self, customer: str, id: str):
        try:
            response = requests.delete(
                f'{self.get_url(customer)}/{id}',
                headers=self.get_headers()
            )
        except requests.exceptions.HTTPError as error:
            print(error)
