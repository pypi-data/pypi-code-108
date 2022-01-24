from typing import Any, Dict, List

import asyncio

from lunar.config import Config
from lunar.lunar_client import LunarClient

loop = asyncio.get_event_loop()


class QueryClient(LunarClient):
    """
    Client for Lunar Data API (`/v1/query`).

    ## Example

    ```python
    import lunar

    client = lunar.client("query")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

    async def get_query_async(
        self,
        dataset_id: str,
        attributes: List[str] = None,
        query: Dict[str, Any] = None,
        sort: Dict[str, int] = None,
        limit: int = 100,
        headers: Dict[str, Any] = dict(),
    ) -> List[Dict[str, Any]]:
        """
        Get a data result (async).

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - attributes: (optional) (dict) Attributes to get from datasets
        - query: (optional) (dict) Query statement
        - sort: (optional) (dict) Sort statement with int index {"Ascending": 1, "Descending": -1}
        - limit: (optional) (int) Max number of items to get
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        list

        ## Example

        ```python
        data = await client.get_query_async(
            dataset_id="my_dataset", attributes=["f1", "f2"], query={"f1": 100}, sort={"f1": 1, "f2": -1}, limit=5
        )

        ```
        """
        data = {"dataset_id": dataset_id}

        if attributes:
            assert isinstance(attributes, list), "`attributes` type must be list"
            data["f"] = attributes
        if query:
            assert isinstance(query, dict), "`query` type must be dict"
            data["q"] = query
        if sort:
            assert isinstance(sort, dict), "`sort` type must be dict"
            data["sort"] = sort
        if limit:
            assert isinstance(limit, int), "`limit` type must be int"
            data["limit"] = limit

        body = await self._request(method="POST", url=self.config.API_PATH, data=data, headers=headers)

        return body["data"]

    def get_query(
        self,
        dataset_id: str,
        attributes: List[str] = None,
        query: Dict[str, Any] = None,
        sort: Dict[str, int] = None,
        limit: int = 100,
        headers: Dict[str, Any] = dict(),
    ) -> List[Dict[str, Any]]:
        """
        Get a data result.

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - attributes: (optional) (dict) Attributes to get from datasets
        - query: (optional) (dict) Query statement
        - sort: (optional) (dict) Sort statement with int index {"Ascending": 1, "Descending": -1}
        - limit: (optional) (int) Max number of items to get
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        list

        ## Example

        ```python
        data = client.get_query(
            dataset_id="my_dataset", attributes=["f1", "f2"], query={"f1": 100}, sort={"f1": 1, "f2": -1}, limit=5
        )

        ```
        """

        return loop.run_until_complete(
            self.get_query_async(
                dataset_id=dataset_id, attributes=attributes, query=query, sort=sort, limit=limit, headers=headers
            )
        )
