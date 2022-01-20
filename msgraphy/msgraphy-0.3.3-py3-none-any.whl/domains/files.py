import urllib
from pathlib import Path
from typing import Tuple

import requests

from msgraphy.data.file import Drive, DriveItem, BaseItem
from msgraphy.data.monitor import Monitor
from msgraphy.client.graph_client import GraphResponse
from msgraphy.data.user import User


class FilesGraphApi:
    __large_file_threshold = 4 * 1024 * 1024
    __large_file_fragment_size = 327680
    __large_file_fragment_target = __large_file_fragment_size * 25

    def __init__(self, api):
        self._api = api

    def parse_file_path(self, filename: str) -> Tuple[GraphResponse[Drive], str]:
        """
        This is a utility method that looks up drive and file data based on a set of fixed formats:

        * <EmailAddress>:path/to/file
        * <SiteName>:path/to/file
        * <SiteName>/<LibraryName>:path/to/file

        For the root site, leave <SiteName> blank, and for the root folder, leave path blank

        :param filename:
        :return:
        """
        if filename.startswith("sharepoint:"):
            filename = filename[11:]

        drivename, filename = filename.split(":", 1)
        if '@' in drivename:
            user = User(user_principal_name=drivename)
            drive = self._api.user.get_user_drive(user)
        elif '/' in drivename:
            sitename, drivename = drivename.split("/", 1)
            site = self._api.sharepoint.get_site_resource(name=sitename)
            drive = self._api.sharepoint.get_drive_by_name(site, drivename)
        else:
            site = self._api.sharepoint.get_site_resource(drivename)
            drive = self._api.sharepoint.get_drive_by_name(site)

        return drive, filename

    def parse_drive_item(self, filename: str) -> GraphResponse[DriveItem]:
        """
        This is a utility method that looks up a driveitem by "special path" as accepted by parse_file_path.

        This makes two requests to the server.
        :param filename:
        :return: A drive item
        """
        drive, filename = self.parse_file_path(filename)
        return self.get_file_by_name(drive.value, filename)

    def get_file_by_name(self, drive: Drive, filename: str) -> GraphResponse[DriveItem]:
        assert drive.id
        assert filename is not None

        if not filename.startswith("/"):
            filename = "/" + filename

        resource = f"/drives/{urllib.parse.quote(drive.id)}/root"
        if filename and filename != "/":
            resource += f":{filename}"

        return self._api.client.make_request(url=resource, method="get", response_type=DriveItem)

    def copy(self, item: BaseItem, new_parent_ref: BaseItem = None,
             new_name: str = None, conflict_behaviour=None) -> GraphResponse[Monitor]:
        """
        Copies a file to a new location.
        :param item: This is the item you want to copy
        :param new_parent_ref: The new parent of the item [optional]
        :param new_name: The new name of the item [optional]
        :param conflict_behaviour: The conflict resolution behavior for actions that create a new item.
                                    You can use the values fail, replace, or rename.
        :return:
        """
        assert new_parent_ref or new_name, "Must either set 'new_parent_ref' or 'new_name'"

        body = {}
        if new_name:
            body['name'] = new_name
        if new_parent_ref:
            body['parentReference'] = dict(
                driveId=new_parent_ref.parent_reference.drive_id,
                id=new_parent_ref.id,
            )

        params = {}
        if conflict_behaviour:
            params['@microsoft.graph.conflictBehavior'] = conflict_behaviour

        resource = f"{item.get_api_reference()}/copy"
        return self._api.client.make_request(url=resource, method="post", params=params,
                                             json=body, response_type=Monitor)

    def download_file(self, item: DriveItem):
        resource = f"{item.get_api_reference()}/content"
        return self._api.client.make_request(url=resource, stream=True)

    def upload_file(self, parent: BaseItem, filename: str, file):
        file_path = Path(file)
        file_size = file_path.stat().st_size
        if file_size < self.__large_file_threshold:
            return self.__upload_small_file(parent, filename, file_path)
        else:
            return self.__upload_large_file(parent, filename, file_path)

    def __upload_small_file(self, parent: BaseItem, filename: str, file: Path) -> GraphResponse[DriveItem]:
        resource = f"{parent.get_api_reference()}/root:{filename}:/content"

        with open(file, 'rb') as FILE:
            data = FILE.read()

        return self._api.client.make_request(url=resource, method="put", data=data, response_type=DriveItem)

    def __upload_large_file(self, parent: BaseItem, filename: str, file: Path) -> GraphResponse[DriveItem]:
        resource = f"{parent.get_api_reference()}/root:{filename}:/createUploadSession"

        file_size = file.stat().st_size

        session_response = self._api.client.make_request(url=resource, method="post", json=dict(fileSize=file_size))
        session_response_value = session_response.value
        upload_url = session_response_value['uploadUrl']

        with open(file, 'rb') as FILE:
            for pos in range(0, file_size, self.__large_file_fragment_target):
                data = FILE.read(self.__large_file_fragment_target)
                headers = {
                    "Content-Length": f"{len(data)}",
                    "Content-Range": f"bytes {pos}-{pos + len(data) - 1}/{file_size}",
                }
                session_response = self._api.client.make_request(url=upload_url, method="put",
                                                                 headers=headers, data=data,
                                                                 use_auth=False,
                                                                 response_type=self.MultiPartResponse,
                                                                 )

        return session_response

    class MultiPartResponse:
        @staticmethod
        def from_response(response: requests.Response):
            if response.status_code == 200 or response.status_code == 201:
                return DriveItem(response.json())
            else:
                return response.json()

