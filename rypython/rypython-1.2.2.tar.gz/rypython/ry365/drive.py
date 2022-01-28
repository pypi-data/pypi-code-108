import logging
import requests

from O365.drive import Drive as _Drive
from O365.drive import Folder as _Folder
from O365.drive import Storage as _Storage
from O365.drive import Image, Photo, File


logger = logging.getLogger(__name__)


class Folder(_Folder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_item(self, item_name: str):
        for item in self.get_items():
            if item_name.lower() in item.name.lower():
                return item

    @staticmethod
    def _classifier(item):
        if 'folder' in item:
            return Folder
        elif 'image' in item:
            return Image
        elif 'photo' in item:
            return Photo
        else:
            return File


class Drive(_Drive):
    def __init__(self, *, parent=None, con=None, **kwargs):
        super().__init__(parent=parent, con=con, **kwargs)

    @staticmethod
    def _classifier(item):
        if 'folder' in item:
            return Folder
        elif 'image' in item:
            return Image
        elif 'photo' in item:
            return Photo
        else:
            return File

    def get_item_by_path(self, *parts: str):
        item_path = f"/{'/'.join(parts)}"
        logger.info(f"{item_path=}")
        if self.object_id:
            url = self.build_url(
                self._endpoints.get('get_item_by_path').format(id=self.object_id,
                                                               item_path=item_path))
        else:
            url = self.build_url(
                self._endpoints.get('get_item_by_path_default').format(item_path=item_path))
        try:
            response = self.con.get(url)
            if not response:
                return None
            data = response.json()
            return self._classifier(data)(
                parent=self,
                **{self._cloud_data_key: data}
            )
        except requests.exceptions.HTTPError:
            return

class Storage(_Storage):
    drive_constructor = Drive

    def __init__(self, *, parent=None, con=None, **kwargs):
        super().__init__(parent=parent, con=con, **kwargs)

    def get_default_drive(self, request_drive=False):
        if request_drive is False:
            return Drive(con=self.con, protocol=self.protocol,
                         main_resource=self.main_resource, name='Default Drive')
        super().get_default_drive(request_drive=request_drive)
