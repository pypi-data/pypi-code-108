import os
import aiohttp
import responses
from aioresponses import aioresponses
from requests import RequestException

from anylearn.interfaces.resource.resource_downloader import AsyncResourceDownloader, SyncResourceDownloader
from tests.base_test_case import BaseTestCase

class TestResourceDownloader(BaseTestCase):
    @responses.activate
    def test_run_async_resource_downloader_ok(self):
        downloader = AsyncResourceDownloader()
        responses.add(responses.POST, url=self._url("resource/compression"),
                        match_querystring=True,
                        json={'data': "COMP123"},
                        status=200)
        responses.add(responses.GET, url=self._url("resource/compression"),
                            match_querystring=True,
                            json={'data': True},
                            status=200)
        with aioresponses() as mock_responses:
            file_name = "test_async_download.zip"
            headers = {'Content-Disposition': "attachment; filename=%s;" % file_name,}
            mock_responses.get(url=self._url("resource/download?file_id=FILE001&compression_id=COMP123&token=TEST_TOKEN"),
                               headers=headers,
                               payload={
                                   'message': "OK",
                               },
                               status=200)
            res = downloader.run(resource_id="FILE001",
                                 save_path="tests/",
                                 polling=1)
        os.remove(f"tests/{file_name}")
        self.assertTrue(res)

    @responses.activate
    def test_run_async_resource_downloader_500(self):
        with aioresponses() as mock_responses:
            downloader = AsyncResourceDownloader()
            responses.add(responses.POST, url=self._url("resource/compression"),
                          match_querystring=True,
                          json={'data': "COMP123"},
                          status=200)
            responses.add(responses.GET, url=self._url("resource/compression"),
                               match_querystring=True,
                               json={'data': True},
                               status=200)
            mock_responses.get(url=self._url("resource/download?file_id=FILE001&compression_id=COMP123&token=TEST_TOKEN"),
                               status=500)
            with self.assertRaises(aiohttp.ClientResponseError) as ctx:
                downloader.run(resource_id="FILE001",
                               save_path="/data/wtt",
                               polling=1)
                e = ctx.exception
                self.assertIsInstance(e,aiohttp.ClientResponseError)

    @responses.activate
    def test_run_sync_resource_downloader_ok(self):
        responses.add(responses.POST, url=self._url("resource/compression"),
                        match_querystring=True,
                        json={'data': "COMP123"},
                        status=200)
        responses.add(responses.GET, url=self._url("resource/compression"),
                            match_querystring=True,
                            json={'data': True},
                            status=200)
        downloader = SyncResourceDownloader()
        file_name = "test_sync_download.zip"
        headers = {'Content-Disposition': "attachment; filename=%s;" % file_name,}
        responses.add(responses.GET, url=self._url("resource/download?file_id=FILE001&compression_id=COMP123&token=TEST_TOKEN"),
                      match_querystring=True,
                      headers=headers,
                      status=200)
        res = downloader.run(resource_id="FILE001",
                             save_path="tests/")
        os.remove(f"tests/{file_name}")
        self.assertTrue(res)

    @responses.activate
    def test_run_sync_resource_downloader_500(self):
        downloader = SyncResourceDownloader()
        responses.add(responses.GET, url=self._url("resource/download?file_id=FILE001&token=TEST_TOKEN"),
                      status=500)
        with self.assertRaises(RequestException) as ctx:
            downloader.run(resource_id="FILE001",
                           save_path="/data/wtt")
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
