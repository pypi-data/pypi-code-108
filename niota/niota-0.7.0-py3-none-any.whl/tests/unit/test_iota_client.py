import json
import pytest
from pytest_mock import MockerFixture
import requests

from niota import exceptions
from niota.iota_client import IotaClient


class MockResponse():
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def text(self):
        return json.dumps(self.json_data)

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(response=self)


@pytest.mark.unit
def test_500_error(mocker: MockerFixture):
    iota = IotaClient(base_url='')
    mocked_get = mocker.patch(
        'requests.Session.get',
        return_value=MockResponse(
            json_data={},
            status_code=500,
        )
    )
    with pytest.raises(exceptions.NodeInternalServerError):
        iota.info()
    mocked_get.assert_called_once()
