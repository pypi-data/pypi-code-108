import datetime
import json
import logging
import re
import string
import sys
from enum import Enum, unique
from pathlib import Path

import requests


class RestService:
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'python', 'Accept': 'application/json'}

    def login(self):
        pass

    def logout(self):
        pass


@unique
class Response(Enum):
    OK = 0
    DUPLICATE = 2
    UNPROCESSABLE_ENTITY = 3


class RestServicePictures(RestService):
    def __init__(self, url, camera_id, client_id, client_secret, username, password):
        super().__init__(url)
        self.camera_id = camera_id
        self.auth = {'grant_type': 'password', 'client_id': client_id, 'client_secret': client_secret,
                     'username': username, 'password': password}

    def login(self) -> None:
        logging.debug("Try to login to " + self.url + '/oauth/token')
        # logging.debug(json.dumps(self.auth))
        try:
            login_headers = {'Content-Type': 'application/json'}
            response = requests.post(self.url + '/oauth/token', data=json.dumps(self.auth), headers=login_headers,
                                     timeout=20)
        except requests.exceptions.RequestException as e:
            logging.exception("RequestException occured: " + str(e))
            sys.exit(1)

        if not response.ok:
            response.raise_for_status()
        str_response = response.content.decode('utf-8')
        if str_response:
            jwt_data = json.loads(str_response)
            jwt = jwt_data['access_token']
            logging.debug(jwt)
            self.headers['Accept'] = 'application/json'
            self.headers['Authorization'] = 'Bearer ' + jwt

    def logout(self) -> None:
        logging.debug("Logging out from " + self.url + '/oauth/token')
        response = requests.delete(self.url + '/oauth/token', headers=self.headers, timeout=15)
        logging.debug(response)

    def post_picture(self, picture: str) -> Response:
        filename = Path(picture).with_suffix('').name
        picture_data = self.picture_data(filename)
        if picture_data is None:
            raise Exception('Unsupported file format ' + picture)
        logging.debug(picture_data)
        file = {'image': open(picture, 'rb')}
        response = requests.post(self.url + '/cameras/' + self.camera_id + '/pictures', files=file, data=picture_data,
                                 headers=self.headers, timeout=300)
        logging.debug(response)
        if response.ok:
            logging.info('Successfully posted picture ' + picture)
            return Response.OK
        if response.status_code == 409:
            logging.info('Picture exists already: ' + picture)
            return Response.DUPLICATE
        if response.status_code == 422:
            return Response.UNPROCESSABLE_ENTITY

        logging.error('Posting picture ' + picture + ' had an error')
        logging.error('Raw error: ' + response.text)
        str_response = response.content.decode('utf-8')
        json_data = json.loads(str_response)
        logging.error('Json error: ' + str(json_data))
        response.raise_for_status()

    def picture_data(self, filename: string) -> string:
        taken_at = self.__taken_at(filename)
        if taken_at is None:
            return None
        return {'taken_at': taken_at.strftime("%Y-%m-%d %H:%M:%S")}

    def __taken_at(self, filename: string) -> string:
        if re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{6}', filename):
            return datetime.datetime.strptime(filename, '%Y-%m-%d_%H%M%S')
        if re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}', filename):
            return datetime.datetime.strptime(filename, '%Y-%m-%d_%H%M')
        return None
