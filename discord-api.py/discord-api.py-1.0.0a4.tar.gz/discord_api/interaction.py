from .route import Route
from .member import Member
from .user import User

class InteractionTypePing:
    pass

class InteractionTypeCommand:
    pass

class InteractionTypeComponent:
    pass

class Interaction:
    def __init__(self, client, data):
        self.http = client.http
        self.token = data["token"]
        self.data = data.get("data")
        self.id = data["id"]
        if data.get("guild_id"):
            self.guild = client.get_guild(int(data.get("guild_id")))
            self.author = Member.from_dict(client, self.guild, data["member"]["user"])
        else:
            self.guild = None
            self.author = User.from_dict(client, data["user"])

    @property
    def type(self):
        if self.data["type"] == 1:
            return InteractionTypePing
        elif self.data["type"] == 2:
            return InteractionTypeCommand
        elif self.data["type"] == 3:
            return InteractionTypeComponent

    async def send(self, content:str = None, ephemeral:bool = False):
        payload = {}
        if content is not None:
            payload["content"] = content
        if ephemeral:
            payload["flags"] = 64
        await self.http.slash_callback(self, payload = payload)
        
    @classmethod
    def from_dict(cls, client, data):
        self = cls(client, data)
        return self