import os
from unittest.mock import patch, create_autospec
import sys

import responses

from anylearn.interfaces.resource.resource import Resource
from anylearn.utils.errors import AnyLearnException
from tests.base_test_case import BaseTestCase

class TestResource(BaseTestCase):
    @responses.activate
    def test_resource_list_dir(self):
        responses.add(responses.GET, url=self._url("resource/listdir?file_id=FILE001"),
                      match_querystring=True,
                      json={
                          'dir0': {
                              'name': "dir0",
                              'type': "dir",
                              'child': {
                                  'file0': {
                                      'name': "file0",
                                      'type': "file",
                                  },
                                  'file1': {
                                      'name': "file1",
                                      'type': "file",
                                  },
                              }
                          }
                      },
                      status=200)
        res = Resource.list_dir("FILE001")
        self.assertIn('dir0', res)
        self.assertIn('name', res['dir0'])
        self.assertIn('type', res['dir0'])
        self.assertIn('child', res['dir0'])
        self.assertEqual(res['dir0']['name'], "dir0")
        self.assertEqual(res['dir0']['type'], "dir")
        self.assertEqual(len(res['dir0']['child']), 2)
        self.assertIn('file0', res['dir0']['child'])
        self.assertIn('file1', res['dir0']['child'])
        self.assertEqual(res['dir0']['child']['file0']['name'], "file0")
        self.assertEqual(res['dir0']['child']['file1']['name'], "file1")
        self.assertEqual(res['dir0']['child']['file0']['type'], "file")
        self.assertEqual(res['dir0']['child']['file1']['type'], "file")

    @patch('anylearn.interfaces.resource.resource_uploader.ResourceUploader')
    @responses.activate
    def test_resource_upload_file(self, MockResourceUploader):
        @create_autospec
        def mock_upload_ok(resource_id, chunks):
            return True

        # Mock uploader with stubbed upload function
        uploader = MockResourceUploader()
        uploader.run = mock_upload_ok

        # Stub finish upload request
        responses.add(responses.POST, url=self._url("resource/upload_finish"),
                     json={
                         'msg': "上传已完成，稍后可查看上传结果"
                     },
                     status=200)
        
        # Stub a test file
        filename = "tests/testfile.txt"
        with open(filename, 'w') as f:
            f.write("test")
        
        res = Resource.upload_file("FILE001", filename, uploader=uploader)

        self.assertTrue(res)
        uploader.run.assert_called_once()

        os.remove(filename)

    @patch('anylearn.interfaces.resource.resource_downloader.ResourceDownloader')
    @responses.activate
    def test_resource_download_file(self, MockResourceDownloader):
        @create_autospec
        def mock_download_ok(resource_id, polling, save_path):
            return True
        
        downloader = MockResourceDownloader()
        downloader.run = mock_download_ok

        res = Resource.download_file(resource_id="FILE001",
                                     save_path="tests/",
                                     downloader=downloader,
                                    )

        self.assertTrue(res)
        downloader.run.assert_called_once()
        
    @patch('anylearn.interfaces.resource.resource_downloader.ResourceDownloader')
    @responses.activate
    def test_resource_download_file_savepath_not_exists(self, MockResourceDownloader):
        @create_autospec
        def mock_download_ok(resource_id,save_path):
            return True
        
        downloader = MockResourceDownloader()
        downloader.run = mock_download_ok

        save_path = "/data/wtt/aaa888"
        with self.assertRaises(AnyLearnException) as ctx:
            res = Resource.download_file("FILE001", save_path, downloader=downloader)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, f"保存路径{save_path}不存在")
