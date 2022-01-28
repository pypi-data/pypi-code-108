from multiprocessing.sharedctypes import Value

from cloudspot.constants.errors import NoValidToken
from .base import APIEndpoint

from cloudspot.models.auth import AuthResponse, PermissionsResponse, User

class AuthMethods(APIEndpoint):

    def __init__(self, api):
        super().__init__(api, 'auth')
        
    def authenticate(self, username, password):
        endpoint = '{0}/{1}'.format(self.endpoint, 'signin-external-app')
        data = { 'username' : username, 'password' : password }
        
        status, headers, resp_json = self.api.post(endpoint, data)
        
        if status != 200: return AuthResponse().parseError(resp_json)
        authResp = AuthResponse().parse(resp_json)
        
        return authResp
    
    def get_permissions(self):
        if not self.api.token: raise NoValidToken('No token found. Authenticate the user first to retrieve a token or supply a token to the function.')
        
        endpoint = '{0}/{1}'.format(self.endpoint, 'get-permissions')
        data = None
        
        status, headers, resp_json = self.api.get(endpoint, data)
        
        if status != 200: return PermissionsResponse().parseError(resp_json)
        permission_resp = PermissionsResponse().parse(resp_json)
        
        return permission_resp
    
    def get_user(self):
        if not self.api.token: raise NoValidToken('No token found. Authenticate the user first to retrieve a token or supply a token to the function.')
        
        endpoint = '{0}/{1}'.format(self.endpoint, 'get-user')
        data = None
        
        status, headers, resp_json = self.api.get(endpoint, data)
        
        if status != 200: return User().parseError(resp_json)
        user_resp = User().parse(resp_json)
        
        return user_resp