from discord_api_types import HttpClient

class Route:
    def __init__(self, method, path):
        self.method = method
        self.path = path

class DiscordRequest(HttpClient):
    def __init__(self, client):
        super().__init__(client.loop)

    def _token(self, token):
        self.token = token

    async def get_ws_url(self):
        data = await self.request(Route("GET", "/gateway"))
        return data["url"]

    async def request(self, route:Route, *args, **kwargs):
        return await super().request(route.method, route.path, *args, **kwargs)

    async def static_login(self):
        data = await self.request(Route("GET", "/users/@me"))
        return data

    async def send_message(self, channelid, payload):
        await self.request(Route("POST", f"/channels/{channelid}/messages"), json = payload)

    async def slash_callback(self, interaction, payload):
        json = {
            "type": 4,
            "data": payload
        }
        return await self.request(Route("POST", f"/interactions/{interaction.id}/{interaction.token}/callback"), json = json)

    async def fetch_commands(self):
        return await self.request(Route("GET", f"/applications/{self.client.user.id}/commands"))

    async def add_command(self, command:Command):
        await self.request(Route("POST", f"/applications/{self.client.user.id}/commands"), json = command.to_dict())
        
    async def add_role(self, member:Member, role:Role):
        await self.request(Route("PUT", f"/guilds/{member.guild.id}/members/{member.id}/roles/{role.id}"))

    async def delete_command(self, cmdid):
        await self.request(Route("DELETE", f"/applications/{self.client.user.id}/commands/{cmdid}"))
