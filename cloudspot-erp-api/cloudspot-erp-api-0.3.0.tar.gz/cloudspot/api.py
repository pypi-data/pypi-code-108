import base64
import requests
import json

from cloudspot.models.auth import AuthPermissions

from . import config
from .authhandler import AuthHandler
from cloudspot.endpoints.auth import AuthMethods
from cloudspot.endpoints.artikels import ArtikelMethods
from cloudspot.endpoints.klanten import KlantenMethods
from cloudspot.constants.errors import BadCredentials

class CloudspotERP_API:

    def __init__(self):
        self.baseUrl = config.BASE_URL
        self.headers = { 'Content-Type' : 'application/json' }
        self.authHandler = AuthHandler()
        
        self.auth = AuthMethods(self)
    
    def setTokenHeader(self, token):
        self.token = token
        self.headers.update({'X-ERP-TOKEN' : self.token})
    
    def checkHeaderTokens(self):
        pass

    def doRequest(self, method, url, data=None, headers=None):
        
        if headers:
            mergedHeaders = self.headers.copy()
            mergedHeaders.update(headers)
            headers = mergedHeaders
        else: headers = self.headers

        reqUrl = '{base}/{url}/'.format(base=self.baseUrl, url=url)

        if method == 'GET':
            response = requests.get(reqUrl, params=data, headers=headers)
        elif method == 'POST':
            response = requests.post(reqUrl, data=json.dumps(data), headers=headers)
        elif method == 'PUT':
            response = requests.put(reqUrl, data=json.dumps(data), headers=headers)
        
        return response


    def request(self, method, url, data=None, headers=None):
        
        # Check the headers for appropriate tokens before we make a request
        self.checkHeaderTokens()

        # Make the request
        response = self.doRequest(method, url, data, headers)
        respContent = response.json()
        
        return response.status_code, response.headers, respContent
    
    def get(self, url, data=None, headers=None):
        status, headers, response = self.request('GET', url, data, headers)
        return status, headers, response
    
    def post(self, url, data=None, headers=None):
        status, headers, response = self.request('POST', url, data, headers)
        return status, headers, response
    
    def put(self, url, data=None, headers=None):
        status, headers, response = self.request('PUT', url, data, headers)
        return status, headers, response


class CloudspotERP_CompanyAPI(CloudspotERP_API):
    
    def __init__(self, token):
        super().__init__()
        self.token = token
        
        self.artikels = ArtikelMethods(self)
        self.klanten = KlantenMethods(self)
    
    def checkHeaderTokens(self):
        if 'X-ERP-TOKEN' not in self.headers:
            self.headers.update({'X-ERP-TOKEN' : self.token})
    

class CloudspotERP_UserAPI(CloudspotERP_API):
    
    def __init__(self, requestor, token=None):
        super().__init__()
        self.token = token
        self.requestor = requestor.lower()
        
        self.headers.update({'X-ERP-REQUESTOR' : self.requestor })
        self.permissions = AuthPermissions()
    
    def checkHeaderTokens(self):
        if 'X-ERP-TOKEN' not in self.headers and self.token:
            self.headers.update({'X-ERP-TOKEN' : self.token})
        if 'X-ERP-REQUESTOR' not in self.headers:
            self.headers.update({'X-ERP-REQUESTOR' : self.requestor })
            
    def authenticate(self, username, password):
        
        authResp = self.auth.authenticate(username, password)
        if authResp.hasError: raise BadCredentials('Username or password not correct.')
        
        self.permissions = authResp.permissions
        self.setTokenHeader(authResp.token)