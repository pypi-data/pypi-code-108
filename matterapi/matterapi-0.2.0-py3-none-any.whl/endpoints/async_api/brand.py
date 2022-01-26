from ...models import StatusOK, UploadBrandImageMultipartData
from ..base import ApiBaseClass


class BrandApi(ApiBaseClass):
    """Endpoints related to custom branding and white-labeling. See [our
    branding
    documentation](https://docs.mattermost.com/administration/branding.html)
    for more information."""

    async def get_brand_image(
        self,
    ) -> str:
        """Get brand image

        Get the previously uploaded brand image. Returns 404 if no brand image
        has been uploaded.

        Permissions:
            No permission required.
        """

        url = "/brand/image".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = response.json()
            return response_200
        return response

    async def upload_brand_image(
        self,
        *,
        multipart_data: UploadBrandImageMultipartData,
    ) -> StatusOK:
        """Upload brand image

        Uploads a brand image.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/brand/image".format()

        multipart_body_data = UploadBrandImageMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
            "files": multipart_body_data.get_files(),
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = StatusOK.parse_obj(response.json())

            return response_201
        return response

    async def delete_brand_image(
        self,
    ) -> StatusOK:
        """Delete current brand image

        Deletes the previously uploaded brand image. Returns 404 if no brand
        image has been uploaded.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.6
        """

        url = "/brand/image".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response
