import json
import unittest
import pytest

import requests
from mockito import unstub, when, mock, verify, arg_that

from ch.zbindenonline.weatherstation.restServiceMeasures import RestServiceMeasures


class ResponseContent:
    def __init__(self, json_data):
        self.json_data = json_data

    def decode(self, utf):
        return json.dumps(self.json_data)


class MockResponse:

    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self.ok = (200 == status_code)
        self.content = ResponseContent(data)


class RestServiceMeasuresShould(unittest.TestCase):

    def tearDown(self):
        unstub()

    def test_login_fails(self):
        when(requests).post('http://testurl/login', data=any, headers=any, timeout=any).thenReturn(MockResponse(404))

        with pytest.raises(Exception):
            RestServiceMeasures('http://testurl', 'testuser', 'testpwd')

    def test_login_ok(self):
        when(requests).post('http://testurl/login', data=any, headers=any, timeout=any).thenReturn(
            MockResponse(data={"access_jwt": "access_token"}))

        service = RestServiceMeasures('http://testurl', 'testuser', 'testpwd')

        self.assertEquals('Bearer access_token', service.headers['Authorization'])

    def test_get_sensors(self):
        service = login()
        service_sensors = [{'id': 1, 'name': 'sensor_1'}, {'id': 2, 'name': 'sensor_2'}]
        when(requests).get('http://testurl/sensors', headers=any, timeout=10).thenReturn(
            MockResponse(data=service_sensors))

        sensors = service.get_sensors()

        self.assertEquals(service_sensors, sensors)

    def test_get_last_timestamp(self):
        service_timestamp = '2021-12-20 14:59'
        when(requests).get('http://testurl/measures/last?sensor=17', headers=any, timeout=10).thenReturn(
            MockResponse(data={'measured_at': service_timestamp}))
        service = login()

        timestamp = service.get_last_timestamp('17')

        self.assertEquals(service_timestamp, timestamp)

    def test_post_measures(self):
        measures = [{'measured_at': '2021-12-20 08:00', 'temperature': '19.7', 'humidity': '67.3'}]
        service = login()
        when(requests) \
            .post('http://testurl/measures',
                  data=arg_that(lambda posted: self.verify_measures('23', measures, json.loads(posted))),
                  headers={'User-Agent': 'python', 'Authorization': 'Bearer access_token'}, timeout=120) \
            .thenReturn(MockResponse(200))

        service.post_measures('23', measures)

    def verify_measures(self, sensor_id, expected, posted):
        return len(expected) == len(posted) and \
               sensor_id == posted[0]['sensor'] and \
               expected[0]['measured_at'] == posted[0]['measured_at'] and \
               expected[0]['temperature'] == posted[0]['temperature'] and \
               expected[0]['humidity'] == posted[0]['humidity']



def login() -> RestServiceMeasures:
    when(requests).post('http://testurl/login', data=any, headers=any, timeout=any).thenReturn(
        MockResponse(data={"access_jwt": "access_token"}))
    return RestServiceMeasures('http://testurl', 'testuser', 'testpwd')


if __name__ == '__main__':
    unittest.main()
