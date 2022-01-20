import json
import logging
import sys
from typing import Any

import requests


class RestServiceMeasures:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.auth = {'username': username, 'password': password}
        self.headers = {'User-Agent': 'python'}
        self.login()

    def login(self) -> None:
        logging.debug("Try to login to " + self.url + '/login')
        try:
            response = requests.post(self.url + '/login', data=json.dumps(self.auth), headers=self.headers, timeout=20)
        except requests.exceptions.RequestException as e:
            logging.exception("RequestException occured: " + str(e))
            sys.exit(1)

        if not response.ok:
            response.raise_for_status()
        str_response = response.content.decode('utf-8')
        logging.debug(str_response)
        if str_response:
            jwt_data = json.loads(str_response)
            jwt = jwt_data['access_jwt']
            logging.info(jwt)
            self.headers['Authorization'] = 'Bearer ' + jwt

    def get_sensors(self) -> Any:
        response = requests.get(self.url + '/sensors', headers=self.headers, timeout=10)
        logging.info(response)
        if response.ok:
            str_response = response.content.decode('utf-8')
            logging.debug(str_response)
            return json.loads(str_response)
        else:
            response.raise_for_status()

    def get_last_timestamp(self, sensor_id) -> str:
        response = requests.get(self.url + '/measures/last?sensor=' + sensor_id, headers=self.headers, timeout=10)
        if response.ok:
            str_response = response.content.decode('utf-8')
            logging.debug(str_response)
            if str_response:
                last = json.loads(str_response)
                return last['measured_at']
            return '1970-01-01 00:00'
        else:
            response.raise_for_status()

    def post_measures(self, sensor_id, measures) -> None:
        measures_data = []
        for measure in measures:
            data = {'sensor': sensor_id, 'measured_at': measure['measured_at'], 'temperature': measure['temperature'],
                    'humidity': measure['humidity']}
            measures_data.append(data)
        logging.debug('Headers:')
        logging.debug(self.headers)
        response = requests.post(self.url + '/measures', data=json.dumps(measures_data), headers=self.headers,
                                 timeout=120)
        logging.debug(response)
        if not response.ok:
            response.raise_for_status()
