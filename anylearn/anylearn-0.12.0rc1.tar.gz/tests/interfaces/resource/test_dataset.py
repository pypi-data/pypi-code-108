import responses
from requests.exceptions import RequestException

from anylearn.config import init_sdk
from anylearn.interfaces.resource.resource import ResourceState, ResourceVisibility
from anylearn.interfaces.resource.dataset import Dataset
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from tests.base_test_case import BaseTestCase

class TestDataset(BaseTestCase):
    @responses.activate
    def test_list_dataset_ok(self):
        responses.add(responses.GET, url=self._url("dataset/list"),
                      json=[
                          {
                              'id': "DSET001",
                              'name': "TestDset1",
                              'description': "test",
                              'state': ResourceState.READY,
                              'visibility': ResourceVisibility.PUBLIC,
                              'upload_time': "2020-01-01 00:00",
                          },
                          {
                              'id': "DSET002",
                              'name': "TestDset2",
                              'description': "test",
                              'state': ResourceState.READY,
                              'visibility': ResourceVisibility.PUBLIC,
                              'upload_time': "2020-01-02 00:00",
                          },
                      ],
                      status=200)
        datasets = Dataset.get_list()
        self.assertIsInstance(datasets, list)
        self.assertEqual(len(datasets), 2)
        self.assertIsInstance(datasets[0], Dataset)
        self.assertIsInstance(datasets[1], Dataset)
        self.assertEqual(datasets[0].id, "DSET001")
        self.assertEqual(datasets[1].id, "DSET002")

    @responses.activate
    def test_list_dataset_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("dataset/list"),
                      json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            Dataset.get_list()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_dataset_detail_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("dataset/query?id=DSET001"),
                      match_querystring=True, json=[{
                          'id': "DSET001",
                          'name': "TestDset1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/datasets/DSET001/test.tar.gz",
                          'size': "250.41",
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                      }],
                      status=200)
        dataset = Dataset(id="DSET001", name="TestDset1", description="test",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PUBLIC,
                          upload_time="2020-01-01 00:00")
        dataset.get_detail()
        self.assertEqual(dataset.filename, "test.tar.gz")
        self.assertTrue(dataset.is_zipfile)
        self.assertEqual(dataset.file_path, "USER001/datasets/DSET001/test.tar.gz")
        self.assertEqual(dataset.size, "250.41")
        self.assertEqual(dataset.creator_id, "USER001")
        self.assertEqual(dataset.node_id, "NODE001")
        self.assertIsInstance(dataset.owner, list)
        self.assertEqual(dataset.owner[0], "USER001")


    @responses.activate
    def test_get_dataset_detail_no_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("dataset/query?id=DSET001"),
                      match_querystring=True, json=[{
                          'id': "DSET001",
                          'name': "TestDset1",
                          'description': "test",
                          'state': ResourceState.READY,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/datasets/DSET001/test.tar.gz",
                          'size': "250.41",
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                      }],
                      status=200)
        dataset = Dataset(id="DSET001", load_detail=True)
        self.assertEqual(dataset.name, "TestDset1")
        self.assertEqual(dataset.filename, "test.tar.gz")
        self.assertTrue(dataset.is_zipfile)
        self.assertEqual(dataset.file_path, "USER001/datasets/DSET001/test.tar.gz")
        self.assertEqual(dataset.size, "250.41")
        self.assertEqual(dataset.creator_id, "USER001")
        self.assertEqual(dataset.node_id, "NODE001")
        self.assertIsInstance(dataset.owner, list)
        self.assertEqual(dataset.owner[0], "USER001")

    @responses.activate
    def test_get_dataset_detail_ko_403(self):
        responses.add(responses.GET, url=self._url("dataset/query?id=DSET403"),
                      match_querystring=True, status=403)
        dataset = Dataset(id="DSET403", name="TestDsetForbidden",
                          description="test",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PRIVATE,
                          upload_time="2020-04-03 04:03")
        with self.assertRaises(RequestException) as ctx:
            dataset.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_get_dataset_detail_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("dataset/query?id=DSET250"),
                      match_querystring=True, json={'msg': "Unknown response"},
                      status=200)
        dataset = Dataset(id="DSET250", name="TestDset", description="test",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PROTECTED,
                          upload_time="2020-01-01 02:50")
        with self.assertRaises(AnyLearnException) as ctx:
            dataset.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_dataset_detail_empty_list(self):
        responses.add(responses.GET, url=self._url("dataset/query?id=DSET250"),
                      match_querystring=True, json=[],
                      status=200)
        dataset = Dataset(id="DSET250", name="TestDset", description="test",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PROTECTED,
                          upload_time="2020-01-01 02:50")
        with self.assertRaises(AnyLearnException) as ctx:
            dataset.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_create_dataset_ok(self):
        responses.add(responses.POST, url=self._url("dataset/add"),
                      json={'data': "DSET001", 'message': "数据集添加成功"},
                      status=200)
        dataset = Dataset(name="TestDset001", filename="test.tar.gz")
        result = dataset.save()
        self.assertTrue(result)
        self.assertEqual(dataset.id, "DSET001")

    @responses.activate
    def test_create_dataset_ko_empty_name_filename(self):
        dataset = Dataset()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            dataset.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "Dataset缺少必要字段：['name', 'filename']")

    @responses.activate
    def test_create_dataset_ko_unknown_response(self):
        responses.add(responses.POST, url=self._url("dataset/add"),
                      json={'msg': "Unknown response"}, status=201)
        dataset = Dataset(name="TestDset", filename="dset250.tar.gz")
        with self.assertRaises(AnyLearnException) as ctx:
            dataset.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_update_dataset_ok(self):
        responses.add(responses.PUT, url=self._url("dataset/update"),
                      json={'data': "DSET001", 'message': "数据集信息更新成功"},
                      status=200)
        dataset = Dataset(id="DSET001", name="TestDset1", description="test m",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PUBLIC,
                          upload_time="2020-01-01 00:00")
        result = dataset.save()
        self.assertTrue(result)

    @responses.activate
    def test_update_dataset_ko_empty_name(self):
        dataset = Dataset(id="DSET250", name="")
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            dataset.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "Dataset缺少必要字段：['name']")

    @responses.activate
    def test_update_dataset_ko_unknown_response(self):
        responses.add(responses.PUT, url=self._url("dataset/update"),
                      json={'msg': "Unknown response"},
                      status=200)
        dataset = Dataset(id="DSET250", name="TestDset", description="test",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PROTECTED,
                          upload_time="2020-01-01 02:50")
        with self.assertRaises(AnyLearnException) as ctx:
            dataset.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_delete_dataset_ok(self):
        responses.add(responses.DELETE,
                      url=self._url("dataset/delete?id=DSET001&force=0"),
                      match_querystring=True,
                      json={'data': "DSET001", 'message': "数据集删除成功"},
                      status=200)
        dataset = Dataset(id="DSET001", name="TestDset1", description="test d",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PUBLIC,
                          upload_time="2020-01-01 00:00")
        result = dataset.delete()
        self.assertTrue(result)

    @responses.activate
    def test_delete_dataset_ko_unknown_response(self):
        responses.add(responses.DELETE,
                      url=self._url("dataset/delete?id=DSET250&force=0"),
                      match_querystring=True,
                      json={'msg': "Unknown response"},
                      status=204)
        dataset = Dataset(id="DSET250", name="TestDset", description="test",
                          state=ResourceState.READY,
                          visibility=ResourceVisibility.PROTECTED,
                          upload_time="2020-01-01 02:50")
        with self.assertRaises(AnyLearnException) as ctx:
            dataset.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")
