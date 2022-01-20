import requests, json
from .rest import RestURL

class OpenID: 
   def __check_params(self, params):
        expected_params = ['password', 'username', 'grant_type', 'client_id'] 
        
        for param in expected_params: 
            if param not in params:
                raise Exception("Missing parameter on OpenId class: ", param)

   @staticmethod
   def __raise_error(resp, url):
        code = resp.status_code

        if code in [404]: 
            raise Exception("Server Error: " + str(code), resp.text, " URL: ", str(url))

        if code in [503, 500]: 
            raise Exception("Server Error: " + str(code), " URL: ", str(url))

        if code == 401:
            raise Exception("Server returned 401: Unauthorized. Please check username or password.")

        json_data = resp.json()
        error_message = json_data["error"] + "--" + json_data["error_description"] 
        raise Exception("Error: " + str(code) + " \n for URL:" + str(url) + " \n Response: " +  error_message)

   # Retrieves the Well Known Endpoint: https://openid.net/specs/openid-connect-discovery-1_0.html 
   @staticmethod
   def discover(url, realm): 
        discovery_url = RestURL(url, ['auth', 'realms', realm, '.well-known', 'openid-configuration'])

        resp = requests.get(url=str(discovery_url))

        if resp.status_code == 200: 
            return resp.json()

        OpenID.__raise_error(resp, discovery_url)

   def __init__(self, credentials, url = None):
        self.__check_params(credentials)

        self.credentials = credentials 
        self.realm = self.credentials['realm']
        self.token = None

        if url: 
            self.urlObject = url 


   @staticmethod 
   def createAdminClient(username, password): 
        __props = {
            "client_id": "admin-cli",
            "grant_type":"password",
            "realm" : "master", 
            "username": username,
            "password": password
        }

        return OpenID(__props)

   def getToken(self, target_url = None):
        url = target_url if target_url else self.urlObject

        token_endpoint = OpenID.discover(url, self.realm)['token_endpoint']

        resp = requests.post(token_endpoint, data=self.credentials)

        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            return self.token
        else:
            OpenID.__raise_error(resp, url)


