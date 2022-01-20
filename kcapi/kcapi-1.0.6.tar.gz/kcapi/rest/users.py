from .crud import KeycloakCRUD
from .helper import ValidateParams


class Users(KeycloakCRUD):
    def __lazy_load_groups(self):
        groups = KeycloakCRUD() 
        groups.token = self.token
        groups.targets = self.targets.copy()
        groups.targets.change('groups')

        return groups

    def __findGroup(self, group): 
        groups = self.__lazy_load_groups()
        return groups.findFirst(group)

    def __userGroupMappingAPI(self, userID): 
        kc = KeycloakCRUD() 
        kc.token = self.token
        kc.targets = self.targets.copy()

        kc.targets.addResources([userID, 'groups'])
        return kc

    def joinGroup(self, user, group): 
        userID = self.findFirst(user)['id']
        groupID = self.__findGroup(group)['id']

        requestBody = {'groupId': groupID, 'userId': userID} 

        return self.__userGroupMappingAPI(userID).update(groupID, requestBody)

    def groups(self, user):
        userID = super().findFirst(user)['id']
        return self.__userGroupMappingAPI(userID).all()

    def leaveGroup(self, user, group):
        userID  = super().findFirst(user)['id']
        groupID = self.__findGroup(group)['id']

        return self.__userGroupMappingAPI(userID).remove(groupID)

    def groupMapping(self, user):
        userID = self.findFirst(user)['id']
        return self.__userGroupMappingAPI(userID)

    # 
    # credentials: {type: "password", value: "passphrases", temporary: true} 
    # type: **password** Is the credential type supported by Keycloak.
    # value: Here we put the passphrase (required) 
    # temporary: **true** Means that this password would works the first time but it will force the user to setup a new one. 
    def updateCredentials(self, user, credentials):

        params = {"type": "password", "temporary":True}
        userID = super().findFirst(user)['id']
        
        params.update(credentials)
        ValidateParams(['type', 'value', 'temporary'],params)
        
        credentials = KeycloakCRUD()
        credentials.token = self.token 
        credentials.targets = self.targets.addResourcesFor('update', [userID, 'reset-password'])

        return credentials.update('', params)


