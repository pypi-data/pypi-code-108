import aiohttp
from aioresponses import aioresponses

from anylearn.interfaces.resource.resource_uploader import AsyncResourceUploader
from tests.base_test_case import BaseTestCase

class TestResourceUploader(BaseTestCase):
    def test_run_async_resource_uploader_ok(self):
        n_chunks = 4

        n_total = n_progress = 0

        def on_start(total):
            nonlocal n_total
            n_total = total

        def on_progress(curr, _):
            nonlocal n_progress
            n_progress += 1

        uploader = AsyncResourceUploader(on_start=on_start,
                                         on_progress=on_progress)

        with aioresponses() as mock_responses:
            [mock_responses.post(url=self._url("resource/upload"),
                                 payload={
                                     'message': "OK",
                                 },
                                 status=200)
                for i in range(n_chunks)]
            res = uploader.run(resource_id="FILE001",
                               chunks=["test"] * n_chunks)
        self.assertTrue(res)
        self.assertEqual(n_total, n_chunks)
        self.assertEqual(n_progress, n_chunks)

    def test_run_resource_uploader_ko_500(self):
        n_chunks = 4
        with aioresponses() as mock_responses:
            uploader = AsyncResourceUploader()
            mock_responses.post(url=self._url("resource/upload"),
                                status=500)
            with self.assertRaises(aiohttp.ClientResponseError) as ctx:
                uploader.run(resource_id="FILE001",
                             chunks=["test"] * n_chunks)
            e = ctx.exception
            self.assertIsInstance(e, aiohttp.ClientResponseError)
