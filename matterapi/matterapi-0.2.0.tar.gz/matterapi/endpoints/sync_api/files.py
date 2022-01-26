from typing import Any, Dict, Optional

from ...models import (
    FileInfo,
    FileInfoList,
    GetFileLinkResponse_200,
    SearchFilesMultipartData,
    UploadFileMultipartData,
    UploadFileResponse_201,
)
from ..base import ApiBaseClass


class FilesApi(ApiBaseClass):
    """Endpoints for uploading and interacting with files."""

    def upload_file(
        self,
        *,
        multipart_data: UploadFileMultipartData,
        channel_id: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> UploadFileResponse_201:
        """Upload a file

        Uploads a file that can later be attached to a post.

        This request can either be a multipart/form-data request with a
        channel_id, files and optional
        client_ids defined in the FormData, or it can be a request with the
        channel_id and filename
        defined as query parameters with the contents of a single file in the
        body of the request.

        Only multipart/form-data requests are supported by server versions up to
        and including 4.7.
        Server versions 4.8 and higher support both types of requests.

        Permissions:
            Must have `upload_file` permission.
        """

        url = "/files".format()
        params: Dict[str, Any] = {
            "channel_id": channel_id,
            "filename": filename,
        }
        params = {k: v for k, v in params.items() if v is not None}

        multipart_body_data = UploadFileMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
            "files": multipart_body_data.get_files(),
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = UploadFileResponse_201.parse_obj(response.json())

            return response_201
        return response

    def get_file(
        self,
        file_id: str,
    ) -> None:
        """Get a file

        Gets a file that has been uploaded previously.

        Permissions:
            Must have `read_channel` permission or be uploader of the file.
        """

        url = "/files/{file_id}".format(
            file_id=file_id,
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

    def get_file_thumbnail(
        self,
        file_id: str,
    ) -> None:
        """Get a file's thumbnail

        Gets a file's thumbnail.

        Permissions:
            Must have `read_channel` permission or be uploader of the file.
        """

        url = "/files/{file_id}/thumbnail".format(
            file_id=file_id,
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

    def get_file_preview(
        self,
        file_id: str,
    ) -> None:
        """Get a file's preview

        Gets a file's preview.

        Permissions:
            Must have `read_channel` permission or be uploader of the file.
        """

        url = "/files/{file_id}/preview".format(
            file_id=file_id,
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

    def get_file_link(
        self,
        file_id: str,
    ) -> GetFileLinkResponse_200:
        """Get a public file link

        Gets a public link for a file that can be accessed without logging into
        Mattermost.

        Permissions:
            Must have `read_channel` permission or be uploader of the file.
        """

        url = "/files/{file_id}/link".format(
            file_id=file_id,
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
            response_200 = GetFileLinkResponse_200.parse_obj(response.json())

            return response_200
        return response

    def get_file_info(
        self,
        file_id: str,
    ) -> FileInfo:
        """Get metadata for a file

        Gets a file's info.

        Permissions:
            Must have `read_channel` permission or be uploader of the file.
        """

        url = "/files/{file_id}/info".format(
            file_id=file_id,
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
            response_200 = FileInfo.parse_obj(response.json())

            return response_200
        return response

    def get_file_public(
        self,
        file_id: str,
        *,
        h: str,
    ) -> None:
        """Get a public file



        Permissions:
            No permissions required.
        """

        url = "/files/{file_id}/public".format(
            file_id=file_id,
        )
        params: Dict[str, Any] = {
            "h": h,
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

        return response

    def search_files(
        self,
        team_id: str,
        *,
        multipart_data: SearchFilesMultipartData,
    ) -> FileInfoList:
        """Search files in a team

        Search for files in a team based on file name, extention and file
        content (if file content extraction is enabled and supported for the
        files).

        Permissions:
            Must be authenticated and have the `view_team` permission.
        Minimum Server Version:
            5.34
        """

        url = "/teams/{team_id}/files/search".format(
            team_id=team_id,
        )

        multipart_body_data = SearchFilesMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = FileInfoList.parse_obj(response.json())

            return response_200
        return response
