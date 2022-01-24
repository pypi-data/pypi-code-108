from .testcase import VolumeTestCase, FileSystemTestCase
from aiohttp.test_utils import unittest_run_loop
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin


class TestVolumeGet(VolumeTestCase, GetOneMixin):
    pass


class TestVolumeGetAll(VolumeTestCase, GetAllMixin):
    pass


class TestVolumePost(VolumeTestCase, PostMixin):
    pass


class TestVolumePut(VolumeTestCase, PutMixin):
    pass


class TestVolumeDelete(VolumeTestCase, DeleteMixin):
    pass


class TestFileSystemGet(FileSystemTestCase, GetOneMixin):
    pass


class TestFileSystemGetAll(FileSystemTestCase, GetAllMixin):
    pass


class TestFileSystemPost(FileSystemTestCase, PostMixin):
    pass


class TestFileSystemPut(FileSystemTestCase, PutMixin):
    pass


class TestFileSystemDelete(FileSystemTestCase, DeleteMixin):
    pass
