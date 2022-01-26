from typing import Any, Dict, List

import asyncio
from pydantic import ValidationError

from lunar.config import Config
from lunar.lunar_client import LunarClient, LunarError
from lunar.data.datasets.models import Dataset, DatasetPutIn, DatasetPatchIn
from lunar.data.datasets.models.params import PARAMS, PARAMS_PATCH


loop = asyncio.get_event_loop()


class DatasetClient(LunarClient):
    """
    Client for Lunar Data API (`/v1/datasets/`).

    ## Example

    ```python
    import lunar

    client = lunar.client("dataset")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

    async def create_dataset_async(self, id: str, data_type: str, params: Dict[str, Any]) -> Dataset:
        """
        Create a new dataset (async).

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (str) Dataset type
        - params: (dict) Dataset parameters

        ## Returns
        `lunar.data.datasets.Dataset`

        ## Example

        ```python
        # For dynamodb
        dataset = await client.create_dataset_async(
            id="my_dataset",
            data_type="dynamodb",
            params={"tables": ["first_table", "second_table"], "main_table": "first_table"},
        )

        or

        # For docdb
        dataset = await client.create_dataset_async(
            id="my_dataset",
            data_type="docdb",
            params={"collection": "my_collection"},
        )
        ```
        """
        assert data_type in PARAMS, f"`data_type` is only available on {list(PARAMS)}"
        assert isinstance(params, dict), "`params` should be `dict` type"

        try:
            dataset = Dataset[PARAMS[data_type]](id=id, data_type=data_type, params=params)
        except ValidationError as e:
            raise LunarError(code=400, msg=str(e))

        body = await self._request(method="POST", url=self.config.API_PATH, data=dataset.dict())
        return Dataset[PARAMS[data_type]](**body["data"])

    def create_dataset(self, id: str, data_type: str, params: Dict[str, Any]) -> Dataset:
        """
        Create a new dataset.

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (str) Dataset type
        - params: (dict) Dataset parameters

        ## Returns
        `lunar.data.datasets.Dataset`

        ## Example

        ```python
        # For dynamodb
        dataset = client.create_dataset(
            id="my_dataset",
            data_type="dynamodb",
            params={"tables": ["first_table", "second_table"], "main_table": "first_table"},
        )

        # For docdb
        dataset = client.create_dataset(
            id="my_dataset",
            data_type="docdb",
            params={"collection": "my_collection"},
        )
        ```
        """

        return loop.run_until_complete(self.create_dataset_async(id=id, data_type=data_type, params=params))

    async def list_datasets_async(self) -> List[Dataset]:
        """
        List datasets (async).

        ## Returns
        list(`lunar.data.datasets.Dataset`)

        ## Example

        ```python
        datasets = await client.list_datasets_async()
        ```
        """

        body = await self._request(method="GET", url=self.config.API_PATH)

        return [Dataset(**dataset) for dataset in body["data"]]

    def list_datasets(self) -> List[Dataset]:
        """
        List datasets.

        ## Returns
        list(`lunar.data.datasets.Dataset`)

        ## Example

        ```python
        datasets = client.list_datasets()
        ```
        """

        return loop.run_until_complete(self.list_datasets_async())

    async def get_dataset_async(self, id: str) -> Dataset:
        """
        Get a dataset (async).

        ## Args

        - id: (str) Unique identifier of a dataset

        ## Returns
        `lunar.data.datasets.Dataset`

        ## Example

        ```python
        dataset = await client.get_dataset_async(id="my_dataset")
        ```
        """

        body = await self._request(method="GET", url=f"{self.config.API_PATH}/{id}")
        return Dataset(**body["data"])

    def get_dataset(self, id: str) -> Dataset:
        """
        Get a dataset.

        ## Args

        - id: (str) Unique identifier of a dataset

        ## Returns
        `lunar.data.datasets.Dataset`

        ## Example

        ```python
        dataset = client.get_dataset(id="my_dataset")
        ```
        """

        return loop.run_until_complete(self.get_dataset_async(id=id))

    async def update_dataset_async(self, id: str, data_type: str, params: Dict[str, Any]) -> Dataset:
        """
        Update a dataset (async).

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (str) Dataset type
        - params: (dict) Dataset parameters with `tables` and `main_table`

        ## Returns
        `lunar.data.datasets.Dataset`

        ## Example

        ```python
        # For dynamodb
        experiment = await client.update_dataset_async(
            id="my_dataset",
            data_type="dynamodb",
            params={"tables": ["first_table", "second_table", "third_table"], "main_table": "second_table"}
        )

        # For docdb
        experiment = await client.update_dataset_async(
            id="my_dataset",
            data_type="docdb",
            params={"collections": "new_collections"}
        )
        ```
        """
        assert data_type in PARAMS, f"`data_type` is only available on {list(PARAMS)}"
        assert isinstance(params, dict), "`params` should be `dict` type"

        try:
            updated_dataset = DatasetPutIn[PARAMS[data_type]](
                data_type=data_type,
                params=params,
            )
        except ValidationError as e:
            raise LunarError(code=400, msg=str(e))

        body = await self._request(method="PUT", url=f"{self.config.API_PATH}/{id}", data=updated_dataset.dict())
        return Dataset[PARAMS[data_type]](**body["data"])

    def update_dataset(self, id: str, data_type: str, params: Dict[str, Any]) -> Dataset:
        """
        Update a dataset.

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (str) Dataset type
        - params: (dict) Dataset parameters

        ## Returns
        `lunar.data.datasets.Dataset`

        ## Example

        ```python
        # For dynamodb
        experiment = client.update_dataset(
            id="my_dataset",
            data_type="dynamodb",
            params={"tables": ["first_table", "second_table", "third_table"], "main_table": "second_table"}
        )

        # For docdb
        experiment = client.update_dataset(
            id="my_dataset",
            data_type="docdb",
            params={"collections": "new_collections"}
        )
        ```
        """

        return loop.run_until_complete(self.update_dataset_async(id=id, data_type=data_type, params=params))

    async def update_dataset_partial_async(self, id: str, data_type: str, params: Dict[str, Any] = None) -> Dataset:
        """
        Partially update a dataset (async).

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (optional) (str) Dataset type
        - params: (optional) (dict) Dataset parameters

        ## Returns
        `lunar.data.datasets.Dataset`

        ## Example

        ```python
        dataset = await client.update_dataset_partial_async(
            id="my_dataset", params={"tables": ["first_table"], "main_table": "first_table"}
        )
        ```
        """
        assert data_type in PARAMS, f"`data_type` is only available on {list(PARAMS)}"

        request_body = {"data_type": data_type}
        if params:
            assert isinstance(params, dict), "`params` should be `dict` type"
            request_body["params"] = params

        patched_dataset = DatasetPatchIn[PARAMS_PATCH[data_type]](**request_body)

        body = await self._request(
            method="PATCH", url=f"{self.config.API_PATH}/{id}", data=patched_dataset.dict(exclude_none=True)
        )
        return Dataset(**body["data"])

    def update_dataset_partial(self, id: str, data_type: str, params: Dict[str, Any] = None) -> Dataset:
        """
        Partially update a dataset.

        ## Args

        - id: (str) Unique identifier of a dataset
        - data_type: (optional) (str) Dataset type
        - params: (optional) (dict) Dataset parameters with `tables` and `main_table`

        ## Returns
        `lunar.data.datasets.Dataset`

        ## Example

        ```python
        dataset = client.update_dataset_partial(
            id="my_dataset", params={"tables": ["first_table"], "main_table": "first_table"}
        )
        ```
        """
        data_type = data_type or None
        params = params or None

        return loop.run_until_complete(self.update_dataset_partial_async(id=id, data_type=data_type, params=params))

    async def delete_dataset_async(self, id: str) -> None:
        """
        Delete a dataset (async)

        ## Args

        - id: (str) Unique identifier of a dataset

        ## Example

        ```python
        await client.delete_dataset_async(id="my_dataset")
        ```
        """

        return await self._request(method="DELETE", url=f"{self.config.API_PATH}/{id}")

    def delete_dataset(self, id: str) -> None:
        """
        Delete a dataset.

        ## Args

        - id: (str) Unique identifier of a dataset

        ## Example

        ```python
        client.delete_dataset(id="my_dataset")
        ```
        """

        return loop.run_until_complete(self.delete_dataset_async(id=id))
