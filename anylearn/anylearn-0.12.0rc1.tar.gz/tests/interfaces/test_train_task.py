from datetime import datetime, timezone, timedelta
import json
import uuid

from requests.exceptions import RequestException
import responses
from urllib.parse import urlencode
from unittest.mock import patch, create_autospec

from anylearn.interfaces.resource import Model, ResourceVisibility, ResourceState
from anylearn.interfaces.train_task import TrainTask, TrainTaskState
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException
from tests.base_test_case import BaseTestCase
from anylearn.storage.db.db import DB
from anylearn.applications.train_profile import TrainProfile

class TestTrainTask(BaseTestCase):
    @responses.activate
    def test_get_train_task_detail_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI001"),
                      match_querystring=True, json=[{
                          'id': "TRAI001",
                          'name': "TestTrainTask1",
                          'description': "test",
                          'state': TrainTaskState.RUNNING,
                          'visibility': 2,
                          'creator_id': "USER001",
                          'owner': ["USER001"],
                          'project_id': "PROJ001",
                          'algorithm_id': "ALGO001",
                          'algorithm_git_ref': None,
                          'args': "{\"arg1\":1, \"arg2\":\"test\"}",
                          'files': "DSET001",
                          'results_id': "FILE001",
                          'secret_key': "SECRET",
                          'create_time': "2021-03-01 23:59:59",
                          'finish_time': "",
                          'envs': "",
                          'resource_request': '[{"default": {"CPU": 1}}]',
                      }],
                      status=200)
        train_task = TrainTask(id="TRAI001")
        train_task.get_detail()
        self.assertEqual(train_task.name, "TestTrainTask1")
        self.assertEqual(train_task.description, "test")
        self.assertEqual(train_task.state, TrainTaskState.RUNNING)
        self.assertEqual(train_task.visibility, 2)
        self.assertEqual(train_task.creator_id, "USER001")
        self.assertIsInstance(train_task.owner, list)
        self.assertEqual(train_task.project_id, "PROJ001")
        self.assertEqual(train_task.algorithm_id, "ALGO001")
        if train_task.train_params:
            self.assertIsInstance(json.loads(train_task.train_params), dict)
        self.assertEqual(train_task.files, "DSET001")
        self.assertEqual(train_task.results_id, "FILE001")
        self.assertEqual(train_task.secret_key, "SECRET")
        self.assertEqual(train_task.create_time, "2021-03-01 23:59:59")

    @responses.activate
    def test_get_train_task_detail_no_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI002"),
                      match_querystring=True, json=[{
                          'id': "TRAI002",
                          'name': "TestTrainTask2",
                          'description': "test",
                          'state': TrainTaskState.RUNNING,
                          'visibility': 2,
                          'creator_id': "USER002",
                          'owner': ["USER002"],
                          'project_id': "PROJ002",
                          'algorithm_id': "ALGO002",
                          'algorithm_git_ref': None,
                          'args': "{\"arg1\":1, \"arg2\":\"test\"}",
                          'files': "DSET001",
                          'results_id': "FILE002",
                          'secret_key': "SECRET",
                          'create_time': "2021-03-01 23:59:59",
                          'finish_time': "",
                          'envs': "",
                          'resource_request': '[{"default": {"CPU": 1}}]',
                      }],
                      status=200)
        train_task = TrainTask(id="TRAI002", load_detail=True)
        self.assertEqual(train_task.name, "TestTrainTask2")
        self.assertEqual(train_task.description, "test")
        self.assertEqual(train_task.state, TrainTaskState.RUNNING)
        self.assertEqual(train_task.visibility, 2)
        self.assertEqual(train_task.creator_id, "USER002")
        self.assertIsInstance(train_task.owner, list)
        self.assertEqual(train_task.project_id, "PROJ002")
        self.assertEqual(train_task.algorithm_id, "ALGO002")
        if train_task.train_params:
            self.assertIsInstance(json.loads(train_task.train_params), dict)
        self.assertEqual(train_task.files, "DSET001")
        self.assertEqual(train_task.results_id, "FILE002")
        self.assertEqual(train_task.secret_key, "SECRET")
        self.assertEqual(train_task.create_time, "2021-03-01 23:59:59")

    @responses.activate
    def test_get_train_task_detail_ko_403(self):
        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI403"),
                      match_querystring=True, status=403)
        train_task = TrainTask(id="TRAI403")
        with self.assertRaises(RequestException) as ctx:
            train_task.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_get_train_task_detail_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI250"),
                      match_querystring=True, json={'msg': "Unknown response"},
                      status=200)
        train_task = TrainTask(id="TRAI250")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_train_task_detail_empty_list(self):
        responses.add(responses.GET, url=self._url("train_task/query?id=TRAI250"),
                      match_querystring=True, json=[],
                      status=200)
        train_task = TrainTask(id="TRAI250")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_create_train_task_ok(self):
        responses.add(responses.POST, url=self._url("train_task/add"),
                      json={'data': "TRAI001", 'message': "服务添加成功"},
                      status=200)
        train_task = TrainTask(name="TestTrainTask001", project_id="PROJ001",
                               algorithm_id="ALGO001",
                               train_params="{\"arg1\":1, \"arg2\":\"test\"}")
        result = train_task.save()
        self.assertTrue(result)
        self.assertEqual(train_task.id, "TRAI001")

    def test_create_train_task_ko_empty_name_projectid_algoid_trainparams(self):
        train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            train_task.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "TrainTask缺少必要字段：['name', 'project_id', 'algorithm_id', 'train_params']")

    @responses.activate
    def test_create_train_task_ko_unknown_response(self):
        responses.add(responses.POST, url=self._url("train_task/add"),
                      json={'msg': "Unknown response"}, status=201)
        train_task = TrainTask(name="TestTrainTask250", project_id="PROJ250",
                               algorithm_id="ALGO250",
                               train_params="{\"arg1\":1, \"arg2\":\"test\"}")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_delete_train_task_ok(self):
        responses.add(responses.DELETE,
                      url=self._url("train_task/delete?id=TRAI001&force=0"),
                      match_querystring=True,
                      json={'data': "TRAI001", 'message': "任务删除成功"},
                      status=200)
        train_task = TrainTask(id="TRAI001")
        result = train_task.delete()
        self.assertTrue(result)

    @responses.activate
    def test_delete_train_task_ko_unknown_response(self):
        responses.add(responses.DELETE,
                      url=self._url("train_task/delete?id=TRAI250&force=0"),
                      match_querystring=True,
                      json={'msg': "Unknown response"},
                      status=204)
        train_task = TrainTask(id="TRAI250")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_train_task_log_ok(self):
        query_str = urlencode({
            'id': "TRAI001",
            'limit': 100,
            'direction': "init",
            'index': 0,
            'offset_index': -1,
        })
        responses.add(responses.GET,
                      url=self._url(f"train_task/log?{query_str}"),
                      match_querystring=True,
                      json=[
                          {'offset': 1, 'offset_index': 1, 'text': "log1"},
                          {'offset': 2, 'offset_index': 2, 'text': "log2"},
                          {'offset': 3, 'offset_index': 3, 'text': "log3"},
                      ],
                      status=200)
        train_task = TrainTask(id="TRAI001")
        result = train_task.get_log()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIn('text', result[0])
        self.assertIn('text', result[1])
        self.assertIn('text', result[2])

    def test_get_service_log_ko_empty_id(self):
        train_task = TrainTask(name="TestTrainTask")
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            train_task.get_log()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "TrainTask缺少必要字段：['id']")

    @responses.activate
    def test_get_train_task_log_ko_unknown_response(self):
        query_str = urlencode({
            'id': "TRAI250",
            'limit': 100,
            'direction': "init",
            'index': 0,
            'offset_index': -1,
        })
        responses.add(responses.GET,
                      url=self._url(f"train_task/log?{query_str}"),
                      match_querystring=True,
                      json="",
                      status=204)
        train_task = TrainTask(id="TRAI250")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.get_log()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_train_task_last_log_ok(self):
        query_str = urlencode({
            'id': "TRAI001",
            'limit': 100,
            'direction': "init",
            'index': 0,
            'offset_index': -1,
        })
        responses.add(responses.GET,
                      url=self._url(f"train_task/log?{query_str}"),
                      match_querystring=True,
                      json=[
                          {'offset': 3, 'offset_index': 3, 'text': "log3"},
                          {'offset': 2, 'offset_index': 2, 'text': "log2"},
                          {'offset': 1, 'offset_index': 1, 'text': "log1"},
                      ],
                      status=200)
        train_task = TrainTask(id="TRAI001")
        result = train_task.get_last_log(debug=False)
        tz = datetime.now().astimezone().tzinfo
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], f"[{str(datetime.fromtimestamp(1/1000, tz=tz))}] log1")
        self.assertEqual(result[1], f"[{str(datetime.fromtimestamp(2/1000, tz=tz))}] log2")
        self.assertEqual(result[2], f"[{str(datetime.fromtimestamp(3/1000, tz=tz))}] log3")

    @responses.activate
    def test_get_train_task_full_log_ok(self):
        log_res = [
            {'offset': i, 'offset_index': i, 'text': f"log{i}"}
            for i in range(200)
        ]
        query_str_1 = urlencode({
            'id': "TRAI001",
            'limit': 100,
            'direction': "back",
            'index': 0,
            'offset_index': -1,
        })
        query_str_2 = urlencode({
            'id': "TRAI001",
            'limit': 100,
            'direction': "back",
            'index': 99,
            'offset_index': 99,
        })
        responses.add(responses.GET,
                      url=self._url(f"train_task/log?{query_str_1}"),
                      match_querystring=True,
                      json=log_res[:100],
                      status=200)
        responses.add(responses.GET,
                      url=self._url(f"train_task/log?{query_str_2}"),
                      match_querystring=True,
                      json=log_res[100:],
                      status=200)
        train_task = TrainTask(id="TRAI001")
        result = train_task.get_full_log(debug=False)
        tz = datetime.now().astimezone().tzinfo
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 200)
        self.assertEqual(result[0], f"[{str(datetime.fromtimestamp(0, tz=tz))}] log0")
        self.assertEqual(result[99], f"[{str(datetime.fromtimestamp(99/1000, tz=tz))}] log99")
        self.assertEqual(result[199], f"[{str(datetime.fromtimestamp(199/1000, tz=tz))}] log199")

    @responses.activate
    def test_get_train_task_status_ok(self):
        responses.add(responses.GET, url=self._url("train_task/status?id=TRAI001&secret_key=SECRET"),
                      match_querystring=True, json={
                          'current_epoch': "6",
                          'current_train_loss': "1.234",
                          'current_train_step': "567",
                          'ip': "10.244.2.165",
                          'process': "0.987",
                          'secret_key': "SECRET",
                          'state': "working",
                      },
                      status=200)
        train_task = TrainTask(id="TRAI001", secret_key="SECRET")
        res = train_task.get_status()
        self.assertIsInstance(res, dict)
        self.assertIn('current_epoch', res)
        self.assertIn('current_train_loss', res)
        self.assertIn('current_train_step', res)
        self.assertIn('process', res)
        self.assertIn('ip', res)
        self.assertIn('secret_key', res)

    def test_get_train_task_status_ko_empty_id_secretkey(self):
        train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            train_task.get_status()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "TrainTask缺少必要字段：['id', 'secret_key']")

    @responses.activate
    def test_get_train_task_status_ko_unknown_response(self):
        responses.add(responses.GET,
                      url=self._url("train_task/status?id=TRAI250&secret_key=SECRET250"),
                      match_querystring=True,
                      json=[{'msg': "Unknown response"}],
                      status=204)
        train_task = TrainTask(id="TRAI250", secret_key="SECRET250")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.get_status()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_report_final_metric_ok(self):
        responses.add(responses.POST, url=self._url("train_task/final_metric"),
                      json={
                          'msg': "任务TRAId123结果指标保存成功",
                      },
                      status=200)
        train_task = TrainTask(id="TRAI123", secret_key="SECRET")
        res = train_task.report_final_metric(metric=66.8)
        self.assertIsInstance(res, dict)
        self.assertEqual("任务TRAId123结果指标保存成功", res['msg'])
        self.assertEqual(train_task.final_metric, 66.8)

    def test_report_final_metric_empty_id_secretkey(self):
        train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            train_task.report_final_metric(250.41)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "TrainTask缺少必要字段：['id', 'secret_key']")

    @responses.activate
    def test_report_final_metric_unknown_response(self):
        responses.add(responses.POST,
                      url=self._url("train_task/final_metric"),
                      json=[{'msg': "Unknown response"}],
                      status=204)
        train_task = TrainTask(id="TRAI250", secret_key="SECRET")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.report_final_metric(250.41)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_final_metric_ok(self):
        responses.add(responses.GET,
                      url=self._url("train_task/final_metric?id=TRAI001"),
                      match_querystring=True,
                      json={
                          'final_metric': 662.8,
                          'id': "TRAI001",
                          'name': "test"
                      },
                      status=200)
        train_task = TrainTask(id="TRAI001")
        res = train_task.get_final_metric()
        self.assertIsInstance(res, dict)
        self.assertIn('id', res)
        self.assertIn('name', res)
        self.assertIn('final_metric', res)

    def test_get_final_metric_empty_id(self):
        train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            train_task.get_final_metric()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "TrainTask缺少必要字段：['id']")

    @responses.activate
    def test_get_final_metric_unknown_response(self):
        responses.add(responses.GET,
                      url=self._url("train_task/final_metric?id=TRAI250"),
                      match_querystring=True,
                      json=[{'msg': "Unknown response"}],
                      status=204)
        train_task = TrainTask(id="TRAI250", secret_key="SECRET250")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.get_final_metric()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_report_intermediate_metric_ok(self):
        responses.add(responses.POST,
                      url=self._url("train_task/intermediate_metric"),
                      json={
                          'msg': "任务TRAId123结果指标保存成功",
                      },
                      status=200)
        train_task = TrainTask(id="TRAI123", secret_key="SECRET")
        res = train_task.report_intermediate_metric(88.6)
        self.assertIsInstance(res, dict)
        self.assertEqual("任务TRAId123结果指标保存成功", res['msg'])

    def test_report_intermediate_metric_empty_id_secretkey(self):
        train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            train_task.report_intermediate_metric(88.8)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "TrainTask缺少必要字段：['id', 'secret_key']")

    @responses.activate
    def test_report_intermediate_metric_unknown_response(self):
        responses.add(responses.POST,
                      url=self._url("train_task/intermediate_metric"),
                      json=[{'msg': "Unknown response"}],
                      status=204)
        train_task = TrainTask(id="TRAI250", secret_key="SECRET")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.report_intermediate_metric(88.8)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_intermediate_metric_ok(self):
        dt = "2021-05-19 00:00:00"
        query_str = urlencode({
            'id': "TRAI123",
            'last_timestamp': dt,
        })
        responses.add(responses.GET,
                      url=self._url(f"train_task/intermediate_metric?{query_str}"),
                      match_querystring=True,
                      json=[
                          {
                              "id": "METR123",
                              "metric": 90.0,
                              "train_task_id": "TRAI123",
                          },
                          {
                              "id": "METR456",
                              "metric": 90.2,
                              "train_task_id": "TRAI123",
                          },
                      ],
                      status=200)
        train_task = TrainTask(id="TRAI123")
        res = train_task.get_intermediate_metric(last_timestamp=dt)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        self.assertIn('id', res[0])
        self.assertIn('id', res[1])
        self.assertIn('metric', res[0])
        self.assertIn('metric', res[1])
        self.assertIn('train_task_id', res[0])
        self.assertIn('train_task_id', res[1])

    def test_get_intermediate_metric_empty_id(self):
        train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            train_task.get_intermediate_metric()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "TrainTask缺少必要字段：['id']")

    @responses.activate
    def test_get_intermediate_metric_unknown_response(self):
        dt = "2021-05-19 00:00:00"
        query_str = urlencode({
            'id': "TRAI250",
            'last_timestamp': dt,
        })
        responses.add(responses.GET,
                      url=self._url(f"train_task/intermediate_metric?{query_str}"),
                      match_querystring=True,
                      json={'msg': "Unknown response"},
                      status=204)
        train_task = TrainTask(id="TRAI250")
        with self.assertRaises(AnyLearnException) as ctx:
            train_task.get_intermediate_metric(last_timestamp=dt)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @patch('anylearn.interfaces.resource.resource_downloader.ResourceDownloader')
    @responses.activate
    def test_download_results_ok(self, MockResourceDownloader):
        @create_autospec
        def mock_download_ok(resource_id, save_path, polling):
            return True

        downloader = MockResourceDownloader()
        downloader.run = mock_download_ok

        save_path = "tests/"
        train_task = TrainTask(results_id="FILE001",
                               state=TrainTaskState.SUCCESS)
        res = train_task.download_results(
            save_path=save_path, downloader=downloader)
        self.assertTrue(res)

    @responses.activate
    def test_download_results_state_not_success(self):

        train_task = TrainTask(results_id="FILE001",
                               state=TrainTaskState.CREATED)
        with self.assertRaises(AnyLearnException) as ctx:
            save_path = "tests/"
            train_task.download_results(
                save_path=save_path, downloader=None)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "训练未开始!")

    @responses.activate
    def test_download_results_state_empty_results_id(self):

        train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            save_path = "tests/"
            train_task.download_results(
                save_path=save_path, downloader=None)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "TrainTask缺少必要字段：['results_id']")

    @responses.activate
    def test_transform_model_ok(self):
        responses.add(responses.POST,
                      url=self._url("model/transform"),
                      match_querystring=True,
                      json={
                          "data": "MODE001",
                          "message": "模型转存工作正在进行，请稍后查看"
                      },
                      status=200)

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
                          'size': 250.41,
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'algorithm_id': "ALGO001",
                      }],
                      status=200)
        train_task = TrainTask(results_id="FILE123", algorithm_id="ALGO123")
        owner = ["USER1", "USER2", "USER13"]
        res = train_task.transform_model(
            "file_path", "name", "description", True, ResourceVisibility.PRIVATE, owner, 1)
        self.assertIsInstance(res, Model)
        self.assertEqual(res.id, "MODE001")
        self.assertEqual(res.state, ResourceState.READY)

    @responses.activate
    def test_transform_model_error(self):
        responses.add(responses.POST,
                      url=self._url("model/transform"),
                      match_querystring=True,
                      json={
                          "data": "MODE001",
                          "message": "模型转存工作正在进行，请稍后查看"
                      },
                      status=200)

        responses.add(responses.GET, url=self._url("model/query?id=MODE001"),
                      match_querystring=True, json=[{
                          'id': "MODE001",
                          'name': "TestModel1",
                          'description': "test",
                          'state': ResourceState.ERROR,
                          'visibility': ResourceVisibility.PUBLIC,
                          'upload_time': "2020-01-01 00:00",
                          'filename': "test.tar.gz",
                          'is_zipfile': 1,
                          'file': "USER001/models/MODE001/test.tar.gz",
                          'size': 250.41,
                          'creator_id': "USER001",
                          'node_id': "NODE001",
                          'owner': ["USER001"],
                          'algorithm_id': "ALGO001",
                      }],
                      status=200)
        train_task = TrainTask(results_id="FILE123", algorithm_id="ALGO123")
        with self.assertRaises(AnyLearnException) as ctx:
            owner = ["USER1", "USER2", "USER13"]
            res = train_task.transform_model(
                "file_path", "name", "description", True, ResourceVisibility.PRIVATE, owner, 1)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "Error occured when transforming model")

    def test_transform_model_empty_results_id_algorithm_id(self):
        train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            owner = ["USER1", "USER2", "USER13"]
            train_task.transform_model(
                "file_path", "name", "description", True, ResourceVisibility.PRIVATE, owner, 1)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(
            e.msg, "TrainTask缺少必要字段：['results_id', 'algorithm_id']")

    @responses.activate
    def test_transform_model_unknown_response(self):
        responses.add(responses.POST,
                      url=self._url("model/transform"),
                      match_querystring=True,
                      json=[{'msg': "Unknown response"}],
                      status=204)
        train_task = TrainTask(results_id="FILE123", algorithm_id="ALGO123")
        with self.assertRaises(AnyLearnException) as ctx:
            owner = ["USER1", "USER2", "USER13"]
            train_task.transform_model(
                "file_path", "name", "description", True, ResourceVisibility.PRIVATE, owner, 1)
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    def test_get_train_profile_ok(self):
        test_train_task = TrainTask(id="TRAI_test_get_train_profile",
                                    state=2,
                                    secret_key="test_key",
                                    project_id="test_project_id",)
        DB().create_or_update_train_task(train_task=test_train_task)
        train_profile = TrainProfile(id=uuid.uuid1().__str__(),
                                     train_task_id=test_train_task.id,
                                     entrypoint="algo.entrypoint_training",
                                     algorithm_id="algo.id",
                                     dataset_id="dset.id",
                                     train_params="train_task.train_params",
                                     algorithm_dir="algorithm_dir",
                                     algorithm_archive="algorithm_archive",
                                     dataset_dir="dataset_dir",
                                     dataset_archive="dataset_archive",)
        train_profile.create_in_db()
        res = test_train_task.get_train_profile()
        if res:
            self.assertIsInstance(res, TrainProfile)
            self.assertEqual("TRAI_test_get_train_profile", res.train_task_id)

    def test_get_train_profile_id_not_found(self):
        test_train_task = TrainTask(id="abcdefg~^%*#@")
        with self.assertRaises(AnyLearnException) as ctx:
            test_train_task.get_train_profile()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, f"资源{test_train_task.id}未找到")

    def test_transform_model_empty_id(self):
        test_train_task = TrainTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            test_train_task.get_train_profile()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(
            e.msg, "TrainTask缺少必要字段：['id']")
