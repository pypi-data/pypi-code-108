from O365.sharepoint import Sharepoint as _Sharepoint
from O365.sharepoint import Site as _Site

from rypython.ry365.drive import Storage


class Site(_Site):
    def __init__(self, *, parent=None, con=None, **kwargs):
        super().__init__(parent=parent, con=con, **kwargs)
        self.site_storage = Storage(parent=self, main_resource=f"/sites/{self.object_id}")


class Sharepoint(_Sharepoint):
    site_constructor = Site

    def __init__(self, *, parent=None, con=None, **kwargs):
        super().__init__(parent=parent, con=con, **kwargs)
