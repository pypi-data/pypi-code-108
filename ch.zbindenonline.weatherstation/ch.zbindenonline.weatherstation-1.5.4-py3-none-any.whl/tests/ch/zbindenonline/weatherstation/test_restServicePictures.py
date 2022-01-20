import json
import os
import shutil
import tempfile
import unittest
import pytest
from unittest import mock
from requests.models import Response as HttpResponse, HTTPError


from ch.zbindenonline.weatherstation.restServicePictures import RestServicePictures, Response


def mocked_requests_post(*args, **kwargs):
    class ResponseContent:
        def __init__(self, json_data):
            self.json_data = json_data

        def decode(self, utf):
            return json.dumps(self.json_data)

    class MockResponse:
        def __init__(self, json_data, status_code, ok):
            self.status_code = status_code
            self.ok = ok
            self.content = ResponseContent(json_data)
            self.text = 'error'

    if args[0] == 'http://testurl/oauth/token':
        return MockResponse({"access_token": "accessTokenToTest"}, 200, True)
    elif args[0] == 'http://testurl/cameras/3/pictures':
        return MockResponse({"key2": "value2"}, 200, True)
    elif args[0] == 'http://testurl/cameras/4/pictures':
        return MockResponse({"key2": "value2"}, 409, False)
    elif args[0] == 'http://testurl/cameras/5/pictures':
        return MockResponse({"key2": "value2"}, 422, False)
    elif args[0] == 'http://testurl/cameras/6/pictures':
        the_response = HttpResponse()
        the_response.status_code = 404
        the_response._content = b'{ "error" : "error text" }'
        return the_response
    return MockResponse({"error": "error"}, 404, False)


class RestServiceShould(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_answerOk(self, mock_post):
        picture = os.path.join(self.test_dir, '2021-04-11_112400.jpg')
        f = open(picture, 'w')
        f.write('The owls are not what they seem')
        f.close()
        service = RestServicePictures('http://testurl',
                                      '3',
                                      'client_id',
                                      'client_secret',
                                      'testuser',
                                      'testpwd')

        service.login()
        self.assertRegex(service.headers['Authorization'], "Bearer accessTokenToTest")

        result = service.post_picture(picture)
        self.assertEqual(Response.OK, result)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_answerRaisesErrorWhenInvalidFile(self, mock_post):
        picture = os.path.join(self.test_dir, '2021-04-11.jpg')
        f = open(picture, 'w')
        f.write('The owls are not what they seem')
        f.close()
        service = RestServicePictures('http://testurl',
                                      '3',
                                      'client_id',
                                      'client_secret',
                                      'testuser',
                                      'testpwd')

        service.login()
        with pytest.raises(Exception) as error_info:
            service.post_picture(picture)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_answerOkWithoutSeconds(self, mock_post):
        picture = os.path.join(self.test_dir, '2021-04-11_1124.jpg')
        f = open(picture, 'w')
        f.write('The owls are not what they seem')
        f.close()
        service = RestServicePictures('http://testurl',
                                      '3',
                                      'client_id',
                                      'client_secret',
                                      'testuser',
                                      'testpwd')

        service.login()
        self.assertRegex(service.headers['Authorization'], "Bearer accessTokenToTest")

        result = service.post_picture(picture)
        self.assertEqual(Response.OK, result)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_answerDuplicate(self, mock_post):
        picture = os.path.join(self.test_dir, '2021-04-11_112400.jpg')
        f = open(picture, 'w')
        f.write('The owls are not what they seem')
        f.close()
        service = RestServicePictures('http://testurl',
                                      '4',
                                      'client_id',
                                      'client_secret',
                                      'testuser',
                                      'testpwd')

        result = service.post_picture(picture)

        self.assertEqual(Response.DUPLICATE, result)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_answerUnprocessable(self, mock_post):
        picture = os.path.join(self.test_dir, '2021-04-11_112400.jpg')
        f = open(picture, 'w')
        f.write('The owls are not what they seem')
        f.close()
        service = RestServicePictures('http://testurl',
                                      '5',
                                      'client_id',
                                      'client_secret',
                                      'testuser',
                                      'testpwd')

        result = service.post_picture(picture)

        self.assertEqual(Response.UNPROCESSABLE_ENTITY, result)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_answerResponseRaiseForStatus(self, mock_post):
        picture = os.path.join(self.test_dir, '2021-04-11_112400.jpg')
        f = open(picture, 'w')
        f.write('The owls are not what they seem')
        f.close()
        service = RestServicePictures('http://testurl',
                                      '6',
                                      'client_id',
                                      'client_secret',
                                      'testuser',
                                      'testpwd')
        with pytest.raises(HTTPError) as error_info:
            service.post_picture(picture)


if __name__ == '__main__':
    unittest.main()
