import os
import uuid
from pathlib import Path

import magic
from django.conf import settings

from isc_common.common.UploadItem import UploadItem


class UploadItemEx(UploadItem):

    def get_path(self, name):
        return os.path.dirname(os.path.abspath(name)).replace(os.sep, os.altsep) if os.altsep else os.path.dirname(os.path.abspath(name))

    def __init__(self, logger=None, **kwargs):
        super().__init__(logger=logger, dictionary=kwargs)

        stat = None
        if self.real_file_name is not None and self.file_mime_type is None:
            _, self.file_name = os.path.split(self.real_file_name)
            mime = magic.Magic(mime=True)
            if isinstance(settings.OLD_FILES, dict):
                o_ssh_client = settings.SSH_CLIENTS.client(settings.OLD_FILES)
                if o_ssh_client.exists(self.real_file_name):
                    self.file_mime_type = mime.from_buffer(o_ssh_client.open(self.real_file_name, 'rb').read())
                    stat = o_ssh_client.stat(self.real_file_name)
                elif os.path.exists(self.tmp_file_name):
                    self.file_mime_type = mime.from_file(self.tmp_file_name)
                    stat = Path(self.tmp_file_name).stat()
            else:
                if os.path.exists(self.real_file_name):
                    self.file_mime_type = mime.from_file(self.real_file_name)
                    stat = Path(self.real_file_name).stat()
                elif os.path.exists(self.tmp_file_name):
                    self.file_mime_type = mime.from_file(self.tmp_file_name)
                    stat = Path(self.tmp_file_name).stat()

        if stat is not None and self.file_size is None:
            self.file_size = stat.st_size

        if self.stored_file_name is None:
            self.stored_file_name = str(uuid.uuid4()).upper()
