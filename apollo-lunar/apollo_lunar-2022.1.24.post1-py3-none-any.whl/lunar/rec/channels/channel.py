from typing import List

import asyncio
from pydantic import ValidationError

from lunar.config import Config
from lunar.lunar_client import LunarClient, LunarError
from lunar.rec.channels.models import Channel, ChannelPutIn, ChannelPatchIn

loop = asyncio.get_event_loop()


class ChannelClient(LunarClient):
    """
    Client for Lunar Recommendation API (`/v1/channels/`).

    ## Example

    ```python
    import lunar

    client = lunar.client("channel")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

    async def create_channel_async(self, id: str, experiment_id: str = None) -> Channel:
        """
        Create a new channel (async).

        ## Args

        - id: (str) Unique identifier of a channel
        - experiment_id: (optional) (str) Unique identifier of an experiment assigned

        ## Returns
        `lunar.rec.channels.models.Channel`

        ## Example

        ```python
        channel = await client.create_channel_async(id="my_channel", experiment_id="my_experiment")
        ```
        """

        try:
            channel = Channel(id=id, experiment_id=experiment_id)
        except ValidationError as e:
            raise LunarError(code=400, msg=str(e))

        body = await self._request(method="POST", url=self.config.API_PATH, data=channel.dict())
        return Channel(**body["data"])

    def create_channel(self, id: str, experiment_id: str = None) -> Channel:
        """
        Create a new channel.

        ## Args

        - id: (str) Unique identifier of a channel
        - experiment_id: (optional) (str) Unique identifier of an experiment assigned

        ## Returns
        `lunar.rec.channels.models.Channel`

        ## Example

        ```python
        channel = client.create_channel(id="my_channel", experiment_id="my_experiment")
        ```
        """
        experiment_id = experiment_id or None

        return loop.run_until_complete(self.create_channel_async(id=id, experiment_id=experiment_id))

    async def list_channels_async(self) -> List[Channel]:
        """
        List channels (async).

        ## Returns
        list(`lunar.rec.channels.models.Channel`)

        ## Example

        ```python
        channels = await client.list_channels_async()
        ```
        """

        body = await self._request(method="GET", url=self.config.API_PATH)
        return [Channel(**channel) for channel in body["data"]]

    def list_channels(self) -> List[Channel]:
        """
        List channels.

        ## Returns
        list(`lunar.rec.channels.models.Channel`)

        ## Example

        ```python
        channels = client.list_channels()
        ```
        """

        return loop.run_until_complete(self.list_channels_async())

    async def get_channel_async(self, id: str) -> Channel:
        """
        Get a channel (async).

        ## Args

        - id: (str) Unique identifier of a channel

        ## Returns
        `lunar.rec.channels.models.Channel`

        ## Example

        ```python
        channel = await client.get_channel_async(id="my_channel")
        ```
        """

        body = await self._request(method="GET", url=f"{self.config.API_PATH}/{id}")
        return Channel(**body["data"])

    def get_channel(self, id: str) -> Channel:
        """
        Get a channel.

        ## Args

        - id: (str) Unique identifier of the channel

        ## Returns
        `lunar.rec.channels.models.Channel`

        ## Example

        ```python
        channel = client.get_channel(id="my_channel")
        ```
        """

        return loop.run_until_complete(self.get_channel_async(id=id))

    async def update_channel_async(self, id: str, experiment_id: str = None) -> Channel:
        """
        Update a channel (async).

        ## Args

        - id: (str) Unique identifier of a channel
        - experiment_id: (optional) (str) Unique identifier of an experiment assigned

        ## Returns
        `lunar.rec.channels.models.Channel`

        ## Example

        ```python
        updated_channel = await client.update_channel_async(id="my_channel", experiment_id="new_experiment")
        ```
        """

        try:
            updated_channel = ChannelPutIn(experiment_id=experiment_id)
        except ValidationError as e:
            raise LunarError(code=400, msg=str(e))

        body = await self._request(method="PUT", url=f"{self.config.API_PATH}/{id}", data=updated_channel.dict())
        return Channel(**body["data"])

    def update_channel(self, id: str, experiment_id: str = None) -> Channel:
        """
        Update a channel.

        ## Args

        - id: (str) Unique identifier of a channel
        - experiment_id: (optional) (str) Unique identifier of an experiment assigned

        ## Returns
        `lunar.rec.channels.models.Channel`

        ## Example

        ```python
        updated_channel = client.update_channel(id="my_channel", experiment_id="new_experiment")
        ```
        """
        experiment_id = experiment_id or None

        return loop.run_until_complete(self.update_channel_async(id=id, experiment_id=experiment_id))

    async def update_channel_partial_async(self, id: str, experiment_id: str = None) -> Channel:
        """
        Partially update a channel (async).

        ## Args

        - id: (str) Unique identifier of a channel
        - experiment_id: (optional) (str) Unique identifier of an experiment assigned

        ## Returns
        `lunar.rec.channels.models.Channel`

        ## Example

        ```python
        updated_channel = await client.update_channel_partial_async(id="my_channel", experiment_id="new_experiment")
        ```
        """

        patched_channel = ChannelPatchIn(**{"experiment_id": experiment_id})

        body = await self._request(
            method="PATCH", url=f"{self.config.API_PATH}/{id}", data=patched_channel.dict(exclude_none=True)
        )
        return Channel(**body["data"])

    def update_channel_partial(self, id: str, experiment_id: str = None) -> Channel:
        """
        Partially update a channel.

        ## Args

        - id: (str) Unique identifier of a channel
        - experiment_id: (optional) (str) Unique identifier of an experiment assigned

        ## Returns
        `lunar.rec.channels.models.Channel`

        ## Example

        ```python
        updated_channel = client.update_channel_partial(id="my_channel", experiment_id="new_experiment")
        ```
        """
        experiment_id = experiment_id or None

        return loop.run_until_complete(self.update_channel_partial_async(id=id, experiment_id=experiment_id))

    async def delete_channel_async(self, id: str) -> None:
        """
        Delete a channel (async).

        ## Args

        - id: (str) Unique identifier of a channel

        ## Example

        ```python
        await client.delete_channel_async(id="my_channel")
        ```
        """

        return await self._request(method="DELETE", url=f"{self.config.API_PATH}/{id}")

    def delete_channel(self, id: str) -> None:
        """
        Delete a channel.

        ## Args

        - id: (str) Unique identifier of a channel

        ## Example

        ```python
        client.delete_channel(id="my_channel")
        ```
        """

        return loop.run_until_complete(self.delete_channel_async(id=id))
