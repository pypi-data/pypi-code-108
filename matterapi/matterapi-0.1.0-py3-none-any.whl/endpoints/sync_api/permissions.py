from typing import Any, Dict, List, Optional, cast

from ..base import ApiBaseClass


class PermissionsApi(ApiBaseClass):
    """ """

    def get_ancillary_permissions(
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

        url = "{}/permissions/ancillary".format(self.client.base_url)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()
        params: Dict[str, Any] = {
            "subsection_permissions": subsection_permissions,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "params": params,
        }

        response = self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = cast(List[str], response.json())

            return response_200
        return response
