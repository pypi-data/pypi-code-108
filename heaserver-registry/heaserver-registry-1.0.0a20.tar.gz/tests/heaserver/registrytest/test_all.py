from .componenttestcase import ComponentTestCase
from aiohttp.test_utils import unittest_run_loop
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin


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