import responses
from requests.exceptions import RequestException

from anylearn.config import init_sdk
from anylearn.interfaces.resource.resource import ResourceState, ResourceVisibility
from anylearn.interfaces.resource.file import File
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from tests.base_test_case import BaseTestCase

class TestFile(BaseTestCase):
    @responses.activate
    def test_list_file_ok(self):
        responses.add(responses.GET, url=self._url("file/list"),
                      json=[
                          {
                              'id': "FILE001",
                              'name': "TestFile1",
                              'description': "test",
                              'state': ResourceState.READY,
                              'visibility': ResourceVisibility.PUBLIC,
                              'upload_time': "2020-01-01 00:00",
                              'filename': "testfile1.txt",
                              'creator_id': "USER001",
                              'node_id': "NODE001",
                              'owner': ["USER001"],
                          },
                          {
                              'id': "FILE002",
                              'name': "TestFile2",
                              'description': "test",
                              'state': ResourceState.READY,
                              'visibility': ResourceVisibility.PUBLIC,
                              'upload_time': "2020-01-02 00:00",
                              'filename': "testfile2.txt",
                              'creator_id': "USER002",
                              'node_id': "NODE002",
                              'owner': ["USER002"],
                          },
                      ],
                      status=200)
        files = File.get_list()
        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 2)
        self.assertIsInstance(files[0], File)
        self.assertIsInstance(files[1], File)
        self.assertEqual(files[0].id, "FILE001")
        self.assertEqual(files[1].id, "FILE002")
        self.assertEqual(files[0].filename, "testfile1.txt")
        self.assertEqual(files[1].filename, "testfile2.txt")

    @responses.activate
    def test_list_file_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("file/list"),
                      json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            File.get_list()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_file_detail_explicit_ok(self):
        responses.add(responses.GET, url=self._url("file/query?id=FILE001"),
                      match_querystring=True, json=[{
                          'id': "FILE001",
                          'name': "TestFile1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/files/FILE001/test.tar.gz",
                          'size': "250.41",
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                      }],
                      status=200)
        test_file = File(id="FILE001")
        test_file.get_detail()
        self.assertEqual(test_file.filename, "test.tar.gz")
        self.assertTrue(test_file.is_zipfile)
        self.assertEqual(test_file.file_path, "USER001/files/FILE001/test.tar.gz")
        self.assertEqual(test_file.size, "250.41")
        self.assertEqual(test_file.creator_id, "USER001")
        self.assertEqual(test_file.node_id, "NODE001")
        self.assertIsInstance(test_file.owner, list)
        self.assertEqual(test_file.owner[0], "USER001")

    @responses.activate
    def test_get_file_detail_no_explicit_ok(self):
        responses.add(responses.GET, url=self._url("file/query?id=FILE001"),
                      match_querystring=True, json=[{
                          'id': "FILE001",
                          'name': "TestFile1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/files/FILE001/test.tar.gz",
                          'size': "250.41",
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                      }],
                      status=200)
        test_file = File(id="FILE001", load_detail=True)
        self.assertEqual(test_file.name, "TestFile1")
        self.assertEqual(test_file.filename, "test.tar.gz")
        self.assertTrue(test_file.is_zipfile)
        self.assertEqual(test_file.file_path, "USER001/files/FILE001/test.tar.gz")
        self.assertEqual(test_file.size, "250.41")
        self.assertEqual(test_file.creator_id, "USER001")
        self.assertEqual(test_file.node_id, "NODE001")
        self.assertIsInstance(test_file.owner, list)
        self.assertEqual(test_file.owner[0], "USER001")

    @responses.activate
    def test_get_file_detail_ko_403(self):
        responses.add(responses.GET, url=self._url("file/query?id=FILE403"),
                      match_querystring=True, status=403)
        test_file = File(id="FILE403")
        with self.assertRaises(RequestException) as ctx:
            test_file.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_get_file_detail_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("file/query?id=FILE250"),
                      match_querystring=True, json={'msg': "Unknown response"},
                      status=200)
        test_file = File(id="FILE250")
        with self.assertRaises(AnyLearnException) as ctx:
            test_file.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_file_detail_empty_list(self):
        responses.add(responses.GET, url=self._url("file/query?id=FILE250"),
                      match_querystring=True, json=[],
                      status=200)
        test_file = File(id="FILE250")
        with self.assertRaises(AnyLearnException) as ctx:
            test_file.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_create_file_ok(self):
        responses.add(responses.POST, url=self._url("file/add"),
                      json={'data': "FILE001", 'message': "文件添加成功"},
                      status=200)
        test_file = File(name="TestFILE001", filename="test.tar.gz")
        result = test_file.save()
        self.assertTrue(result)
        self.assertEqual(test_file.id, "FILE001")

    @responses.activate
    def test_create_file_ko_empty_name_filename(self):
        test_file = File()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            test_file.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "File缺少必要字段：['name', 'filename']")

    @responses.activate
    def test_create_file_ko_unknown_response(self):
        responses.add(responses.POST, url=self._url("file/add"),
                      json={'msg': "Unknown response"}, status=201)
        test_file = File(name="TestFile", filename="FILE250.tar.gz")
        with self.assertRaises(AnyLearnException) as ctx:
            test_file.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_update_file_ok(self):
        responses.add(responses.PUT, url=self._url("file/update"),
                      json={'data': "FILE001", 'message': "文件信息更新成功"},
                      status=200)
        test_file = File(id="FILE001", name="TestFile1", description="test m",
                         state=ResourceState.READY,
                         visibility=ResourceVisibility.PUBLIC,
                         upload_time="2020-01-01 00:00")
        result = test_file.save()
        self.assertTrue(result)

    @responses.activate
    def test_update_file_ko_empty_name(self):
        test_file = File(id="FILE250", name="")
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            test_file.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "File缺少必要字段：['name']")

    @responses.activate
    def test_update_file_ko_unknown_response(self):
        responses.add(responses.PUT, url=self._url("file/update"),
                      json={'msg': "Unknown response"},
                      status=200)
        test_file = File(id="FILE250", name="TestFile", description="test",
                         state=ResourceState.READY,
                         visibility=ResourceVisibility.PROTECTED,
                         upload_time="2020-01-01 02:50")
        with self.assertRaises(AnyLearnException) as ctx:
            test_file.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_delete_file_ok(self):
        responses.add(responses.DELETE,
                      url=self._url("file/delete?id=FILE001&force=0"),
                      match_querystring=True,
                      json={'data': "FILE001", 'message': "文件删除成功"},
                      status=200)
        test_file = File(id="FILE001", name="TestFile1", description="test d",
                         state=ResourceState.READY,
                         visibility=ResourceVisibility.PUBLIC,
                         upload_time="2020-01-01 00:00")
        result = test_file.delete()
        self.assertTrue(result)

    @responses.activate
    def test_delete_file_ko_unknown_response(self):
        responses.add(responses.DELETE,
                      url=self._url("file/delete?id=FILE250&force=0"),
                      match_querystring=True,
                      json={'msg': "Unknown response"},
                      status=204)
        test_file = File(id="FILE250", name="TestFile", description="test",
                         state=ResourceState.READY,
                         visibility=ResourceVisibility.PROTECTED,
                         upload_time="2020-01-01 02:50")
        with self.assertRaises(AnyLearnException) as ctx:
            test_file.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")
