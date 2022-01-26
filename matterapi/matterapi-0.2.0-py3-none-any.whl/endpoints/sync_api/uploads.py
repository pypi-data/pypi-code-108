from typing import Union

from pydantic import BaseModel

from ...models import CreateUploadJsonBody, FileInfo, UploadDataFormData, UploadSession
from ..base import ApiBaseClass


class UploadsApi(ApiBaseClass):
    """Endpoints for creating and performing file uploads."""

    def create_upload(
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

        url = "/uploads".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = UploadSession.parse_obj(response.json())

            return response_201
        return response

    def get_upload(
        self,
        upload_id: str,
    ) -> None:
        """Get an upload session

        Gets an upload session that has been previously created.

        Permissions:
            Must be logged in as the user who created the upload session.
        """

        url = "/uploads/{upload_id}".format(
            upload_id=upload_id,
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

        return response

    def upload_data(
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

        url = "/uploads/{upload_id}".format(
            upload_id=upload_id,
        )

        request_kwargs = {
            "url": url,
            "data": form_data,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = FileInfo.parse_obj(response.json())

            return response_201
        return response
