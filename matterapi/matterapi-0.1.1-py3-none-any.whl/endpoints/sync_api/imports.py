from typing import Any, Dict

from ..base import ApiBaseClass


class ImportsApi(ApiBaseClass):
    """Endpoints related to import files."""

    def list_imports(
        self,
    ) -> None:
        """List import files

        Lists all available import files.

        Permissions:
            Must have `manage_system` permissions.
        Minimum Server Version:
            5.31
        """

        url = "{}/imports".format(self.client.base_url)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        return response
