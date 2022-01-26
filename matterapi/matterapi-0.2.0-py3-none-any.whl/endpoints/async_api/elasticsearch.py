from ...models import StatusOK
from ..base import ApiBaseClass


class ElasticsearchApi(ApiBaseClass):
    """Endpoints for configuring and interacting with Elasticsearch."""

    async def test_elasticsearch(
        self,
    ) -> StatusOK:
        """Test Elasticsearch configuration

        Test the current Elasticsearch configuration to see if the Elasticsearch
        server can be contacted successfully.
        Optionally provide a configuration in the request body to test. If no
        valid configuration is present in the
        request body the current server configuration will be tested.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.1
        """

        url = "/elasticsearch/test".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def purge_elasticsearch_indexes(
        self,
    ) -> StatusOK:
        """Purge all Elasticsearch indexes

        Deletes all Elasticsearch indexes and their contents. After calling this
        endpoint, it is
        necessary to schedule a new Elasticsearch indexing job to repopulate the
        indexes.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.1
        """

        url = "/elasticsearch/purge_indexes".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response
