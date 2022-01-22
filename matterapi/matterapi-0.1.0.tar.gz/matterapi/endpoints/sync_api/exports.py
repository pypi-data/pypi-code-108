from typing import Any, Dict

from ..base import ApiBaseClass


class ExportsApi(ApiBaseClass):
    """Endpoints related to export files."""

    def list_exports(
        self,
    ) -> None:
        """List export files

        Lists all available export files.

        Permissions:
            Must have `manage_system` permissions.
        Minimum Server Version:
            5.33
        """

        url = "{}/exports".format(self.client.base_url)
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

    def download_export(
        self,
        export_name: str,
    ) -> None:
        """Download an export file

        Downloads an export file.

        Permissions:
            Must have `manage_system` permissions.
        Minimum Server Version:
            5.33
        """

        url = "{}/exports/{export_name}".format(
            self.client.base_url, export_name=export_name
        )
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

    def delete_export(
        self,
        export_name: str,
    ) -> None:
        """Delete an export file

        Deletes an export file.

        Permissions:
            Must have `manage_system` permissions.
        Minimum Server Version:
            5.33
        """

        url = "{}/exports/{export_name}".format(
            self.client.base_url, export_name=export_name
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = self.client.delete(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        return response
