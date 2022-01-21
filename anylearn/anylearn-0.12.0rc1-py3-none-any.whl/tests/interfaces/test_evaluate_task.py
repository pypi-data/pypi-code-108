import json
from requests.exceptions import RequestException
import responses
from urllib.parse import urlencode

from anylearn.interfaces.evaluate_task import (
    EvaluateSubTask,
    EvaluateTask,
    EvaluateTaskState,
    EvaluateTaskVisibility
)
from anylearn.utils.errors import (
    AnyLearnException,
    AnyLearnMissingParamException
)
from tests.base_test_case import BaseTestCase

class TestEvaluateTask(BaseTestCase):
    @responses.activate
    def test_list_evaluate_task_ok(self):
        responses.add(responses.GET, url=self._url("evaluate_task/list"),
                      json=[
                          {
                              'id': "EVAL001",
                              'name': "TestEvalTask1",
                              'description': "test",
                              'state': EvaluateTaskState.SUCCESS,
                              'visibility': EvaluateTaskVisibility.PUBLIC,
                              'creator_id': "USER001",
                              'owner': ["USER001"],
                              'create_time': "2020-04-01 00:00",
                              'finish_time': "2020-04-02 00:00",
                              'secret_key': "SECRET",
                          },
                          {
                              'id': "EVAL002",
                              'name': "TestEvalTask2",
                              'description': "test",
                              'state': EvaluateTaskState.RUNNING,
                              'visibility': EvaluateTaskVisibility.PRIVATE,
                              'creator_id': "USER002",
                              'owner': ["USER002"],
                              'create_time': "2020-04-03 00:00",
                              'finish_time': "",
                              'secret_key': "SECRET",
                          },
                      ],
                      status=200)
        evals = EvaluateTask.get_list()
        self.assertIsInstance(evals, list)
        self.assertEqual(len(evals), 2)
        self.assertIsInstance(evals[0], EvaluateTask)
        self.assertIsInstance(evals[1], EvaluateTask)
        self.assertEqual(evals[0].id, "EVAL001")
        self.assertEqual(evals[1].id, "EVAL002")

    @responses.activate
    def test_list_evaluate_task_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("evaluate_task/list"),
                      json={'msg': "Unknown response"},
                      status=200)
        with self.assertRaises(AnyLearnException) as ctx:
            EvaluateTask.get_list()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_evaluate_task_detail_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("evaluate_task/query?id=EVAL001"),
                      match_querystring=True, json={
                          'id': "EVAL001",
                          'name': "TestEvaluateTask1",
                          'description': "test",
                          'state': EvaluateTaskState.RUNNING,
                          'visibility': 3,
                          'creator_id': "USER001",
                          'owner': ["USER001"],
                          'create_time': "2021-04-01 23:59:59",
                          'finish_time': "",
                          'params_list': '[{"model_id": "MODE001", "files": "DSET001", "evaluate_params": {"dataset": "$DSET001", "model_path": "$MODE001"}}]',
                          'secret_key': "SECRET",
                          'results': [
                              {
                                  'args': '{"dataset": "$DSET001", "model_path": "$MODE001"}',
                                  'envs': "",
                                  'files': "DSET001",
                                  'gpu_num': 2,
                                  'id': "EVRE001",
                                  'model_id': "MODE001",
                                  'results': "",
                              }
                          ],
                      },
                      status=200)
        eval_task = EvaluateTask(id="EVAL001")
        eval_task.get_detail()
        self.assertEqual(eval_task.name, "TestEvaluateTask1")
        self.assertEqual(eval_task.description, "test")
        self.assertEqual(eval_task.state, EvaluateTaskState.RUNNING)
        self.assertEqual(eval_task.visibility, EvaluateTaskVisibility.PUBLIC)
        self.assertEqual(eval_task.creator_id, "USER001")
        self.assertIsInstance(eval_task.owner, list)
        self.assertEqual(eval_task.create_time, "2021-04-01 23:59:59")
        self.assertEqual(eval_task.secret_key, "SECRET")
        self.assertIsInstance(eval_task.sub_tasks, list)
        if isinstance(eval_task.sub_tasks, list):
            self.assertEqual(len(eval_task.sub_tasks), 1)
        self.assertEqual(eval_task.sub_tasks[0].id, "EVRE001")
        self.assertEqual(eval_task.sub_tasks[0].model_id, "MODE001")
        self.assertEqual(eval_task.sub_tasks[0].evaluate_params['dataset'], "$DSET001")
        self.assertEqual(eval_task.sub_tasks[0].evaluate_params['model_path'], "$MODE001")
        self.assertEqual(eval_task.sub_tasks[0].files[0], "DSET001")
        self.assertFalse(eval_task.sub_tasks[0].envs)
        self.assertEqual(eval_task.sub_tasks[0].gpu_num, 2)
        self.assertFalse(eval_task.sub_tasks[0].results)

    @responses.activate
    def test_get_evaluate_task_detail_no_explicit_call_ok(self):
        responses.add(responses.GET, url=self._url("evaluate_task/query?id=EVAL002"),
                      match_querystring=True, json={
                          'id': "EVAL002",
                          'name': "TestEvaluateTask2",
                          'description': "test",
                          'state': EvaluateTaskState.RUNNING,
                          'visibility': 3,
                          'creator_id': "USER002",
                          'owner': ["USER002"],
                          'create_time': "2021-04-02 23:59:59",
                          'finish_time': "",
                          'params_list': '[{"model_id": "MODE002", "files": "DSET002", "evaluate_params": {"dataset": "$DSET002", "model_path": "$MODE002"}}]',
                          'secret_key': "SECRET",
                          'results': [
                              {
                                  'args': '{"dataset": "$DSET002", "model_path": "$MODE002"}',
                                  'envs': "",
                                  'files': "DSET002",
                                  'gpu_num': 1,
                                  'id': "EVRE002",
                                  'model_id': "MODE002",
                                  'results': "",
                              }
                          ],
                      },
                      status=200)
        eval_task = EvaluateTask(id="EVAL002", load_detail=True)
        self.assertEqual(eval_task.name, "TestEvaluateTask2")
        self.assertEqual(eval_task.description, "test")
        self.assertEqual(eval_task.state, EvaluateTaskState.RUNNING)
        self.assertEqual(eval_task.visibility, EvaluateTaskVisibility.PUBLIC)
        self.assertEqual(eval_task.creator_id, "USER002")
        self.assertIsInstance(eval_task.owner, list)
        self.assertEqual(eval_task.create_time, "2021-04-02 23:59:59")
        self.assertEqual(eval_task.secret_key, "SECRET")
        self.assertIsInstance(eval_task.sub_tasks, list)
        if isinstance(eval_task.sub_tasks, list):
            self.assertEqual(len(eval_task.sub_tasks), 1)
        self.assertEqual(eval_task.sub_tasks[0].id, "EVRE002")
        self.assertEqual(eval_task.sub_tasks[0].model_id, "MODE002")
        self.assertEqual(eval_task.sub_tasks[0].evaluate_params['dataset'], "$DSET002")
        self.assertEqual(eval_task.sub_tasks[0].evaluate_params['model_path'], "$MODE002")
        self.assertEqual(eval_task.sub_tasks[0].files[0], "DSET002")
        self.assertFalse(eval_task.sub_tasks[0].envs)
        self.assertEqual(eval_task.sub_tasks[0].gpu_num, 1)
        self.assertFalse(eval_task.sub_tasks[0].results)

    @responses.activate
    def test_get_evaluate_task_detail_ko_403(self):
        responses.add(responses.GET, url=self._url("evaluate_task/query?id=EVAL403"),
                      match_querystring=True, status=403)
        evaluate_task = EvaluateTask(id="EVAL403")
        with self.assertRaises(RequestException) as ctx:
            evaluate_task.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, RequestException)
        self.assertEqual(e.response.status_code, 403)

    @responses.activate
    def test_get_evaluate_task_detail_ko_unknown_response(self):
        responses.add(responses.GET, url=self._url("evaluate_task/query?id=EVAL250"),
                      match_querystring=True, json=[{'msg': "Unknown response"}],
                      status=200)
        evaluate_task = EvaluateTask(id="EVAL250")
        with self.assertRaises(AnyLearnException) as ctx:
            evaluate_task.get_detail()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_create_evaluate_task_ok(self):
        responses.add(responses.POST, url=self._url("evaluate_task/add"),
                      json={'data': "EVAL001", 'message': "服务添加成功"},
                      status=200)
        evaluate_task = EvaluateTask(name="TestEvalTask001",
                                     sub_tasks=[
                                         EvaluateSubTask(
                                             model_id="MODE001",
                                             evaluate_params={
                                                 'dataset': "$DSET001",
                                                 'pre_train': "$MODE002",
                                                 'model_path': "$MODE001",
                                             },
                                             files=["DSET001", "MODE002"])
                                     ])
        result = evaluate_task.save()
        self.assertTrue(result)
        self.assertEqual(evaluate_task.id, "EVAL001")
        self.assertEqual(evaluate_task.params_list, '[{"id": null, "model_id": "MODE001", "files": "DSET001,MODE002", "evaluate_params": {"dataset": "$DSET001", "pre_train": "$MODE002", "model_path": "$MODE001"}, "envs": "", "gpu_num": 1, "results": null}]')

    def test_create_evaluate_task_ko_empty_name_subtasks(self):
        evaluate_task = EvaluateTask()
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            evaluate_task.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "EvaluateTask缺少必要字段：['name', 'sub_tasks']")

    def test_create_evaluate_task_ko_empty_subtaskmodelid(self):
        evaluate_task = EvaluateTask(name="TestEvalTask",
                                     sub_tasks=[
                                         EvaluateSubTask(
                                             evaluate_params={
                                                 'dataset': "$DSET001",
                                                 'pre_train': "$MODE002",
                                             },
                                             files=["DSET001", "MODE002"])
                                     ])
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            evaluate_task.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "EvaluateSubTask缺少必要字段：model_id")

    @responses.activate
    def test_create_evaluate_task_ko_unknown_response(self):
        responses.add(responses.POST, url=self._url("evaluate_task/add"),
                      json={'msg': "Unknown response"}, status=201)
        evaluate_task = EvaluateTask(name="TestEvalTask250",
                                     sub_tasks=[
                                         EvaluateSubTask(
                                             model_id="MODE250",
                                             evaluate_params={
                                                 'dataset': "$DSET001",
                                             },
                                             files=["DSET001"])
                                     ])
        with self.assertRaises(AnyLearnException) as ctx:
            evaluate_task.save()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_delete_evaluate_task_ok(self):
        responses.add(responses.DELETE,
                      url=self._url("evaluate_task/delete?id=EVAL001&force=0"),
                      match_querystring=True,
                      json={'data': "EVAL001", 'message': "任务删除成功"},
                      status=200)
        evaluate_task = EvaluateTask(id="EVAL001")
        result = evaluate_task.delete()
        self.assertTrue(result)

    @responses.activate
    def test_delete_evaluate_task_ko_unknown_response(self):
        responses.add(responses.DELETE,
                      url=self._url("evaluate_task/delete?id=EVAL250&force=0"),
                      match_querystring=True,
                      json={'msg': "Unknown response"},
                      status=204)
        evaluate_task = EvaluateTask(id="EVAL250")
        with self.assertRaises(AnyLearnException) as ctx:
            evaluate_task.delete()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")

    @responses.activate
    def test_get_evaluate_task_log_ok(self):
        query_str = urlencode({
            'id': "EVAL001",
            'limit': 100,
            'direction': "init",
            'index': 0,
            'self': 1,
        })
        responses.add(responses.GET,
                      url=self._url(f"evaluate_task/log?{query_str}"),
                      match_querystring=True,
                      json={
                          'EVRE001': [
                            {'offset': 1, 'text': "log1"},
                            {'offset': 2, 'text': "log2"},
                            {'offset': 3, 'text': "log3"},
                          ],
                          'EVRE002': [
                            {'offset': 4, 'text': "log4"},
                            {'offset': 5, 'text': "log5"},
                          ],
                      },
                      status=200)
        evaluate_task = EvaluateTask(id="EVAL001")
        result = evaluate_task.get_log(includes=True)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertIn('EVRE001', result)
        self.assertIn('EVRE002', result)
        self.assertIsInstance(result['EVRE001'], list)
        self.assertIsInstance(result['EVRE002'], list)
        self.assertEqual(len(result['EVRE001']), 3)
        self.assertEqual(len(result['EVRE002']), 2)
        self.assertIn('text', result['EVRE001'][0])
        self.assertIn('text', result['EVRE001'][1])
        self.assertIn('text', result['EVRE001'][2])
        self.assertIn('text', result['EVRE002'][0])
        self.assertIn('text', result['EVRE002'][1])

    def test_get_evaluate_task_log_ko_empty_id(self):
        evaluate_task = EvaluateTask(name="TestEvalTask")
        with self.assertRaises(AnyLearnMissingParamException) as ctx:
            evaluate_task.get_log()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnMissingParamException)
        self.assertEqual(e.msg, "EvaluateTask缺少必要字段：['id']")

    @responses.activate
    def test_get_evaluate_task_log_ko_unknown_response(self):
        query_str = urlencode({
            'id': "EVAL250",
            'limit': 100,
            'direction': "init",
            'index': 0,
            'self': 0,
        })
        responses.add(responses.GET,
                      url=self._url(f"evaluate_task/log?{query_str}"),
                      match_querystring=True,
                      json="",
                      status=204)
        evaluate_task = EvaluateTask(id="EVAL250")
        with self.assertRaises(AnyLearnException) as ctx:
            evaluate_task.get_log()
        e = ctx.exception
        self.assertIsInstance(e, AnyLearnException)
        self.assertEqual(e.msg, "请求未能得到有效响应")
