from .base import APIEndpoint

from cloudspot.models.auth import AuthResponse

class AuthMethods(APIEndpoint):

    def __init__(self, api):
        super().__init__(api, 'authenticate-external-app')
        
    def authenticate(self, username, password):
        data = { 'username' : username, 'password' : password }
        status, headers, respJson = self.api.post(self.endpoint, data)
        
        if status != 200: return AuthResponse().parseError(respJson)
        authResp = AuthResponse().parse(respJson)
        
        return authResp