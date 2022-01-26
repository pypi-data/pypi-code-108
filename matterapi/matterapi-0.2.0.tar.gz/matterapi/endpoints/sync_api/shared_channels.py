from typing import Any, Dict, List, Optional

from ...models import RemoteClusterInfo, SharedChannel
from ..base import ApiBaseClass


class SharedChannelsApi(ApiBaseClass):
    """Endpoints for getting information about shared channels."""

    def get_all_shared_channels(
        self,
        team_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 0,
    ) -> List[SharedChannel]:
        """Get all shared channels for team.

        Get all shared channels for a team.

        Permissions:
            Must be authenticated.
        Minimum Server Version:
            5.50
        """

        url = "/sharedchannels/{team_id}".format(
            team_id=team_id,
        )
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = SharedChannel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_remote_cluster_info(
        self,
        remote_id: str,
    ) -> RemoteClusterInfo:
        """Get remote cluster info by ID for user.

        Get remote cluster info based on remoteId.

        Permissions:
            Must be authenticated and user must belong to at least one channel
        shared with the remote cluster.
        Minimum Server Version:
            5.50
        """

        url = "/sharedchannels/remote_info/{remote_id}".format(
            remote_id=remote_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = RemoteClusterInfo.parse_obj(response.json())

            return response_200
        return response
