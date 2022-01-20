from .crud import KeycloakCRUD
from .helper import ValidateParams


class KeycloakCaches: 
    def __init__(self, kcCRUD, realmName):
        self.name = realmName 
        self.request_body = {'realm': self.name}
        self.kcrud = KeycloakCRUD()
        self.kcrud.token = kcCRUD.token
        self.kcrud.targets = kcCRUD.targets.copy().removeLast()

    def postTo(self, target):
        createRef =self.kcrud.targets.getCreateMethod()
        createRef.addResource(target)
        
        ret = self.kcrud.create(self.request_body)
        
        createRef.removeLast()
        return ret

    def clearUserCache(self):
        return self.postTo('clear-realm-cache')

    def clearRealmCache(self): 
        return self.postTo('clear-user-cache')

    def clearKeyCache(self):
        return self.postTo('clear-keys-cache')

class Realms(KeycloakCRUD):
    def caches(self, realmName): 
        return KeycloakCaches(self, realmName)
