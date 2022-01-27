from types import SimpleNamespace
import json
import requests

from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.services.AbstractIkologikInstallationService import AbstractIkologikInstallationService


class ReportService(AbstractIkologikInstallationService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer: str, installation: str, report_type: str):
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation/{installation}/reporttype/{report_type}/report'

    def create(self, customer: str, installation: str, report_type: str, o: object) -> object:
        try:
            data = json.dumps(o, default=lambda o: o.__dict__)
            response = requests.post(
                self.get_url(customer, installation, report_type),
                data=data,
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.HTTPError as error:
            print(error)

    def build(self, customer: str, installation: str, report_type: str) -> object:
        try:
            response = requests.get(
                f'{self.get_url(customer, installation, report_type)}/build',
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.HTTPError as error:
            print(error)

    def updateStatus (self, customer:str, installation: str, report_type: str, report_id: str, status: str) -> object:
        try:
            response = requests.put(
                f'{self.get_url(customer, installation, report_type)}/{report_id}/status',
                data=status,
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.HTTPError as error:
            print(error)

    def upload (self, customer: str, installation:str, report_type:str, report_id: str, filename: str, content_type: str) -> object:
        try:
            params = {'filename': filename, 'contentType': content_type}
            response = requests.get(
                f'{self.get_url(customer, installation, report_type)}/{report_id}/upload',
                params=params,
                headers=self.get_headers()
            )
            result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return result
        except requests.exceptions.RequestException as error:
            print(error)
            raise requests.exceptions.RequestException(f'Failed to create the uploadurl for {report_id}')