"""A class for interacting with Video Indexer using asyncio.
Does not implement all API facilities."""
# pylint: disable=W0201

from datetime import datetime, timedelta
import aiohttp


class AsyncVideoIndexer:
    """A class for interacting with Video Indexer using asyncio."""

    @classmethod
    async def create(
        cls, account_id, subscription_key, location, get_access_token_on_startup=True
    ):
        """Acts as the __init__ method.
        This triggers W0201.
        Using an @classmethod rather than __init__ in order to init async."""
        self = AsyncVideoIndexer()
        self.account_id = account_id
        self.subscription_key = subscription_key
        self.location = location
        self.access_token = None
        self.next_access_token_reset_required = datetime.now()
        self.session = aiohttp.ClientSession()
        if get_access_token_on_startup:
            await self.get_access_token()
        return self

    async def get_access_token(self) -> None:
        """Rotates the current bearer token."""
        self.access_token = None
        print("Rotating token for Video Indexer.")
        params = {"allowEdit": "true"}
        async with await self.video_indexer_auth_request(
            "AccessToken", params=params
        ) as response:
            self.access_token = await response.json()
            self.next_access_token_reset_required = (
                timedelta(minutes=59) + datetime.now()
            )

    async def get_video_access_token(self, video_id, allow_edit=False):
        """Gets a bearer token for accessing an individual video."""
        if allow_edit:
            allow_edit = "true"
        else:
            allow_edit = "false"
        params = {"allowEdit": allow_edit}
        response = await self.video_indexer_auth_request(
            f"Videos/{video_id}/AccessToken",
            params=params,
        )
        return response

    async def upload_video_from_url(
        self, video_name, video_external_id, callback_url, video_url
    ):
        """Instructs Video Indexer to ingest a video from provided URL."""
        params = {
            "name": video_name,
            "externalId": video_external_id,
            "callbackUrl": callback_url,
            "videoUrl": video_url,
        }
        response = await self.video_indexer_api_request("Videos", "post", params=params)
        return response

    async def list_videos(self):
        """Lists all videos on the current account."""
        response = await self.video_indexer_api_request("Videos", "get")
        return response

    async def get_thumbnail(self, video_id, thumbnail_id):
        """Returns the thumbnail content for the provided video ID."""
        params = {
            "videoId": video_id,
            "thumbnailId": thumbnail_id,
        }
        response = await self.video_indexer_api_request(
            f"Videos/{video_id}/Thumbnails/{thumbnail_id}", "get", params=params
        )
        return response

    async def get_video_index(self, video_id):
        """Returns video information the provided video id."""
        params = {
            "videoId": video_id,
        }
        response = await self.video_indexer_api_request(
            f"Videos/{video_id}/Index", "get", params=params
        )
        return response

    async def get_video_id_by_external_id(self, external_id):
        """Gets the Video Indexer ID using an externally provided ID."""
        params = {
            "externalId": external_id,
        }
        response = await self.video_indexer_api_request(
            "Videos/GetIdByExternalId", "get", params=params
        )
        return response

    async def get_video_player_widget_url(self, video_id, video_access_token):
        """Gets the video player widget."""
        url = (
            f"https://api.videoindexer.ai/{self.location}/"
            + f"Accounts/{self.account_id}/"
            + f"Videos/{video_id}/PlayerWidget?accessToken={video_access_token}"
        )
        return url

    async def get_video_insights_widget_url(
        self, video_id, video_access_token, allow_edit=False
    ):
        """Gets the video insights Widget, as well as whether users should be able to edit."""
        if allow_edit:
            allow_edit = "true"
        else:
            allow_edit = "false"
        url = (
            f"https://api.videoindexer.ai/{self.location}/"
            + f"Accounts/{self.account_id}/"
            + f"Videos/{video_id}/InsightsWidget?accessToken={video_access_token}"
            + f"&allowEdit={allow_edit}"
        )
        return url

    async def video_indexer_api_request(
        self, api_resource, operation, params=None, headers=None
    ):
        """Used for most Async Get and Post API requests."""
        operations = {"get": self.session.get, "post": self.session.post}
        assert operation in operations
        operation = operations[operation]
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        assert isinstance(self.next_access_token_reset_required, datetime)
        current_datetime = datetime.now()
        if self.next_access_token_reset_required < current_datetime:
            await self.get_access_token()
        if self.access_token is not None:
            if "Authorization" not in headers:
                headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Ocp-Apim-Subscription-Key"] = self.subscription_key
        api_endpoint = (
            f"https://api.videoindexer.ai/{self.location}/"
            + f"Accounts/{self.account_id}/"
            + api_resource
        )
        return operation(api_endpoint, params=params, headers=headers)

    async def video_indexer_auth_request(self, api_resource, params=None):
        """Used to get Access tokens- generally and for video access"""
        if params is None:
            params = {}
        headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
        api_endpoint = (
            f"https://api.videoindexer.ai/Auth/{self.location}/"
            + f"Accounts/{self.account_id}/"
            + api_resource
        )
        return self.session.get(api_endpoint, params=params, headers=headers)
