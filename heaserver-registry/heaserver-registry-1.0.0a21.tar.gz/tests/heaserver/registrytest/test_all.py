from .componenttestcase import ComponentTestCase, ComponentTestCase2
from aiohttp.test_utils import unittest_run_loop
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.testcase.mixin import _ordered
from heaobject.user import NONE_USER
from heaobject.volume import DEFAULT_FILE_SYSTEM
from aiohttp import hdrs


class TestGetComponent(ComponentTestCase, GetOneMixin):
    pass


class TestGetAllComponents(ComponentTestCase, GetAllMixin):
    pass


class TestPostComponent(ComponentTestCase, PostMixin):

    @unittest_run_loop
    async def test_post_status_invalid_base_url(self):
        await self._test_invalid({'base_url': 2})

    @unittest_run_loop
    async def test_post_status_invalid_resource(self):
        await self._test_invalid({'resources': [2]})

    @unittest_run_loop
    async def test_post_status_invalid_resources_list(self):
        await self._test_invalid({'resources': 2})


class TestPutComponent(ComponentTestCase, PutMixin):

    @unittest_run_loop
    async def test_put_status_invalid_base_url(self):
        await self._test_invalid({'base_url': 2})

    @unittest_run_loop
    async def test_put_status_invalid_resource(self):
        await self._test_invalid({'resources': [2]})


class TestDeleteComponent(ComponentTestCase, DeleteMixin):
    pass


class TestGetResource(ComponentTestCase):
    _headers = {SUB: NONE_USER, hdrs.X_FORWARDED_HOST: 'localhost:8080'}

    @unittest_run_loop
    async def test_no_file_system(self):
        actual = [{"collection": {"version": "1.0",
                                  "href": "http://localhost:8080/components/bytype/heaobject.folder.Folder", "items": [{
                "data": [
                    {
                        "name": "id",
                        "value": "666f6f2d6261722d71757578",
                        "prompt": "id",
                        "display": False},
                    {
                        "name": "created",
                        "value": None,
                        "prompt": "created",
                        "display": True},
                    {
                        "name": "derived_by",
                        "value": None,
                        "prompt": "derived_by",
                        "display": True},
                    {
                        "name": "derived_from",
                        "value": [],
                        "prompt": "derived_from",
                        "display": True},
                    {
                        "name": "description",
                        "value": None,
                        "prompt": "description",
                        "display": True},
                    {
                        "name": "display_name",
                        "value": "Reximus",
                        "prompt": "display_name",
                        "display": True},
                    {
                        "name": "invited",
                        "value": [],
                        "prompt": "invited",
                        "display": True},
                    {
                        "name": "modified",
                        "value": None,
                        "prompt": "modified",
                        "display": True},
                    {
                        "name": "name",
                        "value": "reximus",
                        "prompt": "name",
                        "display": True},
                    {
                        "name": "owner",
                        "value": "system|none",
                        "prompt": "owner",
                        "display": True},
                    {
                        "name": "shared_with",
                        "value": [],
                        "prompt": "shared_with",
                        "display": True},
                    {
                        "name": "source",
                        "value": None,
                        "prompt": "source",
                        "display": True},
                    {
                        "name": "version",
                        "value": None,
                        "prompt": "version",
                        "display": True},
                    {
                        "name": "base_url",
                        "value": "http://localhost/foo",
                        "prompt": "base_url",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "resource_type_name",
                        "value": "heaobject.folder.Folder",
                        "prompt":
                            "resource_type_name",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "base_path",
                        "value": "/folders",
                        "prompt": "base_path",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "file_system_name",
                        "value": "DEFAULT_FILE_SYSTEM",
                        "prompt": "file_system_name",
                        "display": True}],
                "links": []}]}}]
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.folder.Folder').path,
                                        headers=TestGetResource._headers)
        self.assertEquals(_ordered(actual), _ordered(await obj.json()))

    @unittest_run_loop
    async def test_no_file_system_status(self):
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.folder.Folder').path,
                                        headers=TestGetResource._headers)
        self.assertEquals(200, obj.status)

    @unittest_run_loop
    async def test_right_file_system_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemname' / DEFAULT_FILE_SYSTEM).path,
                                        headers=TestGetResource._headers)
        self.assertEquals(200, obj.status)

    @unittest_run_loop
    async def test_wrong_file_system_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemname' / 'WRONG_FILE_SYSTEM').path,
                                        headers=TestGetResource._headers)
        self.assertEquals(404, obj.status)


class TestGetResource(ComponentTestCase2):
    _headers = {SUB: NONE_USER, hdrs.X_FORWARDED_HOST: 'localhost:8080'}

    @unittest_run_loop
    async def test_no_file_system(self):
        actual = [{"collection": {"version": "1.0",
                                  "href": "http://localhost:8080/components/bytype/heaobject.folder.Folder", "items": [{
                "data": [
                    {
                        "name": "id",
                        "value": "666f6f2d6261722d71757578",
                        "prompt": "id",
                        "display": False},
                    {
                        "name": "created",
                        "value": None,
                        "prompt": "created",
                        "display": True},
                    {
                        "name": "derived_by",
                        "value": None,
                        "prompt": "derived_by",
                        "display": True},
                    {
                        "name": "derived_from",
                        "value": [],
                        "prompt": "derived_from",
                        "display": True},
                    {
                        "name": "description",
                        "value": None,
                        "prompt": "description",
                        "display": True},
                    {
                        "name": "display_name",
                        "value": "Reximus",
                        "prompt": "display_name",
                        "display": True},
                    {
                        "name": "invited",
                        "value": [],
                        "prompt": "invited",
                        "display": True},
                    {
                        "name": "modified",
                        "value": None,
                        "prompt": "modified",
                        "display": True},
                    {
                        "name": "name",
                        "value": "reximus",
                        "prompt": "name",
                        "display": True},
                    {
                        "name": "owner",
                        "value": "system|none",
                        "prompt": "owner",
                        "display": True},
                    {
                        "name": "shared_with",
                        "value": [],
                        "prompt": "shared_with",
                        "display": True},
                    {
                        "name": "source",
                        "value": None,
                        "prompt": "source",
                        "display": True},
                    {
                        "name": "version",
                        "value": None,
                        "prompt": "version",
                        "display": True},
                    {
                        "name": "base_url",
                        "value": "http://localhost/foo",
                        "prompt": "base_url",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "resource_type_name",
                        "value": "heaobject.folder.Folder",
                        "prompt":
                            "resource_type_name",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "base_path",
                        "value": "/folders",
                        "prompt": "base_path",
                        "display": True},
                    {
                        "section": "resources",
                        "index": 0,
                        "name": "file_system_name",
                        "value": "DEFAULT_FILE_SYSTEM",
                        "prompt": "file_system_name",
                        "display": True}],
                "links": []}]}}]
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.folder.Folder').path,
                                        headers=TestGetResource._headers)
        self.assertEquals(_ordered(actual), _ordered(await obj.json()))

    @unittest_run_loop
    async def test_no_file_system_status(self):
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.folder.Folder').path,
                                        headers=TestGetResource._headers)
        self.assertEquals(200, obj.status)

    @unittest_run_loop
    async def test_right_file_system_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemname' / DEFAULT_FILE_SYSTEM).path,
                                        headers=TestGetResource._headers)
        self.assertEquals(200, obj.status)

    @unittest_run_loop
    async def test_wrong_file_system_status(self):
        obj = await self.client.request('GET',
                                        (
                                            self._href / 'bytype' / 'heaobject.folder.Folder' / 'byfilesystemname' / 'WRONG_FILE_SYSTEM').path,
                                        headers=TestGetResource._headers)
        self.assertEquals(404, obj.status)

