from .crud import KeycloakCRUD

class UserAndGroupRelation:
    def __init__(self, userAPI, groupAPI, endpoint): 
        self.endpoint = endpoint
        self.users = userAPI 
        self.groups = groupAPI 

    def join(self, user, group):
        endpoint = self.endpoint.copy()

        user = self.users.findFirstByKV(user['key'], user['value'])
        group = self.groups.findFirstByKV(group['key'], group['value'])
    
        user_id = user['id']
        group_id = group['id']

        endpoint.addResources(['users'])



        return 1
        
