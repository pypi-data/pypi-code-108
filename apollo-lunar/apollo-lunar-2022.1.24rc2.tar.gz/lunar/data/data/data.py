from typing import Any, Dict, List

import asyncio

from lunar.config import Config
from lunar.lunar_client import LunarClient

loop = asyncio.get_event_loop()


class DataClient(LunarClient):
    """
    Client for Lunar Data API (`/v1/data`).

    ## Example

    ```python
    import lunar

    client = lunar.client("data")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

    async def get_batch_data_async(
        self, dataset_id: str, ids: List[str], attributes: List[str] = None, headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get batch data results (async).

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - ids: (list) List of unique identifiers of targets
        - attributes: (optional) (dict) Attributes to get from datasets. If not, all attributes of result would be returned
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        data = await client.get_batch_data_async(dataset_id="my_dataset", ids=["id_1", "id_2"], attributes=["f1", "f2"])
        ```
        """
        assert type(ids) == list, "`ids` type must be list"
        if attributes:
            assert type(attributes) == list, "`attributes` type must be list"

        data = {"dataset_id": dataset_id, "ids": ids}
        if attributes:
            data["f"] = attributes

        body = await self._request(method="POST", url=f"{self.config.API_PATH}/batch", data=data, headers=headers)

        return body["data"]

    def get_batch_data(
        self, dataset_id: str, ids: List[str], attributes: List[str] = None, headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get batch data results.

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - ids: (list) List of unique identifiers of targets
        - attributes: (optional) (dict) Attributes to get from datasets. If not, all attributes of result would be returned
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        data = client.get_batch_data(dataset_id="my_dataset", ids=["id_1", "id_2"], attributes=["f1", "f2"])
        ```
        """

        return loop.run_until_complete(
            self.get_batch_data_async(dataset_id=dataset_id, ids=ids, attributes=attributes, headers=headers)
        )

    async def get_data_async(
        self, dataset_id: str, id: str, attributes: List[str] = None, headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get a data result (async).

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (str) Unique identifier of a target
        - attributes: (optional) (dict) Attributes to get from datasets. If not, all attributes of result would be returned
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        data = await client.get_data_async(dataset_id="my_dataset", id="my_id", attributes=["f1", "f2"])
        ```
        """
        if attributes:
            assert type(attributes) == list, "`attributes` type must be list"

        params = {"dataset_id": dataset_id, "id": id}
        if attributes:
            params["f"] = attributes

        body = await self._request(method="GET", url=self.config.API_PATH, params=params, headers=headers)

        return body["data"]

    def get_data(
        self, dataset_id: str, id: str, attributes: List[str] = None, headers: Dict[str, Any] = dict()
    ) -> Dict[str, Any]:
        """
        Get a data result.

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (str) Unique identifier of a target
        - attributes: (optional) (dict) Attributes to get from datasets. If not, all attributes of result would be returned
        - headers: (optional) (dict) Headers being sent to API server

        ## Returns
        dict

        ## Example

        ```python
        data = client.get_data(dataset_id="my_dataset", id="my_id", attributes=["f1", "f2"])
        ```
        """

        return loop.run_until_complete(
            self.get_data_async(dataset_id=dataset_id, id=id, attributes=attributes, headers=headers)
        )

    async def create_data_async(self, dataset_id: str, id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a data (async).

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (str) Unique identifier of a target
        - attributes: (dict) Attributes to create from datasets

        ## Returns
        dict

        ## Example

        ```python
        data = await client.create_data_async(dataset_id="my_dataset", id="my_id", attributes={"f1": 1, "f2": 2})
        ```
        """
        assert isinstance(attributes, dict), "`attributes` type must be dict"

        data = {"dataset_id": dataset_id, "id": id, "attributes": attributes}

        body = await self._request(method="POST", url=self.config.API_PATH, data=data)

        return body["data"]

    def create_data(self, dataset_id: str, id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a data.

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (str) Unique identifier of a target
        - attributes: (dict) Attributes to create from datasets

        ## Returns
        dict

        ## Example

        ```python
        data = client.create_data(dataset_id="my_dataset", id="my_id", attributes={"f1": 1, "f2": 2})
        ```
        """

        return loop.run_until_complete(self.create_data_async(dataset_id=dataset_id, id=id, attributes=attributes))

    async def update_data_async(self, dataset_id: str, id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a data (async).

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (str) Unique identifier of a target
        - attributes: (dict) Attributes to update from datasets

        ## Returns
        dict

        ## Example

        ```python
        data = await client.update_data_async(dataset_id="my_dataset", id="my_id", attributes={"f1": 1, "f2": 2, "f3": 3})
        ```
        """
        assert isinstance(attributes, dict), "`attributes` type must be dict"

        data = {"dataset_id": dataset_id, "id": id, "attributes": attributes}

        body = await self._request(method="PUT", url=self.config.API_PATH, data=data)

        return body["data"]

    def update_data(self, dataset_id: str, id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a data.

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (str) Unique identifier of a target
        - attributes: (dict) Attributes to update from datasets

        ## Returns
        dict

        ## Example

        ```python
        data = client.update_data(dataset_id="my_dataset", id="my_id", attributes={"f1": 1, "f2": 2, "f3": 3})
        ```
        """

        return loop.run_until_complete(self.update_data_async(dataset_id=dataset_id, id=id, attributes=attributes))

    async def update_data_partial_async(self, dataset_id: str, id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Partially update a data (async).

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (str) Unique identifier of a target
        - attributes: (dict) Attributes to partially update from datasets

        ## Returns
        dict

        ## Example

        ```python
        data = await client.update_data_partial_async(dataset_id="my_dataset", id="my_id", attributes={"feature": "a"})
        ```
        """
        assert isinstance(attributes, dict), "`attributes` type must be dict"

        data = {"dataset_id": dataset_id, "id": id, "attributes": attributes}

        body = await self._request(method="PATCH", url=self.config.API_PATH, data=data)

        return body["data"]

    def update_data_partial(self, dataset_id: str, id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Partially update a data.

        ## Args

        - dataset_id: (str) Unique identifier of a dataset
        - id: (str) Unique identifier of a target
        - attributes: (dict) Attributes to partially update from datasets

        ## Returns
        dict

        ## Example

        ```python
        data = client.update_data_partial(dataset_id="my_dataset", id="my_id", attributes={"feature": "a"})
        ```
        """

        return loop.run_until_complete(
            self.update_data_partial_async(dataset_id=dataset_id, id=id, attributes=attributes)
        )
