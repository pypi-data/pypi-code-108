from httpx import AsyncClient


class HTTPClient(AsyncClient):
    def __init__(self, application_id, token):
        super().__init__()

        self.application_id = application_id
        self.token = token

        self.base_url = "https://discord.com/api/v8"
        self.headers = {"Authorization": f"Bot {self.token}"}

    # https://discord.com/developers/docs/interactions/receiving-and-responding

    async def edit_original_interaction_response(self, token, json):
        endpoint = (
            f"/webhooks/{self.application_id}/{token}/messages/@original"
        )

        return await self.patch(endpoint, json=json)

    async def create_followup_message(self, token, json):
        endpoint = f"/webhooks/{self.application_id}/{token}"

        return await self.post(endpoint, json=json)
