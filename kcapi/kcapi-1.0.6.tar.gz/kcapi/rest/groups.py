from .crud import KeycloakCRUD
from .helper import ValidateParams
from .resp import ResponseHandler
import json, requests



class GroupAndRolesMappingBuilder(): 
    roles = None
    def build(self, groupName, groups): 
        token = groups.token
        targets = groups.targets

        self.roles = self._load(token, targets, KeycloakCRUD)
        self.rolesMappings = self._load(token, targets, KeycloakCRUD)

        self.rolesMappings = self._initGroupMappingAPI(groupName, self.rolesMappings) 
        self.roles.targets.change('roles')

        self.rolesMappings.add = self.add
        self.rolesMappings.__fetchRoles = self.__fetchRoles
        self.rolesMappings.remove = self.remove

        return self.rolesMappings

    
    def _load(self, token, targets, API):
        api = API()
        api.token = token
        api.targets = targets.copy()

        return api

    def _initGroupMappingAPI(self, groupName, groupAPI):
        groupID = groupAPI.findFirst(groupName)['id']
        groupAPI.targets.addResources([groupID, 'role-mappings', 'realm'])
        return groupAPI

    def __fetchRoles(self, roles): 
        find = self.roles.findFirstByKV
        return list( map(lambda name: find('name', name), roles) )

    def add(self, roles): 
        populatedListOfRoles = self.__fetchRoles(roles)
        return self.rolesMappings.create(populatedListOfRoles)

    # Another example of Keycloak not using standard REST behaviour.
    # Overriding remove from CRUD
    def remove(self, roles): 
        populatedListOfRoles = self.__fetchRoles(roles)
        remove_target = self.rolesMappings.targets.url('delete')
        headers = self.rolesMappings.getHeaders()

        ret = requests.delete(remove_target, data=json.dumps(populatedListOfRoles), headers=headers )
        return ResponseHandler(remove_target).handleResponse(ret)

class Groups(KeycloakCRUD): 
    def realmRoles(self, group):
        return GroupAndRolesMappingBuilder().build(group, self)



