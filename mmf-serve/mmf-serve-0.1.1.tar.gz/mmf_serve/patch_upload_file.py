import tempfile
from aiofile import async_open
from starlette.datastructures import UploadFile

orig = UploadFile.__init__


def custom_init(self: UploadFile, *args, **kwargs):
    orig(self, *args, **kwargs)
    filename = self.filename or ""
    *_, ext = filename.split(".")
    self.file = async_open(tempfile.NamedTemporaryFile(suffix=f".{ext}"))


async def custom_write(self: UploadFile, data):
    await self.file.write(data)


async def custom_read(self: UploadFile, size: int = -1):
    return self.file.read(size)


async def custom_seek(self, offset: int):
    try:
        return self.file.seak(offset)
    except Exception as exc:
        pass


async def custom_close(self):
    await self.file.close()


def get_file_name(self: UploadFile):
    self.filename
    return self.file.file.name


def patch_upload_file():
    UploadFile.__init__ = custom_init
    UploadFile.write = custom_write
    UploadFile.read = custom_read
    UploadFile.seek = custom_seek
    UploadFile.close = custom_close
    UploadFile.get_file_name = get_file_name
