from django.core.files.storage import DefaultStorage
from django.db.models import FileField
from isc_common.fields import Field


class DbFileField(FileField, Field):
    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        def_str = '/blob/filename/mimetype'
        _upload_to = f"{upload_to}{def_str}" if upload_to.find(def_str) == -1 else upload_to
        if not storage:
            storage = DefaultStorage()
            storage.download_from = _upload_to
        super().__init__(verbose_name=verbose_name, name=name, upload_to=_upload_to, storage=storage, **kwargs)
