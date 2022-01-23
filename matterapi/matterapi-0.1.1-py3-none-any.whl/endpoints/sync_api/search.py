from typing import Any, Dict

from ...models import FileInfoList, SearchFilesMultipartData
from ..base import ApiBaseClass


class SearchApi(ApiBaseClass):
    """ """

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

        url = "{}/teams/{team_id}/files/search".format(
            self.client.base_url, team_id=team_id
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        multipart_body_data = SearchFilesMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "data": multipart_body_data.get_data(),
        }

        response = self.client.post(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = FileInfoList.parse_obj(response.json())

            return response_200
        return response
