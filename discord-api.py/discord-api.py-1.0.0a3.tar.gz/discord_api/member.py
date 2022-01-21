from .role import Role

class Member:
    def __init__(self, client, guild, user:dict):
        self.client = client
        self.guild = guild
        self.name = user["username"]
        self.id = user["id"]
        self.discriminator = user["discriminator"]
        self.avatar = user["avatar"]

    async def add_role(self, role:Role):
        await self.client.http.add_role(self, role)

    @classmethod
    def from_dict(cls, client, guild, data):
        return cls(client, guild, data)
