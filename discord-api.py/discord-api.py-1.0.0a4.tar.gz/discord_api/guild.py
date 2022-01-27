from .channels import TextChannel
from .role import Role
from typing import Optional

class Guild:
    """This is for easy to get a guild data.
    
    Attributes
    ----------
    name : str
        return a guild name.
    id : str
        return a guild id.
    description : str
        return a guild description.
    roles : List[Role]
        return a guild roles.
    text_channels : List[TextChannel]
        return a guild text channels
    """
    def __init__(self, client, data):
        self.name = data["name"]
        self.id = data["id"]
        self.description = data["description"]
        self.roles = [Role.from_dict(role) for role in data["roles"]]
        self.text_channels = [TextChannel.from_dict(client, i) for i in data["channels"] if i["type"] == 0]

    def get_role(self, id:int) -> Optional[Role]:
        """This can search role from guild.roles
        
        Parameters
        ----------
        id : int
            role id
            
        Returns
        -------
        Optional[Role] : Role or None
        """
        role = None
        for role in self.roles:
            if role.id == id:
                break
        return role
        
    @classmethod
    def from_dict(cls, client, data):
        self = cls(client, data)
        return self
