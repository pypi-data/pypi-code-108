import json
import requests

# This is a class that is designed to include all methods and functions one needs to make an A.P.I. call
class API(object):

    _base_url = "http://nashsync-bankcore.nashglobal.co/api/banks"

    # Most API calls require headers, params and payloads
    _headers = None
    _params = None
    _payload = None

    # You always expect a response from A.P.I. calls
    _response = {}

    # When using this class to create an A.P.I. class, each API should have an optional name and code
    # but must have headers and any required parameters
    def __init__(self, name=None, headers=None, params=None, code=None):
        self._name = name
        self._code = code

        self._headers = headers
        self._params = params

        requests.packages.urllib3.disable_warnings()

    # There are 3 types of API requests that most APIs use, POST, GET and PUT
    # This method will take the payload or data to be sent and send it to the required API url
    # using the desired method and returns the response
    def api_request(self, url, payload, method, verify = False, files = None):
        
        if payload == "null":
            self._payload=json.dumps({})
        else:
            self._payload = payload
        
        try:
            if method == 'POST':
                self._response = requests.post(url, headers=self._headers, params=self._params,
                                           data=self._payload, json=self._payload, verify=verify,files=files)
            elif method == 'PUT':
                self._response = requests.put(url, headers=self._headers, params=self._params,
                                           data=self._payload, json=self._payload, verify=verify)
            elif method == 'GET':
                self._response = requests.get(url, headers=self._headers, params=self._params,
                                           data=self._payload, json=self._payload, verify=verify)
            elif method == 'DELETE':
                self._response = requests.delete(url, headers=self._headers, params=self._params,
                                           data=self._payload, json=self._payload, verify=verify)

            try:
                self._response = json.loads(self._response.text)
            except ValueError as e:
                self._response = self._response.text

        except Exception as e:
            self._response['error'] = 'Internal Server Error'
            print(e)
        finally:
            return self._response

    # Method used to get the repsonse returned by an API instead of calling the API again
    def get_response(self):
        return self._response

    def set_headers(self, headers):
        self._headers = headers
        return self

    def get_headers(self):
        return self._headers

    def set_params(self, params):
        self._params = params
        return self

    def get_params(self):
        return self._params

    def get_payload(self):
        return self._payload

    def get_base_url(self):
        return self._base_url