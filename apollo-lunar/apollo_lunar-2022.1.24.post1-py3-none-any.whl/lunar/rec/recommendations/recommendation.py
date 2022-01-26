from typing import Any, Dict

import asyncio

from lunar.config import Config
from lunar.lunar_client import LunarClient
from lunar.rec.recommendations.models import RecommendationIn, RecommendationOut

loop = asyncio.get_event_loop()


class RecommendationClient(LunarClient):
    """
    Client for Lunar Recommendation API (`/v1/recommend/`).

    ## Example

    ```python
    import lunar

    client = lunar.client("recommend")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

    async def recommend_async(
        self, id: str, channel_id: str, params: Dict[str, Any] = dict(), headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get recommended items for the target (async).

        ## Args

        - id: (str) Unique identifier of a recommendation target
        - channel_id: (str) Unique identifier of a channel
        - params: (optional) (dict) Additional parameters for recommendation
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        result = await client.recommend_async(id="a", channel_id="my_channel", params={"first_param": 100, "second_param": "value"}
        ```
        """

        data = RecommendationIn(id=id, channel_id=channel_id, params=params)

        body = await self._request(
            method="POST", url=self.config.API_PATH, data=data.dict(), params=params, headers=headers
        )
        result = RecommendationOut(**body["data"])

        return result.dict()

    def recommend(
        self, id: str, channel_id: str, params: Dict[str, Any] = dict(), headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get recommended items for the target.

        ## Args

        - id: (str) Unique identifier of a recommendation target
        - channel_id: (str) Unique identifier of a channel
        - params: (optional) (dict) Additional parameters for recommendation
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        result = client.recommend(id="a", channel_id="my_channel", params={"first_param": 100, "second_param": "value"}
        ```
        """

        return loop.run_until_complete(
            self.recommend_async(id=id, channel_id=channel_id, params=params, headers=headers)
        )
