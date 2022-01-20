from .rest import KCResourceBuilder
from .oid import OpenID

class Keycloak: 
    def __init__(self, token, url):
        if not token: 
            raise Exception("No authentication token provided.")
        if not url: 
            raise Exception("No Keycloak endpoint URL has been provided.")

        self.token = token 
        self.url = url

    def admin(self):
        return KCResourceBuilder(self.url).build(self.token) 

    def build(self, resourceName, realm):
        return KCResourceBuilder(self.url).withName(resourceName).forRealm(realm).build(self.token)        

