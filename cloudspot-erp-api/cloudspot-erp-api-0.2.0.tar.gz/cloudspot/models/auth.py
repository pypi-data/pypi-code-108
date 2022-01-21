from .base import BaseModel, ObjectListModel

class AuthPermission(BaseModel):
    
    def __init__(self,
      permission=None           
    ):
        super().__init__()
        
        self.permission = permission
    
class AuthPermissions(ObjectListModel):

    def __init__(self):
        super().__init__(list=[], listObject=AuthPermission)

class AuthResponse(BaseModel):
    
    def __init__(self,
        token=None,
        permissions=None
    ):

        super().__init__()

        self.token = token
        self.permissions = permissions if permissions else AuthPermissions()