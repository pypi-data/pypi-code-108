import responses
from requests.exceptions import RequestException

from anylearn.config import init_sdk
from anylearn.interfaces.resource.resource import ResourceState, ResourceVisibility
from anylearn.interfaces.resource.model import Model
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from tests.base_test_case import BaseTestCase

class TestModel(BaseTestCase):
    @responses.activate
    def test_list_model_ok(self):
        responses.add(responses.GET, url=self._url("model/list"),
                      json=[
                          {
                              'id': "MODE001",
                              'name': "TestModel1",
                              'description': "test",
                              'state': ResourceState.READY,
                              'visibility': ResourceVisibility.PUBLIC,
                              'upload_time': "2020-01-01 00:00",
                              'creator_id': "USER001",
                              'node_id': "NODE001",
                              'owner': ["USER001"],
                              'algorithm_id': "ALGO001",
                          },
                          {
                              'id': "MODE002",
                              'name': "TestModel2",
                              'description': "test",
                              'state': ResourceState.READY,
                              'visibility': ResourceVisibility.PUBLIC,
                              'upload_time': "2020-01-02 00:00",
                              'creator_id': "USER002",
                              'node_id': "NODE002",
                              'owner': ["USER002"],
                              'algorithm_id': "ALGO002",
                          },
                      ],
                      status=200)
        models = Model.get_list()
        self.assertIsInstance(models, list)
        self.assertEqual(len(models), 2)
        self.assertIsInstance(models[0], Model)
        self.assertIsInstance(models[1], Model)
        self.assertEqual(models[0].id, "MODE001")
        self.assertEqual(models[1].id, "MODE002")
        self.assertEqual(models[0].algorithm_id, "ALGO001")
        self.assertEqual(models[1].algorithm_id, "ALGO002")

    @responses.activate
    def test_list_model_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("model/list"),
                      json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            Model.get_list()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_model_detail_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("model/query?id=MODE001"),
                      match_querystring=True, json=[{
                          'id': "MODE001",
                          'name': "TestModel1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/models/MODE001/test.tar.gz",
                          'size': "250.41",
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'algorithm_id': "ALGO001",
                      }],
                      status=200)
        model = Model(id="MODE001")
        model.get_detail()
        self.assertEqual(model.filename, "test.tar.gz")
        self.assertTrue(model.is_zipfile)
        self.assertEqual(model.file_path, "USER001/models/MODE001/test.tar.gz")
        self.assertEqual(model.size, "250.41")
        self.assertEqual(model.creator_id, "USER001")
        self.assertEqual(model.node_id, "NODE001")
        self.assertIsInstance(model.owner, list)
        self.assertEqual(model.owner[0], "USER001")
        self.assertEqual(model.algorithm_id, "ALGO001")

    @responses.activate
    def test_get_model_detail_no_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("model/query?id=MODE001"),
                      match_querystring=True, json=[{
                          'id': "MODE001",
                          'name': "TestModel1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/models/MODE001/test.tar.gz",
                          'size': "250.41",
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'algorithm_id': "ALGO001",
                      }],
                      status=200)
        model = Model(id="MODE001", load_detail=True)
        self.assertEqual(model.name, "TestModel1")
        self.assertEqual(model.filename, "test.tar.gz")
        self.assertTrue(model.is_zipfile)
        self.assertEqual(model.file_path, "USER001/models/MODE001/test.tar.gz")
        self.assertEqual(model.size, "250.41")
        self.assertEqual(model.creator_id, "USER001")
        self.assertEqual(model.node_id, "NODE001")
        self.assertIsInstance(model.owner, list)
        self.assertEqual(model.owner[0], "USER001")
        self.assertEqual(model.algorithm_id, "ALGO001")

    @responses.activate
    def test_get_model_detail_ko_403(self):
        responses.add(responses.GET, url=self._url("model/query?id=MODE403"),
                      match_querystring=True, status=403)
        model = Model(id="MODE403")
        with self.assertRaises(RequestException) as ctx:
            model.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_get_model_detail_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("model/query?id=MODE250"),
                      match_querystring=True, json={'msg': "Unknown response"},
                      status=200)
        model = Model(id="MODE250")
        with self.assertRaises(AnyLearnException) as ctx:
            model.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_model_detail_empty_list(self):
        responses.add(responses.GET, url=self._url("model/query?id=MODE250"),
                      match_querystring=True, json=[],
                      status=200)
        model = Model(id="MODE250")
        with self.assertRaises(AnyLearnException) as ctx:
            model.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_create_model_ok(self):
        responses.add(responses.POST, url=self._url("model/add"),
                      json={'data': "MODE001", 'message': "模型添加成功"},
                      status=200)
        model = Model(name="TestModel001", filename="test.tar.gz",
                      algorithm_id="ALGO001")
        result = model.save()
        self.assertTrue(result)
        self.assertEqual(model.id, "MODE001")

    @responses.activate
    def test_create_model_ko_empty_name_filename_algoid(self):
        model = Model()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            model.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "Model缺少必要字段：['name', 'filename', 'algorithm_id']")

    @responses.activate
    def test_create_model_ko_unknown_response(self):
        responses.add(responses.POST, url=self._url("model/add"),
                      json={'msg': "Unknown response"}, status=201)
        model = Model(name="TestModel", filename="model250.tar.gz",
                      algorithm_id="ALGO250")
        with self.assertRaises(AnyLearnException) as ctx:
            model.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_update_model_ok(self):
        responses.add(responses.PUT, url=self._url("model/update"),
                      json={'data': "MODE001", 'message': "模型信息更新成功"},
                      status=200)
        model = Model(id="MODE001", name="TestModel1", description="test m",
                      state=ResourceState.READY,
                      visibility=ResourceVisibility.PUBLIC,
                      upload_time="2020-01-01 00:00")
        result = model.save()
        self.assertTrue(result)

    @responses.activate
    def test_update_model_ko_empty_name(self):
        model = Model(id="MODE250", name="")
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            model.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "Model缺少必要字段：['name']")

    @responses.activate
    def test_update_model_ko_unknown_response(self):
        responses.add(responses.PUT, url=self._url("model/update"),
                      json={'msg': "Unknown response"},
                      status=200)
        model = Model(id="MODE250", name="TestModel")
        with self.assertRaises(AnyLearnException) as ctx:
            model.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_delete_model_ok(self):
        responses.add(responses.DELETE,
                      url=self._url("model/delete?id=MODE001&force=0"),
                      match_querystring=True,
                      json={'data': "MODE001", 'message': "模型删除成功"},
                      status=200)
        model = Model(id="MODE001")
        result = model.delete()
        self.assertTrue(result)

    @responses.activate
    def test_delete_model_ko_unknown_response(self):
        responses.add(responses.DELETE,
                      url=self._url("model/delete?id=MODE250&force=0"),
                      match_querystring=True,
                      json={'msg': "Unknown response"},
                      status=204)
        model = Model(id="MODE250")
        with self.assertRaises(AnyLearnException) as ctx:
            model.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")
