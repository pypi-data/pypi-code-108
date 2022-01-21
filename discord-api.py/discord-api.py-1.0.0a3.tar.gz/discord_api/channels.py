from .embed import Embed

class TextChannel:
    def __init__(self, client, data):
        self.id = data["id"]
        self.name = data["name"]
        self.http = client.http

    async def send(self, content = None, embeds:Embed = None):
        payload = {}
        if payload is not None:
            payload["content"] = content
        if embeds is not None:
            payload["embeds"] = [embed.to_dict() for embed in embeds]
        await self.http.send_message(self.id, payload)
        
    @classmethod
    def from_dict(cls, client, data):
        return cls(client, data)