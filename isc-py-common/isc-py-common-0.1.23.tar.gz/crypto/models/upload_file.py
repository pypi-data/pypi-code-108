import os

# import websockets

from isc_common.http.DSRequest import DSRequest


class DSResponse_UploadFile(DSRequest):
    def remove(self, path):
        if os.path.exists(path):
            os.remove(path)

    def get_path(self, name):
        return os.path.dirname(os.path.abspath(name)).replace(os.sep, os.altsep) if os.altsep else os.path.dirname(os.path.abspath(name))
