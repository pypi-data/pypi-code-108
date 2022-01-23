from typing import Any, Dict, Union

from pydantic import BaseModel

from ...models import CreateUploadJsonBody, FileInfo, UploadDataFormData, UploadSession
from ..base import ApiBaseClass


class UploadsApi(ApiBaseClass):
    """Endpoints for creating and performing file uploads."""

    async def create_upload(
        self,
        *,
        json_body: CreateUploadJsonBody,
    ) -> UploadSession:
        """Create an upload

        Creates a new upload session.

        Permissions:
            Must have `upload_file` permission.
        Minimum Server Version:
            5.28
        """

        url = "{}/uploads".format(self.client.base_url)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "json": json_json_body,
        }

        response = await self.client.post(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = UploadSession.parse_obj(response.json())

            return response_201
        return response

    async def get_upload(
        self,
        upload_id: str,
    ) -> None:
        """Get an upload session

        Gets an upload session that has been previously created.

        Permissions:
            Must be logged in as the user who created the upload session.
        """

        url = "{}/uploads/{upload_id}".format(self.client.base_url, upload_id=upload_id)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = await self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        return response

    async def upload_data(
        self,
        upload_id: str,
        *,
        form_data: UploadDataFormData,
    ) -> Union[FileInfo, None]:
        """Perform a file upload

        Starts or resumes a file upload.
        To resume an existing (incomplete) upload, data should be sent starting
        from the offset specified in the upload session object.

        The request body can be in one of two formats:
        - Binary file content streamed in request's body
        - multipart/form-data

        Permissions:
            Must be logged in as the user who created the upload session.
        """

        url = "{}/uploads/{upload_id}".format(self.client.base_url, upload_id=upload_id)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "data": form_data,
        }

        response = await self.client.post(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = FileInfo.parse_obj(response.json())

            return response_201
        return response
