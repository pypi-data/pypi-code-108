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

        url = "/imports".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response
