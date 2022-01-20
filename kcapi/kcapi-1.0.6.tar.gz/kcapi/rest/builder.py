from .crud import KeycloakCRUD
from .targets import Targets
from .groups import Groups
from .roles import RolesURLBuilder   
from .users import Users   
from .realms import Realms
from .url import RestURL
from .idp import IdentityProviderURLBuilder
from .auth_flows import AuthenticationFlows, AuthenticationFlowURLBuilder

KCResourceTypes = {
        "users": Users, 
        "groups": Groups, 
        "realms": Realms,
        "authentication": AuthenticationFlows 
}

URLBuilders = {
    'roles': RolesURLBuilder,
    'authentication': AuthenticationFlowURLBuilder,
    "idp": IdentityProviderURLBuilder,
    "identity-provider": IdentityProviderURLBuilder
}

def GenericURLBuilder(url):
     targets = Targets.makeWithURL(url)
     return targets 



class KCResourceBuilder:
    def __URLSetup(self, url):
        return RestURL(url=url, resources=["auth", "admin", "realms"])
    
    def __init__(self, keycloakURL):
        self.name = None
        self.realm = None
        self.url = self.__URLSetup(keycloakURL) 

    def withName(self, name):
        self.name = name
        return self

    def forRealm(self, realm): 
        self.realm = realm
        return self

    def build(self, token):
        KCResourceAPI = KeycloakCRUD if not self.name in KCResourceTypes else KCResourceTypes[self.name]  
        URLBuilder = GenericURLBuilder if not self.name in URLBuilders else URLBuilders[self.name]

        self.url.addResources([self.realm, self.name])

        resource = KCResourceAPI() 
        resource.targets = URLBuilder(str(self.url))
        resource.token = token


        return resource 

