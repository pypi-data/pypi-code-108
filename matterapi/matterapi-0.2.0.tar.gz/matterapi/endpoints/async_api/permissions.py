from typing import Any, Dict, List, Optional, cast

from ..base import ApiBaseClass


class PermissionsApi(ApiBaseClass):
    """ """

    async def get_ancillary_permissions(
        self,
        *,
        subsection_permissions: Optional[str] = None,
    ) -> List[str]:
        """Return all system console subsection ancillary permissions

        Returns all the ancillary permissions for the corresponding system
        console subsection permissions appended to the requested permission
        subsections.

        Minimum Server Version:
            5.35
        """

        url = "/permissions/ancillary".format()
        params: Dict[str, Any] = {
            "subsection_permissions": subsection_permissions,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = cast(List[str], response.json())

            return response_200
        return response
